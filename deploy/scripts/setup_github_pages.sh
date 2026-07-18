#!/usr/bin/env bash
# One-time setup: point this repo's GitHub Pages at the Actions workflow
# (../../.github/workflows/deploy-frontend-pages.yml) instead of the
# classic "serve a branch/folder" mode - the workflow can't turn Pages
# on for itself, GitHub requires this to exist first. Run this once;
# every deploy after that is fully automatic (a push touching
# d3-interactive-web/ triggers the workflow, no manual step involved).
#
# Requires the GitHub CLI (`gh`), already authenticated: `gh auth login`.
# See ../README.md's "First-time setup" for the no-gh alternative
# (three clicks in Settings -> Pages).

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh (GitHub CLI) not found - install it from https://cli.github.com/" >&2
  echo "or follow the manual steps in deploy/README.md instead." >&2
  exit 1
fi

repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
echo "Enabling GitHub Pages (Actions-driven) for $repo..."

if gh api "repos/$repo/pages" >/dev/null 2>&1; then
  # Pages is already on (e.g. someone enabled it via the UI already) -
  # switch its build type rather than trying to create it again.
  gh api -X PUT "repos/$repo/pages" -f build_type=workflow
else
  gh api -X POST "repos/$repo/pages" -f build_type=workflow
fi

echo "Done. Push to main (touching d3-interactive-web/) to trigger the first deploy,"
echo "or trigger it immediately: gh workflow run deploy-frontend-pages.yml"
