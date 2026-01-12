# Business Autopilot

A durable, vendor-resilient autopilot for product analytics and marketing automation.

## Quickstart
```bash
cp .env.example .env
make setup
./bin/autopilot ingest
./bin/autopilot run
./bin/autopilot status
```

## Architecture
See `docs/ARCHITECTURE.md` for the data/control/integration plane design.

## Commands
- `make doctor`: verify dependencies and required env vars.
- `make setup`: install deps and start Postgres.
- `make run`: run daily workflows once.
- `make test`: run unit and integration tests.

CLI:
- `./bin/autopilot ingest`
- `./bin/autopilot run`
- `./bin/autopilot replay --run-id <id>`
- `./bin/autopilot status`
- `./bin/autopilot report-missing`

## Safety Model
- Dry-run mode by default (`DRY_RUN=true`).
- Ads write actions disabled unless `ENABLE_ADS_WRITE=true`.
- Budget changes capped by `BUDGET_CHANGE_LIMIT_PCT`.
- Email frequency caps via `EMAIL_FREQUENCY_CAP_DAILY` and `EMAIL_FREQUENCY_CAP_WEEKLY`.

## Docs
- `docs/MISSING_INFO.md`
- `docs/DECISIONS_NEEDED.md`
- `docs/INTEGRATIONS.md`
- `docs/REPLAY.md`
