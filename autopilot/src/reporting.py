from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"

MISSING_INFO = """# Missing Information Report

This document records gaps, risks, defaults, and upgrade paths.

| Category | Gap | Risk | Safe Default | Upgrade Path |
| --- | --- | --- | --- | --- |
| Business Model | Physical vs digital fulfillment specifics | Incorrect margin/stock logic | Assume physical DTC with conservative margins | Update assumptions and scoring weights |
| Data | Event source of truth | Data drift | Use simulated events for v1 | Integrate event source adapter |
| Marketing | Channel provider selection | Misaligned API usage | Use adapters with dry-run only | Implement provider adapters |
| Governance | Approval thresholds | Overspending | Block budget changes >10% | Configure approval service |
| Tooling | MCP availability | Integration mismatch | Local mock adapters | Swap to MCP adapters |
"""

DECISIONS_NEEDED = """# Decisions Needed

Only high-risk, business-specific choices are listed.

1. Approval workflow for budget changes and compliance-sensitive messaging (who approves, SLA).
2. Target marketing channels and providers (e.g., Meta, Google, Klaviyo) to implement first.
"""

ASSUMPTIONS = """# Assumptions

- Business type defaults to DTC ecommerce with physical goods.
- Ads write actions are disabled unless ENABLE_ADS_WRITE=true.
- Budget cap defaults to $50/day with 10% max change without approval.
- Email frequency defaults to 1/day and 3/week per user.
- Compliance-sensitive categories (health, finance) are blocked by default.
- Attribution uses last-click UTMs for v1.
"""


def write_reports() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "MISSING_INFO.md").write_text(MISSING_INFO)
    (DOCS_DIR / "DECISIONS_NEEDED.md").write_text(DECISIONS_NEEDED)
    (ROOT / "ASSUMPTIONS.md").write_text(ASSUMPTIONS)
