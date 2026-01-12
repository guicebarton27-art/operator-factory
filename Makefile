SHELL := /bin/bash

.PHONY: doctor setup test run lint

doctor:
	@python3 -c 'import sys; print("Python", sys.version)'
	@python3 -c 'import psycopg, jsonschema; print("deps ok")'
	@python3 - <<'PY'
import os
missing = [k for k in ["DATABASE_URL"] if not os.getenv(k)]
if missing:
    print("Missing env vars:", ", ".join(missing))
    raise SystemExit(1)
print("Env ok")
PY

setup:
	@python3 -m pip install -r requirements.txt
	@docker compose up -d
	@python3 -m autopilot.src.db init --database-url $$DATABASE_URL

run:
	@python3 -m autopilot.bin.autopilot run

test:
	@pytest -q

lint:
	@python3 -m py_compile $(shell find autopilot -name '*.py')
