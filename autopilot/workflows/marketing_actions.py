from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from autopilot.adapters.ads import AdsAdapter
from autopilot.adapters.messaging import MessagingAdapter
from autopilot.src import db
from autopilot.src.config import AutopilotConfig
from autopilot.src.idempotency import execute_once
from autopilot.src.logging import get_logger

logger = get_logger("autopilot.marketing_actions")


def _build_user_interest(events: list[dict[str, Any]]) -> dict[str, list[str]]:
    interests: dict[str, list[str]] = defaultdict(list)
    for event in events:
        user_id = event.get("data", {}).get("user_id")
        if not user_id:
            continue
        if event["type"] in {"ProductViewed", "AddToCart"}:
            interests[user_id].append(event["subject"])
    return interests


def _can_send_email(config: AutopilotConfig, user_id: str) -> bool:
    now = datetime.now(timezone.utc)
    daily_count = db.count_events(
        config.database_url, "EmailSent", user_id, now - timedelta(days=1)
    )
    weekly_count = db.count_events(
        config.database_url, "EmailSent", user_id, now - timedelta(days=7)
    )
    return (
        daily_count < config.email_frequency_cap_daily
        and weekly_count < config.email_frequency_cap_weekly
    )


def run(config: AutopilotConfig, recommendations: list[dict[str, Any]]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    events = db.fetch_events(config.database_url)
    interest = _build_user_interest(events)

    messaging_adapter = MessagingAdapter(dry_run=config.dry_run)
    ads_adapter = AdsAdapter(dry_run=config.dry_run, enable_write=config.enable_ads_write)

    if recommendations:
        top = recommendations[0]
        for user_id, products in interest.items():
            if top["product_id"] not in products:
                continue
            if not _can_send_email(config, user_id):
                actions.append(
                    {
                        "action": "send_email",
                        "status": "blocked",
                        "reason": "frequency_cap",
                        "user_id": user_id,
                    }
                )
                continue
            payload = {
                "user_id": user_id,
                "subject": f"Top pick: {top['product_id']}",
                "body": "Based on your interest, this product is trending.",
            }

            def _send():
                response = messaging_adapter.send_email(**payload)
                return {
                    "adapter_status": response.status,
                    "payload": response.payload,
                }

            result = execute_once(config.database_url, "send_email", payload, _send)
            actions.append({"action": "send_email", **payload, "idempotency_key": result["idempotency_key"]})
            results.append(result)

    ads_metrics = ads_adapter.get_metrics().payload
    campaign = ads_metrics["campaigns"][0]
    current_budget = config.daily_budget_cap
    proposed_budget = max(current_budget * 0.9, 0)
    change_pct = abs((proposed_budget - current_budget) / current_budget * 100)

    if change_pct > config.budget_change_limit_pct:
        actions.append(
            {
                "action": "set_budget",
                "campaign_id": campaign["campaign_id"],
                "status": "blocked",
                "reason": "budget_change_limit",
                "proposed_budget": proposed_budget,
            }
        )
    else:
        payload = {"campaign_id": campaign["campaign_id"], "new_budget": proposed_budget}

        def _set_budget():
            response = ads_adapter.set_budget(**payload)
            return {"adapter_status": response.status, "payload": response.payload}

        result = execute_once(config.database_url, "set_budget", payload, _set_budget)
        actions.append(
            {
                "action": "set_budget",
                "campaign_id": campaign["campaign_id"],
                "new_budget": proposed_budget,
                "idempotency_key": result["idempotency_key"],
            }
        )
        results.append(result)

    return {"actions": actions, "results": results}
