# Replay a Failed Job

1. Inspect failures:
   ```bash
   ./bin/autopilot status
   ```
2. Replay a run:
   ```bash
   ./bin/autopilot replay --run-id <id>
   ```
3. Idempotency keys ensure side-effects are not duplicated.
