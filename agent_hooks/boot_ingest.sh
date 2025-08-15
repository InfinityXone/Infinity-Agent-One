
#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "[AgentOne] Boot ingest: soul + knowledge (idempotent)"
python3 "$ROOT/ingestion/soul_ingest.py" --path "$ROOT/soul" --namespace origin || true
python3 "$ROOT/ingestion/ingest.py" --path "$ROOT/soul" --namespace etherverse || true
