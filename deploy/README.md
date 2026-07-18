# deploy

Puts [`data-serve`](../data-serve/README.md) and
[`d3-interactive-web`](../d3-interactive-web/README.md) on the public
internet, for free, so the Pokedex page can be shown to someone without
them cloning the repo or running anything locally.

**Currently live at:**
- Page: https://hovinh.github.io/web-development-learning-lab/
- API: https://pokedex-learning-lab-api.onrender.com/api/meta

This is the first stage that isn't part of the curriculum pipeline
itself - it doesn't produce or transform data, it just hosts two stages
that already exist. Unlike every other stage folder, `deploy/` has no
Python/JS code of its own to run; it's Blueprint/workflow config plus a
couple of verification scripts.

## Why two separate hosts

The app is two independently-run pieces locally (see
`d3-interactive-web/README.md`'s "Running it"), and that split carries
over to deployment - there's no single free host that runs both a
static file server *and* a Python process:

| Piece | What it needs | Free host used here |
|---|---|---|
| `data-serve` | a real Python process (Flask + gunicorn) | [Render](https://render.com), free web service |
| `d3-interactive-web` | static file hosting only (no build step, D3 loads from a CDN) | [GitHub Pages](https://pages.github.com/) |

## First-time setup

Everything *after* this section happens automatically on `git push` -
this part is a one-time link-up per platform, and both platforms
require it to happen through their own login (there's no way to fully
script account creation on a free tier you don't already have API
credentials for).

**1. Backend (Render), via the Blueprint in [`render.yaml`](render.yaml):**

Click **[Deploy to Render](https://render.com/deploy?repo=https://github.com/hovinh/web-development-learning-lab)**
(creates/logs into a free Render account, reads `deploy/render.yaml`,
and provisions the `pokedex-learning-lab-api` service exactly as
described there - see that file's comments for what each setting does
and why). Once created, every push to `main` that changes `data-serve/`
redeploys it automatically; this button is only needed once.

If Render assigns a different URL than
`https://pokedex-learning-lab-api.onrender.com` (it will if that name is
already taken), update `DEPLOYED_API_BASE` in
[`d3-interactive-web/js/api.js`](../d3-interactive-web/js/api.js) to
match, and pass the real URL to `check_deployment` below.

**2. Frontend (GitHub Pages), via the workflow in
[`.github/workflows/deploy-frontend-pages.yml`](../.github/workflows/deploy-frontend-pages.yml):**

GitHub Pages has to be switched to "deploy via Actions" before that
workflow's first run can publish anything - a workflow can't flip this
setting for itself. Do it either way:

- **Scripted** (needs the [GitHub CLI](https://cli.github.com/),
  `gh auth login` once beforehand):
  ```bash
  deploy/scripts/setup_github_pages.sh     # bash
  ```
  ```powershell
  deploy/scripts/setup_github_pages.ps1    # PowerShell
  ```
- **Manual**: repo Settings -> Pages -> Source -> **GitHub Actions**.

After that, every push to `main` that changes `d3-interactive-web/`
redeploys it automatically at
`https://hovinh.github.io/web-development-learning-lab/`.

## Everyday workflow

With both one-time steps done, deploying is just:

```bash
git push origin main
```

- Changed `data-serve/`? Render rebuilds and redeploys the API (its own
  dashboard shows build logs).
- Changed `d3-interactive-web/`? The GitHub Actions workflow rebuilds
  and redeploys the page (see the repo's Actions tab).
- Changed something in neither? Nothing redeploys - both are scoped by
  path (Render via `rootDir`, the workflow via `paths:`).

Check that a deploy actually landed with the health-check script:

```bash
deploy/scripts/check_deployment.sh       # bash
```
```powershell
deploy/scripts/check_deployment.ps1      # PowerShell
```

It hits the live API's `/api/meta` and the live page, and fails loudly
if either doesn't look right - faster than opening a browser and
eyeballing it.

## Free-tier tradeoffs

- **Render's free web services spin down after 15 minutes idle.** The
  first request after that takes roughly 30-50 seconds while it wakes
  back up - expected, not a bug. `d3-interactive-web`'s existing "API
  unreachable" message (see `js/app.js`) will briefly show during that
  window; reloading once it's up resolves it.
- **No persistent disk on the free tier**, which is why `render.yaml`
  rebuilds `pokedex.db` from `data-process`'s committed JSON/images on
  every deploy (see `load_sqlite.py`) instead of expecting the database
  file to survive between deploys.
- **CORS is wide open** (`origins: "*"` in `data-serve/app.py`) rather
  than scoped to the GitHub Pages origin specifically - acceptable for
  a public read-only demo of a public dataset, called out here because
  a real production API should generally scope this narrower.

## Local dev is unaffected

`API_BASE` in `d3-interactive-web/js/api.js` picks the local vs.
deployed API by checking the page's own hostname (see that file's
comments) - running `python data-serve/app.py` +
`npm run serve -- d3-interactive-web` locally still works exactly as
before, nothing here changes that path.
