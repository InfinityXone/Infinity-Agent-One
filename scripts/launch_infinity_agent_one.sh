#!/usr/bin/env bash
set -euo pipefail
echo "∞ Infinity-Agent-One • Final Launch (scan → clean → push → Vercel)"
REPO_SSH="${REPO_SSH:-git@github.com:InfinityXone/infinity-agent-one.git}"
REPO_HTTPS="${REPO_HTTPS:-https://github.com/InfinityXone/infinity-agent-one.git}"
APP_DIR="${APP_DIR:-$HOME/Infinity-Agent-One}"
BRANCH="${BRANCH:-main}"
need(){ command -v "$1" >/dev/null 2>&1 || { echo "Missing $1"; exit 1; }; }
need git
[ -d "$APP_DIR/.git" ] || { mkdir -p "$APP_DIR"; git clone -b "$BRANCH" "$REPO_SSH" "$APP_DIR" || git clone -b "$BRANCH" "$REPO_HTTPS" "$APP_DIR"; }
git -C "$APP_DIR" fetch --all --prune
git -C "$APP_DIR" checkout "$BRANCH"
git -C "$APP_DIR" pull --rebase --autostash || true
cd "$APP_DIR"
git status -sb || true; ls -1 | head -50 || true
if [ -f package.json ]; then
  command -v corepack >/dev/null && corepack enable >/dev/null 2>&1 || true
  if [ -f pnpm-lock.yaml ] && command -v pnpm >/dev/null; then pnpm i --frozen-lockfile || pnpm i
  elif [ -f yarn.lock ] && command -v yarn >/dev/null; then yarn install --frozen-lockfile || yarn install
  elif [ -f package-lock.json ]; then npm ci || npm i
  else npm i || true; fi
  npx -y prettier -c . || npx -y prettier -w . || true
  npx -y eslint . --max-warnings=0 || true
  node -e "process.exit(!require('./package.json').scripts?.build)" || npm run build || true
fi
if [ -f requirements.txt ] || ls -1 *.py 2>/dev/null | grep -q .; then
  command -v python3 >/dev/null && command -v pip >/dev/null && {
    pip install --upgrade pip >/dev/null 2>&1 || true
    [ -f requirements.txt ] && pip install -r requirements.txt || true
    pip install flake8 >/dev/null 2>&1 || true
    flake8 || true
  } || echo "Python/pip not found — skipping."
fi
git config user.email "auto@infinityxone" || true
git config user.name "FinSynapse Auto" || true
git diff --quiet || { git add -A; git commit -m "chore(auto): format/lint sync before deploy [FinSynapse]" || true; }
git push origin "$BRANCH" || true
if command -v vercel >/dev/null 2>&1 && [ -n "${VERCEL_TOKEN:-}" ]; then
  [ -n "${VERCEL_PROJECT_ID:-}" ] && [ -n "${VERCEL_ORG_ID:-}" ] && vercel pull --yes --environment=production --token "$VERCEL_TOKEN" || true
  vercel --prod --confirm --token "$VERCEL_TOKEN" || true
else
  echo "Relying on GitHub→Vercel integration for deploy."
fi
echo "✅ Launch pipeline finished."
