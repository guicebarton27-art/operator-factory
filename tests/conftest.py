import os
import sys
from pathlib import Path

import importlib.util

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

HAS_PSYCOPG = importlib.util.find_spec("psycopg") is not None


@pytest.fixture(scope="session")
def database_url():
    if not HAS_PSYCOPG:
        pytest.skip("psycopg not installed")
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set")
    return url


@pytest.fixture(autouse=True)
def init_db(database_url):
    from autopilot.src import db  # noqa: E402

    db.init_db(database_url)
    yield
    with db.get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM events")
            cur.execute("DELETE FROM workflow_steps")
            cur.execute("DELETE FROM workflow_runs")
            cur.execute("DELETE FROM idempotency_keys")
            cur.execute("DELETE FROM dead_letter")
        conn.commit()
