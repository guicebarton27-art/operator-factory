# Architecture

## Data Plane
- Canonical CloudEvents-style envelope stored in Postgres `events` table.
- Event schema is defined in `autopilot/schemas/events.json`.

## Control Plane
- Durable workflow engine stores state in `workflow_runs`, `workflow_steps`, and `dead_letter`.
- Retries with exponential backoff and replay via `./bin/autopilot replay --run-id <id>`.

## Integration Layer
- Stable adapters in `autopilot/adapters`.
- Adapters support dry-run and idempotency keys (enforced in control plane).

## Agent Layer
- Planned for creative generation only; not allowed to directly execute actions.
