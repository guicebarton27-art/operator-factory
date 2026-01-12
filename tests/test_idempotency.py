import importlib.util

import pytest

if importlib.util.find_spec("psycopg") is None:
    pytest.skip("psycopg not installed", allow_module_level=True)

from autopilot.src.idempotency import execute_once


def test_idempotency_exec(database_url):
    counter = {"value": 0}

    def _increment():
        counter["value"] += 1
        return {"value": counter["value"]}

    payload = {"entity": "abc"}
    first = execute_once(database_url, "increment", payload, _increment)
    second = execute_once(database_url, "increment", payload, _increment)

    assert first["status"] == "completed"
    assert second["status"] == "skipped"
    assert counter["value"] == 1
