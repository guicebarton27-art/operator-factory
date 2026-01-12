# Missing Information Report

This document records gaps, risks, defaults, and upgrade paths.

| Category | Gap | Risk | Safe Default | Upgrade Path |
| --- | --- | --- | --- | --- |
| Business Model | Physical vs digital fulfillment specifics | Incorrect margin/stock logic | Assume physical DTC with conservative margins | Update assumptions and scoring weights |
| Data | Event source of truth | Data drift | Use simulated events for v1 | Integrate event source adapter |
| Marketing | Channel provider selection | Misaligned API usage | Use adapters with dry-run only | Implement provider adapters |
| Governance | Approval thresholds | Overspending | Block budget changes >10% | Configure approval service |
| Tooling | MCP availability | Integration mismatch | Local mock adapters | Swap to MCP adapters |
