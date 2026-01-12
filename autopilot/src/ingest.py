import uuid
from datetime import datetime, timezone

from autopilot.src import db
from autopilot.src.schemas import validate_event


def build_event(event_type: str, subject: str, data: dict) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "source": "autopilot.simulator",
        "subject": subject,
        "time": datetime.now(timezone.utc).isoformat(),
        "specversion": "1.0",
        "data": data,
    }


def simulate_events(database_url: str) -> list[dict]:
    events = [
        build_event("ProductViewed", "sku_001", {"user_id": "user_1"}),
        build_event("AddToCart", "sku_001", {"user_id": "user_1"}),
        build_event("CheckoutStarted", "sku_001", {"user_id": "user_1"}),
        build_event("OrderPaid", "sku_001", {"user_id": "user_1", "total": 59.0}),
        build_event("RefundIssued", "sku_002", {"user_id": "user_2", "total": 15.0}),
        build_event("AdImpression", "cmp_001", {"campaign_id": "cmp_001"}),
        build_event("AdClick", "cmp_001", {"campaign_id": "cmp_001"}),
        build_event("EmailSent", "user_1", {"campaign_id": "camp_01"}),
        build_event("EmailClicked", "user_1", {"campaign_id": "camp_01"}),
        build_event("TicketOpened", "user_2", {"reason": "refund"}),
    ]
    for event in events:
        validate_event(event)
        db.insert_event(database_url, event)
    return events
