from typing import Any

from autopilot.adapters.base import AdapterResponse, BaseAdapter


class MessagingAdapter(BaseAdapter):
    def send_email(self, user_id: str, subject: str, body: str) -> AdapterResponse:
        payload = {"user_id": user_id, "subject": subject, "body": body}
        if self.dry_run:
            return AdapterResponse(status="dry_run", payload=payload)
        return AdapterResponse(status="sent", payload=payload)

    def create_segment(self, name: str, criteria: dict[str, Any]) -> AdapterResponse:
        payload = {"name": name, "criteria": criteria}
        if self.dry_run:
            return AdapterResponse(status="dry_run", payload=payload)
        return AdapterResponse(status="created", payload=payload)
