#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-.}"
cd "$REPO"
echo "🔧 Stamping port 8001 across repo: $REPO"
mapfile -t FILES < <(git ls-files | grep -E '\.(env|json|js|ts|tsx|py|md|sh|yaml|yml|toml|txt)$')
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  sed -i.bak \
    -e 's#:8000\b#:8001#g' \
    -e 's#http://0\.0\.0\.0:8000#http://0.0.0.0:8001#g' \
    -e 's#http://127\.0\.0\.1:8000#http://127.0.0.1:8001#g' \
    -e 's#http://localhost:8000#http://localhost:8001#g' \
    -e 's#\bPORT=8000\b#PORT=8001#g' \
    -e 's#\bINFINITY_LOOP_PORT=8000\b#INFINITY_LOOP_PORT=8001#g' \
    -e 's#\bBROKER_PORT=8000\b#BROKER_PORT=8001#g' \
    "$f" || true
  cmp -s "$f" "$f.bak" && rm -f "$f.bak" || true
done
find . -name "*.bak" -type f -delete || true
git add -A || true
git diff --cached --quiet || git commit -m "chore: canonicalize broker port → 8001 (auto-stamp)"
echo "✅ Port stamping complete."
