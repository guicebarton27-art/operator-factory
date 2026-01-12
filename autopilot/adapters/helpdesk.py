from autopilot.adapters.base import AdapterResponse, BaseAdapter


class HelpdeskAdapter(BaseAdapter):
    def list_tickets(self) -> AdapterResponse:
        payload = {"tickets": [{"ticket_id": "tkt_001", "reason": "refund"}]}
        return AdapterResponse(status="ok", payload=payload)

    def tag_ticket(self, ticket_id: str, tag: str) -> AdapterResponse:
        payload = {"ticket_id": ticket_id, "tag": tag}
        if self.dry_run:
            return AdapterResponse(status="dry_run", payload=payload)
        return AdapterResponse(status="tagged", payload=payload)
