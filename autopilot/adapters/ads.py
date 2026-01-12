from typing import Any

from autopilot.adapters.base import AdapterError, AdapterResponse, BaseAdapter


class AdsAdapter(BaseAdapter):
    def __init__(self, dry_run: bool = True, enable_write: bool = False) -> None:
        super().__init__(dry_run=dry_run)
        self.enable_write = enable_write

    def get_metrics(self) -> AdapterResponse:
        payload = {
            "campaigns": [
                {
                    "campaign_id": "cmp_001",
                    "spend": 120.0,
                    "clicks": 45,
                    "conversions": 0,
                }
            ]
        }
        return AdapterResponse(status="ok", payload=payload)

    def set_budget(self, campaign_id: str, new_budget: float) -> AdapterResponse:
        if not self.enable_write:
            return AdapterResponse(
                status="blocked",
                payload={"reason": "ads write disabled", "campaign_id": campaign_id},
            )
        if self.dry_run:
            return AdapterResponse(
                status="dry_run",
                payload={"campaign_id": campaign_id, "new_budget": new_budget},
            )
        if new_budget <= 0:
            raise AdapterError("Budget must be positive")
        return AdapterResponse(
            status="applied",
            payload={"campaign_id": campaign_id, "new_budget": new_budget},
        )

    def pause_campaign(self, campaign_id: str) -> AdapterResponse:
        if not self.enable_write:
            return AdapterResponse(
                status="blocked",
                payload={"reason": "ads write disabled", "campaign_id": campaign_id},
            )
        if self.dry_run:
            return AdapterResponse(status="dry_run", payload={"campaign_id": campaign_id})
        return AdapterResponse(status="paused", payload={"campaign_id": campaign_id})
