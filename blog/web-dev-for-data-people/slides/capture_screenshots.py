"""Re-capture the deck's demo screenshots with Playwright.

Each demo needs its own server(s) already running (and seeded, where it has
a database) before calling its capture function here - see README.md's
"Re-capturing screenshots" section, and each demo's own README, for exact
run commands. This module doesn't start or stop any servers itself: the
four demos have too little in common (Django's runserver, two processes for
FastAPI+React, two more for Huey, a static file server for the PSA map) for
one orchestrator to be simpler than just starting what you need by hand.

Selectors below are the ones actually confirmed working against each demo
(not guessed from source alone) when these screenshots were first captured.
If a demo's markup changes, re-check the relevant view/template/component
rather than assuming these still match.

Usage, once a demo's server(s) are up:

    python -c "import capture_screenshots as c; c.capture_django()"
    python -c "import capture_screenshots as c; c.capture_fastapi_react()"
    python -c "import capture_screenshots as c; c.capture_long_jobs()"
    python -c "import capture_screenshots as c; c.capture_psa_map()"
    python -c "import capture_screenshots as c; c.capture_field_map()"
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Page, sync_playwright

SLIDES_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SLIDES_DIR / "assets" / "screenshots"
BLOG_DIR = SLIDES_DIR.parent

VIEWPORT = {"width": 1600, "height": 1000}
DEVICE_SCALE_FACTOR = 2  # crisp screenshots on a projector, not just a laptop screen


def _new_page(browser):
    return browser.new_page(viewport=VIEWPORT, device_scale_factor=DEVICE_SCALE_FACTOR)


def _login(page: Page, username_selector: str, password_selector: str, submit_selector: str,
           username: str, password: str) -> None:
    page.fill(username_selector, username)
    page.fill(password_selector, password)
    page.click(submit_selector)
    page.wait_for_load_state("networkidle")


def capture_django(base_url: str = "http://127.0.0.1:8000") -> None:
    """Assumes `manage.py migrate` + `seed_demo` + `runserver` are already running."""
    out = ASSETS_DIR / "django"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)

        page.goto(f"{base_url}/accounts/login/")
        _login(page, "#id_username", "#id_password", "button[type=submit], input[type=submit]",
               "alice", "demo-alice-pw")
        page.screenshot(path=str(out / "alice-queue.png"), full_page=True)

        page.click("a[href='/1/']")  # first item in alice's queue
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "label-item.png"), full_page=True)

        page.goto(f"{base_url}/admin/login/")
        _login(page, "#id_username", "#id_password", "input[type=submit]",
               "admin", "demo-admin-pw")
        page.goto(f"{base_url}/admin/labeling/label/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "admin-labels.png"))

        page.goto(f"{base_url}/admin/auth/user/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "admin-users.png"))

        browser.close()


def capture_fastapi_react(web_url: str = "http://localhost:5173", api_url: str = "http://127.0.0.1:8000") -> None:
    """Assumes `api/seed.py` has run and both `uvicorn` and `npm run dev` are up."""
    out = ASSETS_DIR / "fastapi-react"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)

        page.goto(web_url)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "login.png"))

        _login(page, "label:has-text('Username') input", "label:has-text('Password') input",
               "button[type='submit']", "alice", "demo-alice-pw")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "alice-queue.png"))

        page.click("button:has-text('Correct')")
        page.wait_for_timeout(500)  # let the auto-advance animation settle
        page.screenshot(path=str(out / "labeling-in-progress.png"))

        page.goto(f"{api_url}/docs")
        page.wait_for_selector(".swagger-ui .opblock")
        page.screenshot(path=str(out / "swagger-docs.png"))

        admin_op = page.locator(".opblock-summary", has_text="/admin/labels")
        admin_op.click()
        page.wait_for_timeout(300)
        page.screenshot(path=str(out / "swagger-admin-endpoint.png"))

        browser.close()


def capture_long_jobs(base_url: str = "http://127.0.0.1:8000") -> None:
    """Assumes `uvicorn` and `huey_consumer tasks.huey -k thread` are both running."""
    out = ASSETS_DIR / "long-jobs"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)

        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(out / "idle.png"))

        page.click("text=Start queued rescore")
        page.wait_for_timeout(500)
        page.screenshot(path=str(out / "queued-start.png"))

        # Poll the progress bar's value rather than a fixed sleep - a fixed
        # sleep landed before Huey had advanced the job the first time this
        # was captured, producing a byte-identical "0/30" screenshot.
        page.wait_for_function(
            "document.querySelector('progress')?.value >= 5 "
            "&& document.querySelector('progress')?.value <= 25"
        )
        page.screenshot(path=str(out / "queued-progress.png"))

        page.wait_for_function("document.querySelector('progress')?.value >= 30", timeout=20000)
        page.screenshot(path=str(out / "queued-done.png"))

        page.reload()
        page.click("text=Start blocking rescore")
        page.wait_for_timeout(300)  # the button disables immediately - no need to wait for the response
        page.screenshot(path=str(out / "blocking-stuck.png"))

        browser.close()


def capture_psa_map(base_url: str = "http://localhost:8080") -> None:
    """Assumes `npm run serve -- demos/psa-terminal-map` is running."""
    out = ASSETS_DIR / "psa-map"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = _new_page(browser)

        page.goto(base_url)
        page.wait_for_selector("#map svg circle.mark-circle")
        page.screenshot(path=str(out / "map-overview.png"))

        page.click("#map svg circle.mark-circle >> nth=0")
        page.wait_for_selector("#detail-panel")
        page.screenshot(path=str(out / "detail-card.png"))

        page.locator("#build-trail").scroll_into_view_if_needed()
        page.wait_for_selector("#functionality-table-body")
        page.screenshot(path=str(out / "build-trail.png"))

        page.locator("#use-case-shortcuts button").first.scroll_into_view_if_needed()
        page.locator("#use-case-shortcuts button").first.click()
        page.wait_for_selector("#advisor-result:not(.is-empty)")
        page.screenshot(path=str(out / "live-advisor.png"))

        browser.close()


def capture_field_map() -> None:
    """No server needed - rasterizes the blog post's own field-map.svg."""
    out = ASSETS_DIR / "field-map"
    svg_path = (BLOG_DIR / "images" / "field-map.svg").resolve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 600}, device_scale_factor=2)
        page.goto(svg_path.as_uri())
        page.wait_for_timeout(300)
        page.query_selector("svg").screenshot(path=str(out / "field-map.png"))
        browser.close()


if __name__ == "__main__":
    import sys

    functions = {
        "django": capture_django,
        "fastapi-react": capture_fastapi_react,
        "long-jobs": capture_long_jobs,
        "psa-map": capture_psa_map,
        "field-map": capture_field_map,
    }
    if len(sys.argv) != 2 or sys.argv[1] not in functions:
        names = ", ".join(functions)
        raise SystemExit(f"Usage: python capture_screenshots.py <{names}>")
    functions[sys.argv[1]]()
