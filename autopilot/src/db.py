from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterable

import psycopg
from psycopg.types.json import Jsonb

from autopilot.src.logging import get_logger

logger = get_logger("autopilot.db")


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        source TEXT NOT NULL,
        subject TEXT NOT NULL,
        time TIMESTAMPTZ NOT NULL,
        envelope JSONB NOT NULL,
        received_at TIMESTAMPTZ NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_runs (
        run_id TEXT PRIMARY KEY,
        workflow_name TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TIMESTAMPTZ NOT NULL,
        ended_at TIMESTAMPTZ,
        replay_of TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_steps (
        run_id TEXT NOT NULL,
        step_name TEXT NOT NULL,
        status TEXT NOT NULL,
        attempts INT NOT NULL,
        last_error TEXT,
        updated_at TIMESTAMPTZ NOT NULL,
        PRIMARY KEY (run_id, step_name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS idempotency_keys (
        key TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        status TEXT NOT NULL,
        result JSONB,
        created_at TIMESTAMPTZ NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS dead_letter (
        id SERIAL PRIMARY KEY,
        run_id TEXT NOT NULL,
        step_name TEXT NOT NULL,
        error TEXT NOT NULL,
        payload JSONB,
        created_at TIMESTAMPTZ NOT NULL
    );
    """,
]


@contextmanager
def get_connection(database_url: str):
    conn = psycopg.connect(database_url)
    try:
        yield conn
    finally:
        conn.close()


def init_db(database_url: str) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            for ddl in TABLES:
                cur.execute(ddl)
        conn.commit()
    logger.info("Database initialized")


def insert_event(database_url: str, envelope: dict[str, Any]) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO events (id, type, source, subject, time, envelope, received_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (
                    envelope["id"],
                    envelope["type"],
                    envelope["source"],
                    envelope["subject"],
                    envelope["time"],
                    Jsonb(envelope),
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()


def fetch_events(database_url: str) -> list[dict[str, Any]]:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT envelope FROM events ORDER BY time ASC")
            rows = cur.fetchall()
    return [row[0] for row in rows]


def count_events(
    database_url: str,
    event_type: str,
    user_id: str,
    since: datetime,
) -> int:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM events
                WHERE type = %s
                  AND envelope->'data'->>'user_id' = %s
                  AND time >= %s
                """,
                (event_type, user_id, since),
            )
            row = cur.fetchone()
    return int(row[0]) if row else 0


def upsert_workflow_run(
    database_url: str,
    run_id: str,
    workflow_name: str,
    status: str,
    started_at: datetime,
    ended_at: datetime | None = None,
    replay_of: str | None = None,
) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workflow_runs (run_id, workflow_name, status, started_at, ended_at, replay_of)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    ended_at = EXCLUDED.ended_at
                """,
                (run_id, workflow_name, status, started_at, ended_at, replay_of),
            )
        conn.commit()


def update_step(
    database_url: str,
    run_id: str,
    step_name: str,
    status: str,
    attempts: int,
    last_error: str | None,
) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workflow_steps (run_id, step_name, status, attempts, last_error, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (run_id, step_name) DO UPDATE SET
                    status = EXCLUDED.status,
                    attempts = EXCLUDED.attempts,
                    last_error = EXCLUDED.last_error,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    run_id,
                    step_name,
                    status,
                    attempts,
                    last_error,
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()


def record_dead_letter(
    database_url: str,
    run_id: str,
    step_name: str,
    error: str,
    payload: dict[str, Any] | None = None,
) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO dead_letter (run_id, step_name, error, payload, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    step_name,
                    error,
                    Jsonb(payload) if payload else None,
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()


def list_dead_letters(database_url: str) -> list[dict[str, Any]]:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT run_id, step_name, error, payload, created_at FROM dead_letter ORDER BY created_at DESC LIMIT 20"
            )
            rows = cur.fetchall()
    return [
        {
            "run_id": row[0],
            "step_name": row[1],
            "error": row[2],
            "payload": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def list_runs(database_url: str) -> list[dict[str, Any]]:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT run_id, workflow_name, status, started_at, ended_at, replay_of FROM workflow_runs ORDER BY started_at DESC LIMIT 20"
            )
            rows = cur.fetchall()
    return [
        {
            "run_id": row[0],
            "workflow_name": row[1],
            "status": row[2],
            "started_at": row[3],
            "ended_at": row[4],
            "replay_of": row[5],
        }
        for row in rows
    ]


def get_workflow_name(database_url: str, run_id: str) -> str | None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT workflow_name FROM workflow_runs WHERE run_id = %s",
                (run_id,),
            )
            row = cur.fetchone()
    return row[0] if row else None


def check_idempotency(database_url: str, key: str) -> dict[str, Any] | None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT action, status, result FROM idempotency_keys WHERE key = %s",
                (key,),
            )
            row = cur.fetchone()
    if not row:
        return None
    return {"action": row[0], "status": row[1], "result": row[2]}


def store_idempotency(
    database_url: str, key: str, action: str, status: str, result: dict[str, Any]
) -> None:
    with get_connection(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO idempotency_keys (key, action, status, result, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    status = EXCLUDED.status,
                    result = EXCLUDED.result
                """,
                (
                    key,
                    action,
                    status,
                    Jsonb(result),
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["init"])
    parser.add_argument("--database-url", required=True)
    args = parser.parse_args()
    if args.action == "init":
        init_db(args.database_url)


if __name__ == "__main__":
    main()
