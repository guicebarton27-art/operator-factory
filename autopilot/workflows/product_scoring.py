from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from autopilot.adapters.ads import AdsAdapter
from autopilot.adapters.store import StoreAdapter
from autopilot.src import db
from autopilot.src.config import AutopilotConfig
from autopilot.src.logging import get_logger

logger = get_logger("autopilot.product_scoring")


def compute_scores(
    config: AutopilotConfig, events: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    traffic = defaultdict(int)
    orders = defaultdict(int)
    refunds = defaultdict(int)

    for event in events:
        subject = event["subject"]
        if event["type"] == "ProductViewed":
            traffic[subject] += 1
        if event["type"] == "OrderPaid":
            orders[subject] += 1
        if event["type"] == "RefundIssued":
            refunds[subject] += 1

    store_adapter = StoreAdapter(dry_run=config.dry_run)
    products = store_adapter.list_products().payload["products"]
    scores = []
    for product in products:
        product_id = product["product_id"]
        views = traffic[product_id]
        order_count = orders[product_id]
        refund_count = refunds[product_id]
        cvr = (order_count / views) if views else 0.0
        refund_rate = (refund_count / order_count) if order_count else 0.0
        refund_cost = 10.0
        stockout_risk = 0.0
        score = (views * cvr * product["margin"]) - (
            refund_rate * refund_cost
        ) - (stockout_risk * 5.0)
        scores.append(
            {
                "product_id": product_id,
                "score": round(score, 4),
                "views": views,
                "orders": order_count,
                "refunds": refund_count,
                "cvr": round(cvr, 4),
                "refund_rate": round(refund_rate, 4),
            }
        )
    scores.sort(key=lambda item: item["score"], reverse=True)

    ads_adapter = AdsAdapter(dry_run=config.dry_run, enable_write=config.enable_ads_write)
    ads_metrics = ads_adapter.get_metrics().payload
    spent_no_conversions = [
        campaign
        for campaign in ads_metrics["campaigns"]
        if campaign["spend"] > 0 and campaign["conversions"] == 0
    ]

    refund_spike = [
        item for item in scores if item["refund_rate"] > 0.2 and item["orders"] >= 2
    ]

    metrics = {
        "ads_metrics": ads_metrics,
        "alerts": {
            "spent_with_no_conversions": spent_no_conversions,
            "refund_spike": refund_spike,
        },
    }
    return scores, metrics


def run(config: AutopilotConfig) -> dict[str, Any]:
    events = db.fetch_events(config.database_url)
    recommendations, metrics = compute_scores(config, events)
    logger.info(
        "computed_scores",
        extra={"recommendations": recommendations, "alerts": metrics["alerts"]},
    )
    return {
        "recommendations": recommendations,
        "metrics": metrics,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
