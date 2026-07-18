# Post-deploy smoke test: confirms both halves of the public deployment
# are actually reachable and serving the right thing, without opening a
# browser. Safe to (re)run any time - it only makes GET requests.
#
# Usage: deploy/scripts/check_deployment.ps1 [-ApiBase <url>] [-PagesUrl <url>]
# Both default to this repo's deployed URLs (see deploy/README.md);
# override either to check a different environment, e.g. a fork's.

param(
    [string]$ApiBase = "https://pokedex-learning-lab-api.onrender.com",
    [string]$PagesUrl = "https://hovinh.github.io/web-development-learning-lab/"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking API at $ApiBase ..."
$meta = Invoke-RestMethod -Uri "$ApiBase/api/meta"
Write-Host "  backend=$($meta.backend) count=$($meta.count)"
if ($meta.count -lt 1) {
    Write-Error "  FAIL: /api/meta didn't report a positive Pokemon count"
    exit 1
}
Write-Host "  OK: API is up and reports $($meta.count) Pokemon."

Write-Host "Checking frontend at $PagesUrl ..."
$page = Invoke-WebRequest -Uri $PagesUrl -UseBasicParsing
if ($page.Content -notmatch "Pokedex") {
    Write-Error "  FAIL: page loaded but didn't contain the expected title text"
    exit 1
}
Write-Host "  OK: frontend is up and serving the expected page."

Write-Host "Both deployments look healthy."
