#!/bin/bash
cd $(dirname $0)/..
source venv/bin/activate
export $(grep -v '^#' config/.env.agent_one | xargs)
uvicorn api:app --host 0.0.0.0 --port 8787 --reload
