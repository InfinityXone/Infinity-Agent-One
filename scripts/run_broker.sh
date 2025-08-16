#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${INFINITY_BROKER_SECRET:?Set INFINITY_BROKER_SECRET first}"
export HANDSHAKE_HEADER="${HANDSHAKE_HEADER:-NEO-PULSE}"
export AGENT_ID="${AGENT_ID:-FinSynapse}"
python3 -m venv .venv && source .venv/bin/activate
pip install -r broker/requirements.txt
exec uvicorn broker.main:app --host 0.0.0.0 --port 8001
