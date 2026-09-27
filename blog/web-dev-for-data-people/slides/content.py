"""The talk content itself, as data - this is the file to edit to fine-tune the deck.

Every slide is a `Slide` (one visual, one idea) grouped into a `Section` (one
beat of the talk). `generate_deck.py` walks `SECTIONS` in order, assigns each
section an accent color (cycling theme.SERIES), and renders every slide with
theme.py's builder for its `kind`. Nothing about layout, color, or fonts
lives here - only what the deck says and how long each slide should take.

Image paths are relative to `assets/screenshots/`. A missing file renders as
a clearly-labeled placeholder box instead of failing the build, so the deck
can be regenerated at any point in the screenshot-capture process.

Source material: `../2026-09-20-web-dev-for-data-people.md` (the blog post)
and the four `demos/` READMEs it backs. Section 8 ("Stay in the driver's
seat") is the one beat that isn't a paraphrase of the post - it's the
speaker's own framing of the post's closing line, given its own slides
because it's the thesis of the talk, not just the blog's.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Slide:
    kind: str
    title: str = ""
    subtitle: str = ""
    icon: str = ""
    bullets: list[str] = field(default_factory=list)
    image: str | None = None
    caption: str = ""
    image_left: str | None = None
    caption_left: str = ""
    image_right: str | None = None
    caption_right: str = ""
    table_headers: list[str] = field(default_factory=list)
    table_rows: list[list[str]] = field(default_factory=list)
    comp_left_header: str = ""
    comp_right_header: str = ""
    comp_rows: list[tuple[str, str, str]] = field(default_factory=list)
    ladder_rungs: list[tuple[int, str, str, str]] = field(default_factory=list)
    quote_text: str = ""
    notes: str = ""
    minutes: float = 1.0


@dataclass
class Section:
    name: str
    icon: str
    slides: list[Slide]


SECTIONS: list[Section] = [
    # ------------------------------------------------------------------
    Section(
        name="Open",
        icon="🧭",
        slides=[
            Slide(
                kind="title",
                title="Web Dev for Data People",
                subtitle="Choosing a stack, working with an LLM, and staying in control",
                icon="🧭",
                notes="Welcome. ~90 minutes total, including four live demos. "
                "Questions welcome any time, or hold them - your call as speaker.",
                minutes=1,
            ),
            Slide(
                kind="bullets",
                title="What we'll cover",
                icon="🗺️",
                bullets=[
                    "Why this matters for data people, not just engineers",
                    "A ladder for picking the lightest tool that works",
                    "Two gaps that quietly turn a demo into a product",
                    "How to use an LLM without losing control of your own codebase",
                    "Four live demos - screenshots included as a backup",
                ],
                notes="Set expectations for the shape of the talk before diving in.",
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Why it matters",
        icon="🙋",
        slides=[
            Slide(
                kind="bullets",
                title="The moment every analysis hits",
                icon="👀",
                bullets=[
                    "A chart in a notebook convinces you.",
                    "It rarely convinces a colleague who is never going to open that notebook.",
                    "A small web app can: move a slider, filter to their own region, "
                    "type a value and watch the model's answer change.",
                    "That feels very different from a screenshot.",
                ],
                notes="Open with the everyday moment - this is the 'why' before any tooling talk.",
                minutes=2,
            ),
            Slide(
                kind="bullets",
                title="Where this quietly pays off",
                icon="🎯",
                bullets=[
                    "Makes exploring a dataset more interactive",
                    "Demonstrates a model as a live service",
                    "Prototypes a product idea before anyone spends engineering time on it",
                    "An LLM can write most of the boilerplate for you now",
                    "…but the difficulty didn't disappear. It moved: to picking the right tool.",
                ],
                notes="Land the hook: the assistant will build whatever you name - the costly "
                "mistake now happens earlier, picking wrong and finding out three days in.",
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="A field too wide",
        icon="🌐",
        slides=[
            Slide(
                kind="image",
                title="Where each tool lives",
                icon="🗺️",
                image="field-map/field-map.png",
                caption="Same band = alternatives. Different bands = usually combine.",
                notes="Walk top to bottom: Python-native UI, browser, server, and underneath it "
                "all, the pandas/model work that's already there.",
                minutes=2.5,
            ),
            Slide(
                kind="bullets",
                title="Two easy things to miss",
                icon="👓",
                bullets=[
                    "Tailwind isn't a rival to Django or React - it only styles, "
                    "so it works with any of them.",
                    "React and Angular sit on the same rung: both still need something else "
                    "to supply data and handle login.",
                    "If you live in Python: Streamlit and Dash need zero JavaScript, "
                    "and for many tasks that's the whole answer.",
                ],
                notes="These two misconceptions cause most of the 'framework wars' confusion.",
                minutes=2.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Decompose before you choose",
        icon="🧩",
        slides=[
            Slide(
                kind="bullets",
                title="Stop asking 'which framework?'",
                icon="❓",
                bullets=[
                    "Ask instead: what does this app actually have to do?",
                    "Any web app is some combination of the same 12 capabilities.",
                    "Tick the rows your use case needs - the ticks are the decision.",
                ],
                notes="This reframe is the whole method the rest of the talk builds on.",
                minutes=2,
            ),
            Slide(
                kind="table",
                title="The 12 functionalities",
                icon="🧾",
                table_headers=["#", "Functionality", "What it means"],
                table_rows=[
                    ["1", "Presentation", "Show static content"],
                    ["2", "Styling & layout", "Make it look decent and consistent"],
                    ["3", "Client interactivity", "Filters and tooltips, no page reload"],
                    ["4", "API: providing", "Expose data or a model over HTTP"],
                    ["5", "API: consuming", "A page or service calls an API"],
                    ["6", "Server-side compute", "Run pandas or a model per request"],
                    ["7", "Persistence", "Save records"],
                    ["8", "Forms & CRUD", "Validated create, edit, delete"],
                    ["9", "Authentication", "Who is this user?"],
                    ["10", "Authorization", "What may they do or see?"],
                    ["11", "Session & state", "Remember a user's choices"],
                    ["12", "Background / long jobs", "Work that outlives one request"],
                ],
                notes="Dense slide on purpose - give it room. Don't read every row; point at "
                "a few (7-10) since they come back in the 'two gaps' section later.",
                minutes=3,
            ),
            Slide(
                kind="bullets",
                title="Worked examples",
                icon="✅",
                bullets=[
                    "Share a chart you're proud of  →  functions 1, 2, 3",
                    "Explore a dataset  →  functions 3, 6",
                    "A labeling tool  →  7 through 10 on top of the rest",
                    "The number of ticks is the signal: each tick from persistence onward "
                    "is a reason to reach for a heavier tool.",
                ],
                notes="Bridge straight into the ladder section.",
                minutes=3,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="From functionalities to a stack",
        icon="🪜",
        slides=[
            Slide(
                kind="ladder",
                title="Climb only when you must",
                icon="🪜",
                ladder_rungs=[
                    (1, "Static HTML + D3", "— show a finished result, no server at all",
                     "no install, or: npm install http-server"),
                    (2, "Streamlit or Dash", "— explore data, or build a tool for peers. Python only",
                     "pip install streamlit   /   pip install dash"),
                    (3, "Flask or FastAPI", "— serve a model or data over HTTP",
                     "pip install fastapi uvicorn   /   pip install flask"),
                    (4, "Django + a Tailwind kit", "— users, a database, forms, and an admin",
                     "pip install django  →  django-admin startproject"),
                    (5, "React or Angular over an API", "— only when the UI is genuinely app-like",
                     "npm create vite@latest -- --template react"),
                ],
                notes="Read the pull-quote: start at the lowest rung that covers every tick; "
                "climb only when you can name the specific thing the rung below can't do.",
                minutes=3.5,
            ),
            Slide(
                kind="table",
                title="Applied to concrete cases",
                icon="🎯",
                table_headers=["Use case", "Functions", "Pick"],
                table_rows=[
                    ["Share a finished chart", "1, 2, 3", "Static HTML + D3"],
                    ["Explore a dataset", "3, 6", "Streamlit"],
                    ["Peer dashboard", "3, 6", "Dash"],
                    ["Demo a model", "4, 6", "FastAPI - /docs is a free test form"],
                    ["Labeling or review tool", "7-10", "Django"],
                    ["Pipeline that ends in a page", "1, 3", "Python writes JSON, D3 renders it"],
                ],
                notes="Mention the honest caveat: React+Tailwind is 2 projects, a build step, "
                "and auth you write yourself - climb there only for app-like UI needs.",
                minutes=3.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Pretty enough",
        icon="💅",
        slides=[
            Slide(
                kind="table",
                title="Pretty enough for business users",
                icon="💅",
                table_headers=["Option", "Good for"],
                table_rows=[
                    ["Django templates, Tailwind, daisyUI", "A clean prototype with no React - the default"],
                    ["React, Tailwind, shadcn/ui", "The best-looking and most customizable, highest setup cost"],
                    ["Dash + dash-bootstrap-components", "Tidy dashboards out of the box"],
                    ["Django admin", "Back-office screens for free"],
                ],
                notes="Raw Tailwind gives utility classes, not a design - a component kit is "
                "what makes it look 'standard'. Mention the standalone CLI, no-Node option.",
                minutes=4,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Gap: multi-user",
        icon="🔐",
        slides=[
            Slide(
                kind="bullets",
                title="Multi-user: six things to solve",
                icon="🔐",
                bullets=[
                    "Authentication — who is this user?",
                    "Authorization — what may they do?",
                    "Data isolation — user A never sees user B's rows",
                    "Per-user state, concurrent writes, and an audit trail",
                    "None of this shows up in a 'build a dashboard in 10 minutes' tutorial.",
                ],
                notes="This and background jobs are the two gaps that bite the moment a demo "
                "becomes a product.",
                minutes=2.5,
            ),
            Slide(
                kind="table",
                title="The tools differ sharply here",
                icon="⚖️",
                table_headers=["Tool", "What you get"],
                table_rows=[
                    ["Django", "Auth, sessions, groups & permissions - all built in"],
                    ["FastAPI", "Nothing built in - docs show an OAuth2/JWT pattern to write yourself"],
                    ["Streamlit", "Built-in OIDC login (Google, Microsoft) - but no roles"],
                    ["Dash", "dash-auth: HTTP Basic only, no logout"],
                    ["React, Angular", "Login screens only - real security lives on the server"],
                ],
                notes="The rule to repeat: authorization is enforced on the server. Hiding a "
                "button in React protects nothing. Streamlit's cache is shared across all users.",
                minutes=2.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Gap: background jobs",
        icon="⏳",
        slides=[
            Slide(
                kind="ladder",
                title="A request must answer in seconds. Retraining a model doesn't.",
                icon="⏳",
                ladder_rungs=[
                    (1, "The request starts the job", "and returns at once", ""),
                    (2, "The job runs", "somewhere else", ""),
                    (3, "Its status is", "stored", ""),
                    (4, "The page checks back", "every few seconds", ""),
                ],
                notes="The fix is always this same shape. This exact sequence reappears in "
                "demo 3, coming up shortly.",
                minutes=2.5,
            ),
            Slide(
                kind="table",
                title="Surprising traps, especially on Windows",
                icon="🪟",
                table_headers=["Need", "Tool", "Catch"],
                table_rows=[
                    ["Tiny work after a response", "FastAPI BackgroundTasks", "In-process, no persistence/retries"],
                    ["Simple queue, no Redis", "Huey + SQLite", "Smaller ecosystem"],
                    ["Simple queue + Redis", "RQ", "Uses os.fork - no native Windows support"],
                    ["Full-featured queue", "Celery", "Windows is unsupported by the project"],
                    ["Django's own API", "django.tasks (6.0)", "Defines enqueue, ships no worker"],
                ],
                notes="My default for a laptop: polling + a job-status table, Huey with SQLite "
                "for the worker. We'll prove that live in a few minutes.",
                minutes=2.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Stay in the driver's seat",
        icon="🧠",
        slides=[
            Slide(
                kind="quote",
                title="Web is secondary here",
                icon="🧠",
                quote_text="An LLM makes writing the code cheap. That makes the choice of "
                "what to write - and who owns the logic - the one part worth your care.",
                notes="This is the thesis of the whole talk, not just the blog's closing line. "
                "Everything before this was building the vocabulary to make that choice well.",
                minutes=2.5,
            ),
            Slide(
                kind="bullets",
                title="Let the LLM write boilerplate. You hold the backend logic.",
                icon="🎛️",
                bullets=[
                    "✅ 'Write a Django view that filters by request.user' — you already "
                    "decided the ownership rule",
                    "✅ 'Scaffold this FastAPI route from my Pydantic model' — you own the model",
                    "🚫 'Build me a labeling tool' and walking away — now the LLM decided "
                    "your data model, your auth, your schema",
                    "The 12-functionality list is exactly how you stay the one deciding, "
                    "not just the one asking",
                    "If everything is LLM-driven end to end, you stop being able to explain "
                    "your own codebase",
                ],
                notes="Land this before the head-to-head comparison - it reframes why the "
                "Django-vs-FastAPI contrast coming up matters beyond 'which is prettier'.",
                minutes=2.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Two real stacks",
        icon="⚔️",
        slides=[
            Slide(
                kind="bullets",
                title="The test case: a labeling tool",
                icon="🏷️",
                bullets=[
                    "A model has predicted a category for a batch of support tickets.",
                    "Reviewers label rows; admins see everyone's labels and manage users.",
                    "A reviewer sees only the rows assigned to them.",
                    "A long job re-scores the data with a new model.",
                    "That touches almost all 12 functionalities — a fair test.",
                ],
                notes="Set up the comparison before showing the table.",
                minutes=2,
            ),
            Slide(
                kind="comparison",
                title="Django vs. FastAPI + React + Tailwind",
                icon="⚔️",
                comp_left_header="Django (one project)",
                comp_right_header="FastAPI + React (two projects)",
                comp_rows=[
                    ("Login & users", "Built in", "You build it"),
                    ("Ownership filtering", "A queryset filter, one line", "A check in every endpoint"),
                    ("Forms & validation", "Automatic", "Pydantic + client-side form state"),
                    ("Back-office screens", "Admin gives users & labels for free", "You build them"),
                    ("API for other systems", "Add Django REST Framework", "Built in, with automatic docs"),
                    ("Interface feel", "Page loads, a little JS", "Instant, app-like"),
                ],
                notes="For a small team, Django wins on time. FastAPI+React wins when the UI "
                "must be fast/keyboard-driven, another system needs the API, or a front-end "
                "engineer owns the UI.",
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Demo: Django",
        icon="🐍",
        slides=[
            Slide(
                kind="bullets",
                title="Live demo: Django labeling tool",
                icon="🐍",
                bullets=[
                    "Log in as alice → see only her queue",
                    "Try one of bob's item ids as alice → 404, not a data leak",
                    "Log in as admin → /admin/ shows every reviewer's labels, "
                    "zero view or template code written for it",
                ],
                notes="SWITCH TO THE BROWSER NOW. http://127.0.0.1:8000/ - alice/demo-alice-pw, "
                "bob/demo-bob-pw, admin/demo-admin-pw. Fallback screenshots on the next slide.",
                minutes=3.5,
            ),
            Slide(
                kind="image_pair",
                title="What we just saw",
                icon="✅",
                image_left="django/alice-queue.png",
                caption_left="Alice's queue — only her tickets",
                image_right="django/admin-labels.png",
                caption_right="Admin: every reviewer's labels, free",
                notes="`Item.objects.filter(assigned_to=request.user)` is the whole ownership "
                "rule, one line. Auth is django.contrib.auth.urls - zero hand-written view code.",
                minutes=3.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Demo: FastAPI + React",
        icon="⚛️",
        slides=[
            Slide(
                kind="bullets",
                title="Live demo: FastAPI + React labeling tool",
                icon="⚛️",
                bullets=[
                    "Same task, same data, same three users",
                    "Log in as alice, label with the 1 / 2 / 3 keys — watch it "
                    "auto-advance, no page reload",
                    "Open /docs — FastAPI's free Swagger test form",
                    "Ownership is checked in three separate places, not one",
                ],
                notes="http://localhost:5173/ for the app, http://127.0.0.1:8000/docs for "
                "Swagger. Same credentials as the Django demo.",
                minutes=3.5,
            ),
            Slide(
                kind="image_pair",
                title="What we just saw",
                icon="✅",
                image_left="fastapi-react/labeling-in-progress.png",
                caption_left="Keyboard-driven, instant, app-like",
                image_right="fastapi-react/swagger-docs.png",
                caption_right="/docs — the free test form",
                notes="The payoff cost more code: JWTs minted by hand, ownership repeated "
                "across GET/POST/list endpoints instead of one queryset filter.",
                minutes=3.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Debrief",
        icon="🧭",
        slides=[
            Slide(
                kind="bullets",
                title="Same guarantee, two very different bills",
                icon="🧭",
                bullets=[
                    "Django: less code, an admin for free, a queryset filter for the hard part",
                    "FastAPI + React: more code, but an instant, keyboard-driven feel and a "
                    "separate API other systems can call",
                    "Start with Django, outgrow it, add an API and put React in front later — "
                    "you don't have to throw away the data model",
                ],
                notes="Close the loop on the comparison before moving to the next demo.",
                minutes=3,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Demo: long jobs",
        icon="⏱️",
        slides=[
            Slide(
                kind="bullets",
                title="Live demo: blocking vs. queued",
                icon="⏱️",
                bullets=[
                    "Click 'Start blocking rescore' — the tab just sits there for ~15s, "
                    "nothing to show for it",
                    "Click 'Start queued rescore' — a job id appears instantly, and a progress "
                    "bar climbs 0 → 30 while the page stays fully responsive",
                    "Huey + SQLite: no Redis, nothing to install beyond Python — verified "
                    "working on Windows with -k thread",
                ],
                notes="http://127.0.0.1:8000/. The blocking button is the whole point: there's "
                "nothing to screenshot while it hangs, and that's exactly the problem.",
                minutes=3,
            ),
            Slide(
                kind="image_pair",
                title="What we just saw",
                icon="✅",
                image_left="long-jobs/blocking-stuck.png",
                caption_left="Blocking: button disabled, 'waiting for the server' - and that's it",
                image_right="long-jobs/queued-progress.png",
                caption_right="Queued: job id back at once, progress climbing, page stays responsive",
                notes="The blocking button really does just sit there disabled for ~15s with no "
                "progress signal - the contrast with the queued version is the whole lesson.",
                minutes=3,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Demo: PSA map",
        icon="🌍",
        slides=[
            Slide(
                kind="bullets",
                title="Live demo: the skill, as a runnable page",
                icon="🌍",
                bullets=[
                    "Static HTML + D3 + Tailwind — rung 1 of the ladder, because that's "
                    "exactly what this use case needs",
                    "27 PSA container terminals worldwide, cross-filtered map + charts",
                    "The page shows its own working, not just the product",
                ],
                notes="Served at whatever URL `npm run serve -- demos/psa-terminal-map` prints "
                "(typically http://localhost:8080).",
                minutes=2.5,
            ),
            Slide(
                kind="image_pair",
                title="The product",
                icon="🗺️",
                image_left="psa-map/map-overview.png",
                caption_left="27 terminals, filterable, zoomable",
                image_right="psa-map/detail-card.png",
                caption_right="Click a terminal → a sourced detail card",
                notes="",
                minutes=2.5,
            ),
            Slide(
                kind="image_pair",
                title="The skill, showing its work",
                icon="🔬",
                image_left="psa-map/build-trail.png",
                caption_left="Act 2 — the 12-functionality verdict for THIS app",
                image_right="psa-map/live-advisor.png",
                caption_right="Act 3 — try the advisor live, same logic, tested",
                notes="The point: the skill's advice is a function you can run, not an "
                "opinion — asserted by a test suite against all 8 documented use cases.",
                minutes=3,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Try it",
        icon="🛠️",
        slides=[
            Slide(
                kind="bullets",
                title="Try it: a skill file",
                icon="🛠️",
                bullets=[
                    "The whole framework, packaged as a Markdown file your AI assistant loads",
                    "Describe an app idea → it ticks the 12 functionalities and recommends "
                    "the lightest stack",
                    "Flags the two gaps (multi-user, background jobs) automatically",
                    "Drop the folder into .claude/skills/ of any project",
                ],
                notes="This is the 'go try it yourself' moment.",
                minutes=2,
            ),
            Slide(
                kind="table",
                title="Setup cheat-sheet",
                icon="📋",
                table_headers=["Rung", "Install"],
                table_rows=[
                    ["Static HTML + D3", "Nothing — or npm install http-server to preview locally"],
                    ["Streamlit", "pip install streamlit"],
                    ["Dash", "pip install dash"],
                    ["Flask", "pip install flask"],
                    ["FastAPI", "pip install fastapi uvicorn"],
                    ["Django", "pip install django  →  django-admin startproject"],
                    ["React (Vite)", "npm create vite@latest"],
                    ["Tailwind, no Node", "standalone CLI, or the CDN browser build — even pip-installable"],
                    ["daisyUI", "npm package, or paired with Tailwind's CDN build"],
                ],
                notes="Honest caveat: everything here assumes it runs on your own machine. "
                "Deployment is a separate decision.",
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Close",
        icon="🎬",
        slides=[
            Slide(
                kind="bullets",
                title="Three lessons",
                icon="🎬",
                bullets=[
                    "Audience matters as much as architecture — a peer forgives a plain "
                    "page, a business user doesn't",
                    "Multi-user and background jobs are where a demo silently becomes a "
                    "product",
                    "An LLM makes writing code cheap — which makes the choice of what to "
                    "write the one part worth your care",
                ],
                notes="Close on the throughline: decompose before you choose.",
                minutes=2,
            ),
            Slide(
                kind="title",
                title="Questions?",
                subtitle="Decompose before you choose.",
                icon="🙌",
                notes="Thank you. Open the floor.",
                minutes=2,
            ),
        ],
    ),
]


def total_minutes() -> float:
    return sum(slide.minutes for section in SECTIONS for slide in section.slides)


def total_slides() -> int:
    return sum(len(section.slides) for section in SECTIONS)
