import importlib.util

import pytest

if importlib.util.find_spec("jsonschema") is None:
    pytest.skip("jsonschema not installed", allow_module_level=True)

from autopilot.src.schemas import validate_event


def test_validate_event_schema():
    valid_event = {
        "id": "evt_1",
        "type": "ProductViewed",
        "source": "unit",
        "subject": "sku_1",
        "time": "2024-01-01T00:00:00Z",
        "specversion": "1.0",
        "data": {"user_id": "user_1"},
    }
    validate_event(valid_event)

    invalid_event = {
        "id": "evt_2",
        "source": "unit",
        "subject": "sku_1",
        "time": "2024-01-01T00:00:00Z",
        "data": {},
    }
    with pytest.raises(Exception):
        validate_event(invalid_event)
