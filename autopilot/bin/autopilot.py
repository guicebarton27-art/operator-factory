#!/usr/bin/env python3
import argparse
import json

from autopilot.src import db, ingest
from autopilot.src.config import load_config
from autopilot.src.reporting import write_reports
from autopilot.src.runner import run_daily


def cmd_ingest() -> None:
    config = load_config()
    events = ingest.simulate_events(config.database_url)
    print(json.dumps({"ingested": len(events)}))


def cmd_run(replay_of: str | None = None) -> None:
    config = load_config()
    result = run_daily(config, replay_of=replay_of)
    print(json.dumps(result, default=str))


def cmd_replay(run_id: str) -> None:
    config = load_config()
    workflow_name = db.get_workflow_name(config.database_url, run_id)
    if not workflow_name:
        raise SystemExit(f"Unknown run_id {run_id}")
    result = run_daily(config, replay_of=run_id)
    print(json.dumps(result, default=str))


def cmd_status() -> None:
    config = load_config()
    runs = db.list_runs(config.database_url)
    dead_letters = db.list_dead_letters(config.database_url)
    print(json.dumps({"runs": runs, "dead_letters": dead_letters}, default=str, indent=2))


def cmd_report_missing() -> None:
    write_reports()
    print("Reports updated")


def main() -> None:
    parser = argparse.ArgumentParser(prog="autopilot")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ingest")
    sub.add_parser("run")
    replay = sub.add_parser("replay")
    replay.add_argument("--run-id", required=True)
    sub.add_parser("status")
    sub.add_parser("report-missing")

    args = parser.parse_args()
    if args.command == "ingest":
        cmd_ingest()
    elif args.command == "run":
        cmd_run()
    elif args.command == "replay":
        cmd_replay(args.run_id)
    elif args.command == "status":
        cmd_status()
    elif args.command == "report-missing":
        cmd_report_missing()


if __name__ == "__main__":
    main()
