#!/bin/bash
set -euo pipefail

# Keep the session alive even if your phone browser dies
if ! command -v tmux >/dev/null 2>&1; then
  sudo apt-get update -y >/dev/null
  sudo apt-get install -y tmux >/dev/null
fi

# Start a new tmux session or attach to existing one
tmux new-session -d -s builder_store 2>/dev/null || true
tmux attach-session -t builder_store 2>/dev/null || echo "Session 'builder_store' is running in background"
