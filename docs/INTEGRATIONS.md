# Adding a New Tool Integration

1. Create a new adapter in `autopilot/adapters` implementing the required methods.
2. Ensure every method accepts an idempotency key and supports `dry_run`.
3. Add adapter wiring in workflows and guardrails in `autopilot/workflows`.
4. Add tests to validate idempotency and failure/retry behavior.
5. Update `docs/MISSING_INFO.md` if the adapter depends on provider-specific choices.
