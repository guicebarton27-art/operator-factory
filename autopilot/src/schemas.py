import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "events.json"


def load_event_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_event(envelope: dict) -> None:
    schema = load_event_schema()
    Draft202012Validator(schema).validate(envelope)
