import importlib.util

import pytest

if importlib.util.find_spec("psycopg") is None:
    pytest.skip("psycopg not installed", allow_module_level=True)

from autopilot.src.workflow_engine import run_step


def test_workflow_dead_letter(database_url):
    def _fail():
        raise RuntimeError("boom")

    result = run_step(database_url, "run_1", "failing_step", _fail, max_attempts=2)
    assert result.status == "failed"
