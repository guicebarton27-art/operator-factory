import hashlib
import json
from typing import Any

from autopilot.src import db


def make_idempotency_key(action: str, payload: dict[str, Any]) -> str:
    normalized = json.dumps(payload, sort_keys=True)
    digest = hashlib.sha256(f"{action}:{normalized}".encode("utf-8")).hexdigest()
    return f"{action}:{digest}"


def execute_once(database_url: str, action: str, payload: dict[str, Any], func):
    key = make_idempotency_key(action, payload)
    existing = db.check_idempotency(database_url, key)
    if existing:
        return {"status": "skipped", "idempotency_key": key, "result": existing["result"]}
    result = func()
    db.store_idempotency(database_url, key, action, "completed", result)
    return {"status": "completed", "idempotency_key": key, "result": result}
