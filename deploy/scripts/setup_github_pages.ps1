# One-time setup: point this repo's GitHub Pages at the Actions workflow
# (../../.github/workflows/deploy-frontend-pages.yml) instead of the
# classic "serve a branch/folder" mode - the workflow can't turn Pages
# on for itself, GitHub requires this to exist first. Run this once;
# every deploy after that is fully automatic (a push touching
# d3-interactive-web/ triggers the workflow, no manual step involved).
#
# Requires the GitHub CLI (gh), already authenticated: gh auth login.
# See ../README.md's "First-time setup" for the no-gh alternative
# (three clicks in Settings -> Pages).

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh (GitHub CLI) not found - install it from https://cli.github.com/ or follow the manual steps in deploy/README.md instead."
    exit 1
}

$repo = gh repo view --json nameWithOwner --jq .nameWithOwner
Write-Host "Enabling GitHub Pages (Actions-driven) for $repo..."

# gh api exits non-zero (and writes to stderr) when Pages doesn't exist
# yet - that failure is expected here, so it's caught rather than left
# to stop the script, per this repo's PowerShell exit-code notes.
$pagesExist = $true
try {
    gh api "repos/$repo/pages" 2>$null | Out-Null
} catch {
    $pagesExist = $false
}

if ($pagesExist) {
    # Pages is already on (e.g. someone enabled it via the UI already) -
    # switch its build type rather than trying to create it again.
    gh api -X PUT "repos/$repo/pages" -f build_type=workflow
} else {
    gh api -X POST "repos/$repo/pages" -f build_type=workflow
}

Write-Host "Done. Push to main (touching d3-interactive-web/) to trigger the first deploy,"
Write-Host "or trigger it immediately: gh workflow run deploy-frontend-pages.yml"
