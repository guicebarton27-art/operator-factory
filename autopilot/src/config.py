import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AutopilotConfig:
    env: str
    database_url: str
    dry_run: bool
    enable_ads_write: bool
    daily_budget_cap: float
    budget_change_limit_pct: float
    email_frequency_cap_daily: int
    email_frequency_cap_weekly: int
    compliance_blocked_categories: tuple[str, ...]


DEFAULTS = {
    "AUTOPILOT_ENV": "development",
    "DRY_RUN": "true",
    "ENABLE_ADS_WRITE": "false",
    "DAILY_BUDGET_CAP": "50",
    "BUDGET_CHANGE_LIMIT_PCT": "10",
    "EMAIL_FREQUENCY_CAP_DAILY": "1",
    "EMAIL_FREQUENCY_CAP_WEEKLY": "3",
    "COMPLIANCE_BLOCKED_CATEGORIES": "health,finance",
}


def _get_env(name: str) -> str:
    return os.getenv(name, DEFAULTS.get(name, ""))


def load_config() -> AutopilotConfig:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set")
    return AutopilotConfig(
        env=_get_env("AUTOPILOT_ENV"),
        database_url=database_url,
        dry_run=_get_env("DRY_RUN").lower() == "true",
        enable_ads_write=_get_env("ENABLE_ADS_WRITE").lower() == "true",
        daily_budget_cap=float(_get_env("DAILY_BUDGET_CAP")),
        budget_change_limit_pct=float(_get_env("BUDGET_CHANGE_LIMIT_PCT")),
        email_frequency_cap_daily=int(_get_env("EMAIL_FREQUENCY_CAP_DAILY")),
        email_frequency_cap_weekly=int(_get_env("EMAIL_FREQUENCY_CAP_WEEKLY")),
        compliance_blocked_categories=tuple(
            item.strip()
            for item in _get_env("COMPLIANCE_BLOCKED_CATEGORIES").split(",")
            if item.strip()
        ),
    )
