from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AdapterResponse:
    status: str
    payload: dict[str, Any]


class AdapterError(Exception):
    pass


class BaseAdapter:
    def __init__(self, dry_run: bool = True) -> None:
        self.dry_run = dry_run
