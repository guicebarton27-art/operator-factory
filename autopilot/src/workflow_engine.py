import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from autopilot.src import db
from autopilot.src.logging import get_logger

logger = get_logger("autopilot.workflow")


@dataclass
class StepResult:
    name: str
    status: str
    attempts: int
    error: str | None
    output: dict[str, Any] | None = None


def run_step(
    database_url: str,
    run_id: str,
    step_name: str,
    func: Callable[[], dict[str, Any]],
    max_attempts: int = 3,
    backoff_seconds: float = 1.0,
    payload: dict[str, Any] | None = None,
) -> StepResult:
    attempts = 0
    last_error = None
    while attempts < max_attempts:
        attempts += 1
        try:
            output = func()
            db.update_step(database_url, run_id, step_name, "completed", attempts, None)
            return StepResult(step_name, "completed", attempts, None, output)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            db.update_step(database_url, run_id, step_name, "retrying", attempts, last_error)
            logger.error("step_failed", extra={"step": step_name, "error": last_error})
            if attempts < max_attempts:
                time.sleep(backoff_seconds * attempts)
    db.update_step(database_url, run_id, step_name, "failed", attempts, last_error)
    db.record_dead_letter(
        database_url,
        run_id,
        step_name,
        last_error or "unknown error",
        payload=payload,
    )
    return StepResult(step_name, "failed", attempts, last_error)


def start_run(database_url: str, run_id: str, workflow_name: str, replay_of: str | None) -> datetime:
    started_at = datetime.now(timezone.utc)
    db.upsert_workflow_run(database_url, run_id, workflow_name, "running", started_at, None, replay_of)
    return started_at


def finish_run(
    database_url: str,
    run_id: str,
    workflow_name: str,
    status: str,
    started_at: datetime,
) -> datetime:
    ended_at = datetime.now(timezone.utc)
    db.upsert_workflow_run(database_url, run_id, workflow_name, status, started_at, ended_at)
    return ended_at
