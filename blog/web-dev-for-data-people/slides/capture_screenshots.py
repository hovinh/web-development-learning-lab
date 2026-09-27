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
# A narrower viewport for demos whose screenshots sit side by side on an
# image_pair slide (half the slide width each): at 1600px the app's text
# ends up too small to read from the back of a room once scaled down.
# 1280px keeps the same layout but makes everything ~25% larger on the slide.
SLIDE_PAIR_VIEWPORT = {"width": 1280, "height": 800}
DEVICE_SCALE_FACTOR = 2  # crisp screenshots on a projector, not just a laptop screen


def _new_page(browser, viewport=VIEWPORT):
    return browser.new_page(viewport=viewport, device_scale_factor=DEVICE_SCALE_FACTOR)


def _login(page: Page, username_selector: str, password_selector: str, submit_selector: str,
           username: str, password: str) -> None:
    page.fill(username_selector, username)
    page.fill(password_selector, password)
    page.click(submit_selector)
    page.wait_for_load_state("networkidle")


def _django_label_some_items(browser, base_url: str, username: str, password: str,
                             decisions: list[str]) -> None:
    """Log in as one reviewer (in a fresh browser context, so no cookies
    carry over between users) and label the first few items in their queue.

    Why this exists: the admin "Labels" screenshot is the deck's evidence
    for "admins see every reviewer's labels, for free" - captured against a
    freshly seeded database it showed "0 labels", the opposite of its own
    caption. Labeling as two different reviewers first makes the admin list
    show exactly the claim: rows from alice AND bob, in one place.
    """
    context = browser.new_context(viewport=SLIDE_PAIR_VIEWPORT, device_scale_factor=DEVICE_SCALE_FACTOR)
    page = context.new_page()
    page.goto(f"{base_url}/accounts/login/")
    _login(page, "#id_username", "#id_password", "button[type=submit], input[type=submit]",
           username, password)
    # Item links in the queue look like "/7/" - read them off the page
    # rather than assuming which ids the seed's round-robin gave this user.
    hrefs = page.eval_on_selector_all(
        "a[href]", "els => els.map(e => e.getAttribute('href')).filter(h => /^\\/\\d+\\/$/.test(h))"
    )
    for href, decision in zip(hrefs, decisions):
        page.goto(f"{base_url}{href}")
        page.check(f"input[name='decision'][value='{decision}']")
        # Not a bare "button[type=submit]": the navbar's "Log out" is also a
        # submit button (a POST form), and it comes first in the page.
        page.click("button:has-text('Save label')")
        page.wait_for_load_state("networkidle")
    context.close()


def capture_django(base_url: str = "http://127.0.0.1:8000") -> None:
    """Assumes `manage.py migrate` + `seed_demo` + `runserver` are already running.

    Writes labels into the demo's (gitignored) db.sqlite3 as a side effect -
    see _django_label_some_items. Safe to re-run: relabeling updates in place.
    """
    out = ASSETS_DIR / "django"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        _django_label_some_items(browser, base_url, "alice", "demo-alice-pw",
                                 ["correct", "incorrect", "correct"])
        _django_label_some_items(browser, base_url, "bob", "demo-bob-pw",
                                 ["correct", "unsure"])

        page = _new_page(browser, SLIDE_PAIR_VIEWPORT)

        page.goto(f"{base_url}/accounts/login/")
        _login(page, "#id_username", "#id_password", "button[type=submit], input[type=submit]",
               "alice", "demo-alice-pw")
        # Viewport only, not full_page: the full 15-row queue is a tall strip
        # that shrinks to unreadable on a half-width slide slot. The first
        # screenful already makes the point (her tickets, some labeled).
        page.screenshot(path=str(out / "alice-queue.png"))

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
        page = _new_page(browser, SLIDE_PAIR_VIEWPORT)

        page.goto(base_url)
        page.wait_for_selector("#map svg circle.mark-circle")
        page.screenshot(path=str(out / "map-overview.png"))

        page.click("#map svg circle.mark-circle >> nth=0")
        page.wait_for_selector("#detail-panel")
        # The click leaves the mouse over the map, so the terminal's hover
        # tooltip stays open and lands on top of the detail card - move the
        # pointer to a blank corner and let the tooltip hide first.
        page.mouse.move(2, 2)
        page.wait_for_timeout(300)
        page.locator("#detail-panel").screenshot(path=str(out / "detail-card.png"))

        # Element screenshots, not the viewport: the caption is about the
        # 12-functionality verdict table and the advisor, so crop to exactly
        # those instead of a full screen of small surrounding text. The
        # page's sticky navbar (.site-navbar) would otherwise be painted over
        # the top of each crop, hiding the table's header row - hide it
        # first (screenshot-only; the demo itself is untouched).
        page.add_style_tag(content=".site-navbar { display: none !important; }")
        page.locator("#build-trail").scroll_into_view_if_needed()
        page.wait_for_selector("#functionality-table-body")
        page.locator("#functionality-table-body").locator("xpath=ancestor::table[1]").screenshot(
            path=str(out / "build-trail.png")
        )

        page.locator("#use-case-shortcuts button").first.scroll_into_view_if_needed()
        page.locator("#use-case-shortcuts button").first.click()
        page.wait_for_selector("#advisor-result:not(.is-empty)")
        page.locator("#advisor").screenshot(path=str(out / "live-advisor.png"))

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
