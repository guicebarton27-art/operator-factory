import uuid
from datetime import datetime
from typing import Any

from autopilot.src import db
from autopilot.src.config import AutopilotConfig
from autopilot.src.receipts import build_receipt, write_receipt
from autopilot.src.workflow_engine import finish_run, run_step, start_run
from autopilot.workflows import marketing_actions, product_scoring


def run_product_scoring(config: AutopilotConfig, replay_of: str | None = None) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    workflow_name = "ProductScoringDaily"
    started_at = start_run(config.database_url, run_id, workflow_name, replay_of)

    step = run_step(
        config.database_url,
        run_id,
        "compute_scores",
        lambda: product_scoring.run(config),
    )

    status = "completed" if step.status == "completed" else "failed"
    ended_at = finish_run(config.database_url, run_id, workflow_name, status, started_at)
    decisions = {"recommendations": step.output.get("recommendations", [])} if step.output else {}
    metrics = step.output.get("metrics", {}) if step.output else {}
    receipt = build_receipt(
        run_id=run_id,
        workflow_name=workflow_name,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        inputs={"config": config.__dict__},
        decisions=decisions,
        actions=[],
        results=[step.__dict__],
        metrics=metrics,
        replay_of=replay_of,
    )
    write_receipt(receipt)
    return {"run_id": run_id, "status": status, "output": step.output}


def run_marketing_actions(
    config: AutopilotConfig,
    recommendations: list[dict[str, Any]],
    replay_of: str | None = None,
) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    workflow_name = "MarketingActionsDaily"
    started_at = start_run(config.database_url, run_id, workflow_name, replay_of)

    step = run_step(
        config.database_url,
        run_id,
        "apply_actions",
        lambda: marketing_actions.run(config, recommendations),
        payload={"recommendations": recommendations},
    )

    status = "completed" if step.status == "completed" else "failed"
    ended_at = finish_run(config.database_url, run_id, workflow_name, status, started_at)
    actions = step.output.get("actions", []) if step.output else []
    results = step.output.get("results", []) if step.output else []
    receipt = build_receipt(
        run_id=run_id,
        workflow_name=workflow_name,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        inputs={"config": config.__dict__, "recommendations": recommendations},
        decisions={"selected": recommendations[:1]},
        actions=actions,
        results=results,
        metrics={},
        replay_of=replay_of,
    )
    write_receipt(receipt)
    return {"run_id": run_id, "status": status}


def run_daily(config: AutopilotConfig, replay_of: str | None = None) -> dict[str, Any]:
    scoring = run_product_scoring(config, replay_of=replay_of)
    recommendations = scoring["output"]["recommendations"] if scoring["output"] else []
    actions = run_marketing_actions(config, recommendations, replay_of=replay_of)
    return {"product_scoring": scoring, "marketing_actions": actions}
