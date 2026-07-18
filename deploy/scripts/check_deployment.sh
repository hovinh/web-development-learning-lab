#!/usr/bin/env bash
# Post-deploy smoke test: confirms both halves of the public deployment
# are actually reachable and serving the right thing, without opening a
# browser. Safe to (re)run any time - it only makes GET requests.
#
# Usage: deploy/scripts/check_deployment.sh [api_base] [pages_url]
# Both default to this repo's deployed URLs (see deploy/README.md);
# override either to check a different environment, e.g. a fork's.

set -euo pipefail

API_BASE="${1:-https://pokedex-learning-lab-api.onrender.com}"
PAGES_URL="${2:-https://hovinh.github.io/web-development-learning-lab/}"

echo "Checking API at $API_BASE ..."
# --fail turns a 4xx/5xx into a non-zero exit instead of printing the
# error body and succeeding; -sS keeps it quiet except on failure.
meta=$(curl --fail -sS "$API_BASE/api/meta")
echo "  $meta"
count=$(echo "$meta" | grep -o '"count": *[0-9]*' | grep -o '[0-9]*')
if [ -z "$count" ] || [ "$count" -lt 1 ]; then
  echo "  FAIL: /api/meta didn't report a positive Pokemon count" >&2
  exit 1
fi
echo "  OK: API is up and reports $count Pokemon."

echo "Checking frontend at $PAGES_URL ..."
html=$(curl --fail -sS "$PAGES_URL")
if ! echo "$html" | grep -q "Pokedex"; then
  echo "  FAIL: page loaded but didn't contain the expected title text" >&2
  exit 1
fi
echo "  OK: frontend is up and serving the expected page."

echo "Both deployments look healthy."
