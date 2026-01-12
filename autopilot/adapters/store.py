from typing import Any

from autopilot.adapters.base import AdapterResponse, BaseAdapter


class StoreAdapter(BaseAdapter):
    def list_products(self) -> AdapterResponse:
        payload = {
            "products": [
                {"product_id": "sku_001", "name": "Widget", "margin": 0.4},
                {"product_id": "sku_002", "name": "Gizmo", "margin": 0.3},
            ]
        }
        return AdapterResponse(status="ok", payload=payload)

    def list_orders(self) -> AdapterResponse:
        payload = {
            "orders": [
                {"order_id": "ord_001", "product_id": "sku_001", "total": 59.0}
            ]
        }
        return AdapterResponse(status="ok", payload=payload)

    def get_order_costs(self, order_id: str) -> AdapterResponse:
        payload = {"order_id": order_id, "cost": 30.0}
        return AdapterResponse(status="ok", payload=payload)
