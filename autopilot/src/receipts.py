import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def _receipts_dir() -> Path:
    return Path(
        os.getenv(
            "RECEIPTS_DIR",
            str(Path(__file__).resolve().parents[1] / ".." / "receipts"),
        )
    )


def build_receipt(
    run_id: str,
    workflow_name: str,
    status: str,
    started_at: datetime,
    ended_at: datetime,
    inputs: dict[str, Any],
    decisions: dict[str, Any],
    actions: list[dict[str, Any]],
    results: list[dict[str, Any]],
    metrics: dict[str, Any],
    replay_of: str | None = None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "workflow_name": workflow_name,
        "status": status,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "inputs": inputs,
        "decisions": decisions,
        "actions": actions,
        "results": results,
        "metrics": metrics,
        "replay_of": replay_of,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_receipt(receipt: dict[str, Any]) -> Path:
    receipts_dir = _receipts_dir()
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / f"{receipt['run_id']}.json"
    path.write_text(json.dumps(receipt, indent=2, default=str))
    return path
