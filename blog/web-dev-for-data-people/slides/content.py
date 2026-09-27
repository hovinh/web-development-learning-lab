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
and the four `demos/` READMEs (and PROMPT.md files) it backs.

Who it's for, and the throughline that shapes every section below: PSA
colleagues in data roles who have their own projects and no web-dev
background. A web app shows up *afterwards*, as a supporting tool, and they
will ask an LLM to build it - that's the talk's selling point, not a side
note. So the LLM thread runs through the whole deck instead of sitting in
one section: the hook says "you'll ask an LLM", "Stay in the driver's seat"
states the thesis right after it (not 40 minutes in), the 12
functionalities are framed as the requirements you hand the LLM, each gap
ends with what to put in the request, and the Django demo opens with the
real PROMPT.md that built it. "Decompose before you choose" and "you own the
request" are one idea, not two: decomposing is how you write the request.

Tick numbers ("deciding ticks") follow the web-stack-advisor skill's own
references/use-cases.md - the functionalities that *decide* the pick, not
every one an app touches (a labeling tool is "#7-10", even though it also
has a page and styling). Keep every slide on that convention; three
different counts for the same app was one of the review findings.
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
    # Optional relative column widths for a "table" slide (e.g. [0.6, 3, 5]);
    # empty = equal widths.
    col_weights: list[float] = field(default_factory=list)
    comp_left_header: str = ""
    comp_right_header: str = ""
    comp_rows: list[tuple[str, str, str]] = field(default_factory=list)
    footer: str = ""  # optional one-line conclusion under a table/comparison/ladder/code slide
    ladder_rungs: list[tuple[int, str, str, str]] = field(default_factory=list)
    quote_text: str = ""
    # "concept_pair" kind: a small illustrated two-box contrast (e.g. static vs
    # interactive), plus a closing one-line insight underneath both boxes.
    concept_left_label: str = ""
    concept_left_note: str = ""
    concept_right_label: str = ""
    concept_right_note: str = ""
    insight: str = ""
    # "cards" kind: a row of labeled cards, plus an optional closing "hook"
    # line underneath that reads as connected prose, not another card.
    cards: list[tuple[str, str]] = field(default_factory=list)
    hook: str = ""
    # "bullets_meter" kind: each item gets a 12-dot meter, one dot per row of
    # the functionality table, lit at the ticked positions (e.g. [3, 6]).
    # `bullets` (inherited above) still works for a plain closing line.
    meter_items: list[tuple[str, list[int]]] = field(default_factory=list)
    # "code" kind: 1-2 dark editor panels of (header, text). Lines starting
    # with `#`, or trailing "  # ..." comments, get highlighted - on these
    # slides the comments are the plain-language point next to the code.
    code_panels: list[tuple[str, str]] = field(default_factory=list)
    code_size: float = 13.0
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
                notes="Welcome. ~90 minutes, including four live demos. No web background "
                "assumed - that's the point. Questions welcome any time, or hold them - "
                "your call as speaker.",
                minutes=1,
            ),
            Slide(
                kind="bullets",
                title="What we'll cover",
                icon="🗺️",
                bullets=[
                    "Why a small web app helps a data project",
                    "You'll ask an LLM to build it: what your request has to decide",
                    "12 functionalities and a ladder: naming the lightest tool that works",
                    "Two gaps that quietly turn a demo into a product",
                    "Four live demos, including the written request that built one of them",
                ],
                notes="Set expectations: nobody here needs to learn to write web code. The "
                "talk is about asking for the right thing and being able to check what "
                "comes back.",
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
                kind="concept_pair",
                title="The moment every analysis hits",
                icon="👀",
                concept_left_label="A chart in a notebook",
                concept_left_note="Convinces you. It rarely convinces a colleague who's "
                "never going to open that notebook.",
                concept_right_label="A small web app",
                concept_right_note="Move a slider, filter to their own region, type a "
                "value - watch the answer change.",
                insight="That feels very different from a screenshot.",
                notes="Open with the everyday moment - this is the 'why' before any tooling talk.",
                minutes=2,
            ),
            Slide(
                kind="cards",
                title="Where this quietly pays off",
                icon="🎯",
                cards=[
                    ("Explore", "Makes exploring a dataset more interactive"),
                    ("Demonstrate", "Demonstrates a model as a live service"),
                    ("Prototype", "Prototypes a product idea before anyone spends "
                     "engineering time on it"),
                ],
                hook="You won't hand-write this app - you'll ask an LLM to build it. It builds "
                "whatever you ask for, so the hard part moves to the asking: which tool, and "
                "which rules.",
                notes="Land the hook: the LLM will build whatever you name. The costly mistake "
                "now happens earlier - asking for the wrong thing and finding out three days in.",
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    # The thesis, stated right after the hook rather than mid-talk: the
    # audience came for "an LLM builds it", so everything after this slide
    # is framed as vocabulary for writing that request.
    Section(
        name="Stay in the driver's seat",
        icon="🧠",
        slides=[
            Slide(
                kind="quote",
                title="Web is secondary here",
                icon="🧠",
                quote_text="An LLM makes writing the code cheap. That makes the request - which "
                "tool, and who may see or change what - the one part worth your care.",
                notes="This is the thesis of the whole talk. Say it plainly: you won't write "
                "this code, and you don't need to. Everything after this slide is the "
                "vocabulary for writing a request you can stand behind.",
                minutes=1.5,
            ),
            Slide(
                kind="bullets",
                title="Let the LLM write the code. You decide the rules.",
                icon="🎛️",
                bullets=[
                    "🚫 “Build me a labeling tool.” The LLM quietly picks the tool, what gets "
                    "saved, and who can see what",
                    "✅ “Use Django. Save each reviewer's labels. Reviewers see only the rows "
                    "assigned to them; admins see everything.” You decided - the LLM writes it",
                    "The rest of this talk gives you the words for the ✅ version",
                    "Skip it, and you end up with an app you can't explain, check, or safely change",
                ],
                notes="Both requests are one sentence long - the ✅ one isn't more technical, "
                "it's more decided. Promise: by the Django demo, you'll see the real request "
                "that built it.",
                minutes=2.5,
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
                "all, the pandas/model work that's already there. These are the names an LLM "
                "will throw at you - the map is where they fit.",
                minutes=2.5,
            ),
            Slide(
                kind="image_bullets",
                title="Three easy things to miss",
                icon="👓",
                image="field-map/field-map.png",
                bullets=[
                    "Tailwind (styling only) isn't a rival to Django or React - "
                    "it works with either.",
                    "React and Angular are alternatives to each other, and neither works "
                    "alone: both need a server behind them for data and login.",
                    "If you live in Python: Streamlit and Dash need zero JavaScript, "
                    "and for many tasks that's the whole answer.",
                ],
                notes="These cause most of the 'framework wars' confusion. Keeping the map on "
                "screen means nobody has to hold these names in their head.",
                minutes=2,
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
                    "Any web app is some mix of the same 12 functionalities.",
                    "Tick the ones yours needs. That list is the core of your request "
                    "to the LLM.",
                ],
                notes="This reframe is the whole method the rest of the talk builds on - and "
                "it's the step that turns a 🚫 request into a ✅ one.",
                minutes=1.5,
            ),
            Slide(
                kind="table",
                title="The 12 functionalities",
                icon="🧾",
                table_headers=["#", "Functionality", "What it means"],
                col_weights=[0.5, 3, 5],
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
                "a few (7-10) since they come back in the 'two gaps' section later. The "
                "numbers matter: every later slide refers to ticks by these numbers.",
                minutes=3,
            ),
            Slide(
                kind="bullets_meter",
                title="Worked examples",
                icon="✅",
                meter_items=[
                    ("Share a chart you're proud of  →  Presentation, Styling & layout, "
                     "Client interactivity", [1, 2, 3]),
                    ("Explore a dataset  →  Client interactivity, Server-side compute", [3, 6]),
                    ("A labeling tool  →  Persistence, Forms, Authentication, Authorization",
                     [7, 8, 9, 10]),
                ],
                bullets=[
                    "It's not how many ticks - it's how far right they sit. #6 needs a running "
                    "server; #7 onward needs a database and user accounts.",
                ],
                notes="The dots are the rows of the table you just saw, lit where ticked. "
                "'Explore' has fewer ticks than 'Share a chart' but needs a heavier tool, "
                "because #6 sits further right. Bridge straight into the ladder.",
                minutes=2.5,
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
                     "covers #1-3"),
                    (2, "Streamlit or Dash", "— explore data, or a tool for peers. Python only",
                     "adds #6: your Python runs each time someone interacts"),
                    (3, "Flask or FastAPI", "— serve a model or data to other programs",
                     "adds #4: an API other code can call"),
                    (4, "Django + a Tailwind kit", "— users, a database, forms, and an admin",
                     "adds #7-11: saved records, forms, logins, permissions"),
                    (5, "React or Angular over an API", "— only when the UI must feel like an app",
                     "adds no new tick: instant, keyboard-driven screens, at the cost of two projects"),
                ],
                footer="→ Start at the lowest rung that covers your furthest tick. Climb only when "
                "you can name what the rung below can't do.",
                notes="Read the footer out loud - it's the rule. Each rung's second line says "
                "which ticks it adds, so the ladder and the 12-row table are one picture. "
                "Background jobs (#12) aren't a rung - they're one of the two gaps coming up. "
                "Install commands live on the cheat-sheet at the end; the LLM will run them "
                "for you anyway.",
                minutes=3.5,
            ),
            Slide(
                kind="table",
                title="Applied to concrete cases",
                icon="🎯",
                table_headers=["Use case", "Who uses it", "Deciding ticks", "Pick"],
                col_weights=[3, 2.8, 1.7, 4.5],
                table_rows=[
                    ["Share a finished chart", "Anyone with the link", "#1-3", "Static HTML + D3"],
                    ["Explore a dataset", "You, or a data peer", "#3, #6", "Streamlit"],
                    ["Metrics dashboard", "Your team, every day", "#3, #6", "Dash"],
                    ["Demo a model", "Engineers first", "#4, #6",
                     "FastAPI (/docs is a free test form); add a Streamlit page for others"],
                    ["Labeling or review tool", "Several named people", "#7-10", "Django"],
                    ["Pipeline that ends in a page", "Anyone with the link", "#1, #3",
                     "Python writes JSON, D3 draws it"],
                ],
                footer="→ Same ticks, different pick? Who uses it breaks the tie: Streamlit is "
                "fastest for you, Dash gives a team more layout control.",
                notes="Walk the 'who uses it' column - it's what separates Streamlit from Dash, "
                "and why FastAPI's /docs is fine for engineers but not for a business user. "
                "Honest caveat: React+Tailwind is 2 projects, a build step, and auth you write "
                "yourself - climb there only for app-like UI needs.",
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
                    ["Django + Tailwind + daisyUI (a ready-made component kit)",
                     "A clean prototype with no React - the default"],
                    ["React + Tailwind + shadcn/ui",
                     "The best-looking and most customizable, highest setup cost"],
                    ["Dash + dash-bootstrap-components", "Tidy dashboards out of the box"],
                    ["Django admin", "Back-office screens for free"],
                ],
                footer="→ Name the kit in your request. Otherwise the LLM picks the look for you.",
                notes="Raw Tailwind gives utility classes, not a design - a component kit is "
                "what makes it look 'standard'. A peer forgives a plain page; a business user "
                "doesn't. The Django demo you'll see is the first row.",
                minutes=3,
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
                    "Authentication (#9) — who is this user?",
                    "Authorization (#10) — what may they do?",
                    "Data isolation (#10) — user A never sees user B's rows",
                    "Per-user state (#11) — remembering each user's own choices",
                    "Concurrent writes (#7) — two people editing the same row at once",
                    "Audit trail (#7) — who changed what, and when",
                    "Don't count on an LLM to add these unprompted: name each one you need.",
                ],
                notes="This and background jobs are the two gaps that bite the moment a demo "
                "becomes a product. The numbers show they're not new functionalities - they're "
                "what #7, #9-11 really mean once more than one person uses the app. None of "
                "this shows up in a 'build a dashboard in 10 minutes' tutorial.",
                minutes=2.5,
            ),
            Slide(
                kind="table",
                title="The tools differ sharply here",
                icon="⚖️",
                table_headers=["Tool", "What you get"],
                col_weights=[1.6, 5],
                table_rows=[
                    ["Django", "Auth, sessions, groups & permissions (role-based access) "
                     "- all built in"],
                    ["Flask", "Nothing built in - Flask-Login adds sessions; roles you write yourself"],
                    ["FastAPI", "Nothing built in - docs show an OAuth2/JWT pattern "
                     "(a token sent with every request) to write yourself"],
                    ["Streamlit", "Built-in OIDC login (“log in with Google/Microsoft”) "
                     "- but no roles, and cached data is shared by every user"],
                    ["Dash", "dash-auth: HTTP Basic only (a plain browser login popup, "
                     "no real session) - no logout"],
                    ["React, Angular", "Login screens only - real security lives on the server"],
                ],
                footer="→ Only Django ships real roles. With anything else, your request has to "
                "spell out who may see and change what.",
                notes="The rule to repeat: authorization is enforced on the server. Hiding a "
                "button in React protects nothing. Streamlit's cache being shared means one "
                "user's filtered data can be served to another if you cache per-user results.",
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
                title="A web page must answer in seconds. Retraining a model doesn't.",
                icon="⏳",
                ladder_rungs=[
                    (1, "Clicking 'Start' starts the job", "— the page gets a job id back at once", ""),
                    (2, "The job runs somewhere else", "— in a separate worker process", ""),
                    (3, "Its status is stored", "— a row in a table, updated as it runs", ""),
                    (4, "The page checks back", "— every few seconds, until it's done", ""),
                ],
                footer="→ Ask for this shape by name: “run it as a background job, and have the "
                "page poll its status.”",
                notes="The fix is always this same shape. This exact sequence reappears in "
                "demo 3.",
                minutes=2,
            ),
            Slide(
                kind="table",
                title="Surprising traps in background-job tooling",
                icon="🪟",
                table_headers=["Tool", "What it is", "Example", "Catch"],
                table_rows=[
                    ["FastAPI BackgroundTasks", "Runs a function after the response is sent, "
                     "same process", "background_tasks.add_task(fn)", "In-process - no "
                     "persistence or retries"],
                    ["Huey + SQLite", "A small task queue that keeps its queue in a SQLite "
                     "file - no separate server to run", "huey_consumer tasks.huey -k thread",
                     "Smaller ecosystem than Celery/RQ"],
                    ["RQ", "A job queue that needs a Redis server", "rq worker  (a separate process)",
                     "Uses os.fork - no native Windows support"],
                    ["Celery", "The most full-featured distributed task queue",
                     "celery -A proj worker", "Windows is unsupported by the project"],
                    ["Django's django.tasks (6.0)", "Django's own built-in task API",
                     "tasks.enqueue(my_task)", "Defines enqueue, ships no worker - you "
                     "still supply one"],
                ],
                footer="→ Default on a laptop: Huey + SQLite. Works on Windows, and plugs into "
                "Django too.",
                notes="Most of us are on Windows laptops - that's why the Windows column matters. "
                "Huey's Django integration is huey.contrib.djhuey. Watch for tutorials that say "
                "huey_consumer.py - the installed command is huey_consumer. We'll prove this "
                "live in a few minutes.",
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
                    "A long job re-scores the data with a new model (demo 3 shows that part "
                    "on its own).",
                    "Deciding ticks: #7-10, plus #12 for the re-scoring - a fair test of both stacks.",
                ],
                notes="Set up the comparison before showing the table.",
                minutes=1.5,
            ),
            Slide(
                kind="comparison",
                title="Django vs. FastAPI + React",
                icon="⚔️",
                comp_left_header="Django",
                comp_right_header="FastAPI + React",
                comp_rows=[
                    ("Login & users", "Built in", "You build it"),
                    ("Who-sees-what rule", "Inside the query, once per view",
                     "Repeated per route - 3 places to remember"),
                    ("Back-office screens", "Admin gives users & labels for free", "You build them"),
                    ("API for other systems", "Add Django REST Framework", "Built in, with automatic docs"),
                    ("Interface feel", "Page loads, a little JS", "Instant, app-like"),
                ],
                notes="For a small team, Django wins on time. FastAPI+React wins when the UI "
                "must be fast/keyboard-driven, another system needs the API, or a front-end "
                "engineer owns the UI. Both use Tailwind for styling.",
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
                kind="code",
                title="The request that built demo 1",
                icon="📝",
                code_panels=[
                    ("demos/labeling-django/PROMPT.md  (abridged; # notes added for this slide)",
                     "# The tool: Django - login and an admin screen come built in\n"
                     "Build a Django demo app at demos/labeling-django/ ...\n"
                     "\n"
                     "# What gets saved\n"
                     "Item:  text, model_label, model_score, assigned_to (FK to a user)\n"
                     "Label: item, reviewer, decision (correct / incorrect / unsure)\n"
                     "\n"
                     "# The who-sees-what rule, stated outright\n"
                     "queue(): Item.objects.filter(assigned_to=request.user)\n"
                     "         \"This one line is the whole point of the demo - comment it as such.\"\n"
                     "\n"
                     "# Use what the framework ships - don't hand-build it\n"
                     "Auth:  use django.contrib.auth.urls (login/logout for free)\n"
                     "Admin: register Item and Label - admins see everyone's labels\n"
                     "\n"
                     "# Ask for the test that would catch a leak\n"
                     "Tests: log in as one reviewer, request another reviewer's item id\n"
                     "       - expect 404."),
                ],
                footer="→ Every highlighted line is a decision made in plain words. The LLM "
                "wrote the code.",
                notes="This is the ✅ request from the start of the talk, for real. The full "
                "prompt is 64 lines, in demos/labeling-django/PROMPT.md; the highlighted "
                "comments are added here to show the decision behind each part. You don't need "
                "the technical names - the skill (later) helps with those. You do need the "
                "decisions: tool, what's saved, who sees what, and the test that proves it.",
                minutes=2.5,
            ),
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
                "bob/demo-bob-pw, admin/demo-admin-pw. Label a couple of items as alice AND bob "
                "before opening /admin/, or the Labels list is empty. Run commands: appendix. "
                "Fallback screenshots on the next slide.",
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
                notes="`Item.objects.filter(assigned_to=request.user)` is the ownership rule - "
                "the line the request asked for by name. Auth is django.contrib.auth.urls - "
                "zero hand-written view code.",
                minutes=2,
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
                    "The who-sees-what rule is written in three separate places - code in "
                    "two slides",
                ],
                notes="http://localhost:5173/ for the app, http://127.0.0.1:8000/docs for "
                "Swagger. Same credentials as the Django demo. Run commands: appendix.",
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
                notes="The payoff cost more code - next slide shows exactly where.",
                minutes=2,
            ),
            Slide(
                kind="code",
                title="The rule you own, in two codebases",
                icon="🔍",
                code_size=12.5,
                code_panels=[
                    ("Django · labeling/views.py",
                     "@login_required                 # login: built in\n"
                     "def queue(request):\n"
                     "    Item.objects.filter(assigned_to=request.user)\n"
                     "\n"
                     "@login_required\n"
                     "def label_item(request, item_id):\n"
                     "    get_object_or_404(Item, pk=item_id,\n"
                     "                      assigned_to=request.user)\n"
                     "\n"
                     "# The rule is part of each query itself -\n"
                     "# there's no separate guard to forget."),
                    ("FastAPI · api/deps.py + api/main.py",
                     "def get_owned_item(item_id, current_user, db):\n"
                     "    ...filter(Item.assigned_to_id == current_user.id)\n"
                     "\n"
                     "@app.get(\"/items\")                  # 1: a list can't\n"
                     "    ...filter(Item.assigned_to_id    #    reuse the guard\n"
                     "              == current_user.id)\n"
                     "\n"
                     "@app.get(\"/items/{item_id}\")        # 2: remember to\n"
                     "    item = Depends(get_owned_item)  #    attach it\n"
                     "\n"
                     "@app.post(\"/items/{item_id}/label\") # 3: ...and here\n"
                     "    item = Depends(get_owned_item)\n"
                     "\n"
                     "# plus security.py: JWT login, by hand"),
                ],
                footer="→ You don't have to write this line. You do have to know it exists - and "
                "ask for the test that proves it.",
                notes="Abridged from the two demos' real code. Same rule both times. In Django "
                "the rule sits inside the query; in FastAPI a route that forgets Depends(...) "
                "still runs fine and quietly returns someone else's rows. Both demos ship a test "
                "that logs in as alice and asks for bob's item - that test is what you ask the "
                "LLM for.",
                minutes=2.5,
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
                    "The guarantee: a reviewer never sees another reviewer's rows - both "
                    "stacks deliver it",
                    "Django: less code, an admin for free, the rule inside one query per view",
                    "FastAPI + React: more code, but an instant, keyboard-driven feel and a "
                    "separate API other systems can call",
                    "Start with Django; add an API and React later without throwing away the "
                    "data model",
                    "Either way, the LLM wrote most of the code. The request is where the two "
                    "diverged.",
                ],
                notes="Close the loop on the comparison before the next demo. If someone asks "
                "'can't I have both?' - yes, see the backup slide in the appendix.",
                minutes=2,
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
                    "Click 'Start queued rescore' — a job id appears instantly, and progress "
                    "climbs 0 → 30 rows while the page stays responsive",
                    "Huey + SQLite: no Redis, nothing to install beyond Python — verified "
                    "on Windows",
                    "Built on FastAPI here; the same Huey setup plugs into Django",
                ],
                notes="http://127.0.0.1:8000/. The blocking button is the whole point: there's "
                "nothing to screenshot while it hangs, and that's exactly the problem. Run "
                "commands: appendix (the worker needs -k thread on Windows).",
                minutes=3,
            ),
            Slide(
                kind="comparison",
                title="What's happening underneath",
                icon="🔧",
                comp_left_header="Blocking",
                comp_right_header="Queued (Huey + SQLite)",
                comp_rows=[
                    ("Where the work runs", "Inside the page's own request, same process",
                     "A separate Huey worker process"),
                    ("What comes back immediately", "Nothing - the connection just waits",
                     "A job id, instantly"),
                    ("How progress is tracked", "It isn't - no signal until it finishes "
                     "or times out", "A status row in SQLite, updated as it runs"),
                    ("What the page does", "Sits there, disabled, hoping",
                     "Polls the status every few seconds"),
                ],
                notes="This is the same 4-step shape from the earlier background-jobs slide "
                "(start / run elsewhere / store status / check back), now with the real "
                "names filled in.",
                minutes=1.5,
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
                minutes=2,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    # The skill is introduced *before* the PSA map demo, because that demo
    # is the skill running as a web page - showing it first left "the
    # skill" undefined for three slides.
    Section(
        name="Try it",
        icon="🛠️",
        slides=[
            Slide(
                kind="bullets",
                title="Try it: a skill file",
                icon="🛠️",
                bullets=[
                    "The whole method from this talk, packaged as a Markdown file your AI "
                    "assistant loads",
                    "Describe your app idea in plain words → it ticks the 12 functionalities "
                    "and names the lightest stack",
                    "Flags the two gaps (multi-user, background jobs) before anything is built",
                    "What it gives back is the raw material for a ✅ request: which tool, "
                    "which rules, which gaps",
                    "Drop the folder into .claude/skills/ of any project",
                ],
                notes="This is the 'go try it yourself' moment - and the answer to 'but I don't "
                "know the technical names': the skill supplies them.",
                minutes=2,
            ),
            Slide(
                kind="table",
                title="Trigger it from VS Code Chat",
                icon="💬",
                table_headers=["Where", "How"],
                table_rows=[
                    ["Claude Code (CLI or VS Code extension)", "Type / to see it listed, "
                     "or just describe your use case - it auto-loads from its description"],
                    ["GitHub Copilot Chat (VS Code)", "Same / menu - Agent Skills is an "
                     "open standard both read"],
                    ["Either one", "Drop the folder in .claude/skills/ (or .github/skills/) "
                     "- no conversion needed"],
                ],
                footer="→ One skill folder, not one per assistant.",
                notes="Worth saying explicitly: people assume Claude-authored tooling is "
                "Claude-only. Since VS Code's Agent Skills became an open standard "
                "(agentskills.io), it isn't - Copilot Chat reads the same .claude/skills/ "
                "folder.",
                minutes=1,
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
                    "Built on the skill's own advice: static HTML + D3 + Tailwind - rung 1, "
                    "because that's all this use case needs",
                    "27 PSA container terminals worldwide, cross-filtered map + charts",
                    "It shows its own working: the 12-tick verdict for this app, and an "
                    "advisor you can try live",
                ],
                notes="Served at whatever URL `npm run serve -- demos/psa-terminal-map` prints "
                "(typically http://localhost:8080). The page is in three acts: the map, why "
                "this stack, and try the advisor. Run commands: appendix.",
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
                minutes=2,
            ),
            Slide(
                kind="image_pair",
                title="The skill, showing its work",
                icon="🔬",
                image_left="psa-map/build-trail.png",
                caption_left="The 12-functionality verdict for this app",
                image_right="psa-map/live-advisor.png",
                caption_right="Try the advisor on your own use case - same logic, tested",
                notes="The point: the skill's advice is a function you can run, not an "
                "opinion - asserted by a test suite against all 8 documented use cases.",
                minutes=2.5,
            ),
        ],
    ),
    # ------------------------------------------------------------------
    Section(
        name="Close",
        icon="🎬",
        slides=[
            Slide(
                kind="table",
                title="Setup cheat-sheet",
                icon="📋",
                table_headers=["Tool", "Install"],
                table_rows=[
                    ["Static HTML + D3", "Nothing — or npm install http-server to preview locally"],
                    ["Streamlit", "pip install streamlit"],
                    ["Dash", "pip install dash"],
                    ["Flask", "pip install flask"],
                    ["FastAPI", "pip install fastapi uvicorn"],
                    ["Django", "pip install django  →  django-admin startproject"],
                    ["React (Vite)", "npm create vite@latest"],
                    ["Tailwind, no Node", "standalone CLI, or a CDN link (hosted script tag)"],
                    ["daisyUI", "npm package, or paired with Tailwind's CDN link"],
                ],
                notes="Flash it, don't read it - the LLM will usually run these for you, and "
                "it's all in the repo. Honest caveat: everything here assumes it runs on your "
                "own machine. Deployment is a separate decision.",
                minutes=1,
            ),
            Slide(
                kind="bullets",
                title="Takeaways",
                icon="🎬",
                bullets=[
                    "You'll ask an LLM to build it. The request - which tool, which rules - is "
                    "the part you own",
                    "Decompose before you choose: tick the 12, then start at the lowest rung "
                    "that covers your furthest tick",
                    "Multi-user and background jobs are where a demo quietly becomes a "
                    "product. Name them in your request",
                    "Audience sets the finish: a peer forgives a plain page, a business user "
                    "doesn't. Name a component kit",
                    "Climbing later is normal: Django, then an API, then React, keeping the "
                    "data model. Outgrowing Streamlit means a rebuild - fine, the prototype "
                    "was cheap",
                ],
                notes="Close on the throughline: decompose before you choose - that's how you "
                "write the request. (Title is deliberately count-agnostic - it's been 'three "
                "lessons' before and grown; don't re-name it back to a number.)",
                minutes=2.5,
            ),
            Slide(
                kind="bullets",
                title="Everything from this talk lives here",
                icon="📦",
                bullets=[
                    "github.com/hovinh/web-development-learning-lab",
                    ".claude/skills/web-stack-advisor/ — the skill: drop it into any project",
                    "demos/ — the four demos, each with the PROMPT.md that built it and a "
                    "README to run it",
                    "blog/web-dev-for-data-people/ — the post this talk is based on, and this "
                    "deck",
                ],
                notes="Give people a moment to note the URL down before moving to questions. "
                "The repo root is a wider learning lab - point them at these three folders.",
                minutes=1,
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
    # ------------------------------------------------------------------
    # Appendix: not part of the planned run of show (minutes=0, so they
    # don't count toward the 90-minute budget). The "Run it" slides were
    # moved here from before each demo: they're instructions for whoever
    # runs the demo, not something the audience needs mid-talk, and they
    # cost ~3.5 minutes of flow. Kept as slides (not only READMEs) so the
    # presenter can pull one up if a demo needs restarting on stage.
    Section(
        name="Appendix",
        icon="🎒",
        slides=[
            Slide(
                kind="bullets",
                title="Backup: can I get the best of both worlds?",
                icon="🎒",
                bullets=[
                    "Yes - and it's the normal path, not a special trick.",
                    "Start Django. Add Django REST Framework once another system (or a "
                    "future React frontend) needs an API - the data model doesn't change.",
                    "Put React (or just htmx/Alpine.js, no build step) in front of only "
                    "the screens that must feel instant - label review, not the admin.",
                    "django-ninja is a lighter, FastAPI-flavored alternative to DRF if "
                    "you want typed, automatic-docs endpoints without leaving Django.",
                    "What you don't get: two frameworks' auth merged into one - you "
                    "still pick a single system of record for who's logged in.",
                ],
                notes="Only show this if asked - it's the natural 'can't I have both' "
                "follow-up. The honest limit: authentication still has to live in one place.",
                minutes=0,
            ),
            Slide(
                kind="ladder",
                title="Run it: Django demo",
                icon="⌨️",
                ladder_rungs=[
                    (1, "Activate the venv", "— so python resolves to the repo's shared packages",
                     ".venv\\Scripts\\Activate.ps1  (bash: source .venv/Scripts/activate)"),
                    (2, "Migrate", "— creates the database tables from Django's models",
                     "python demos/labeling-django/manage.py migrate"),
                    (3, "Seed demo data", "— creates alice/bob/admin and their sample tickets",
                     "python demos/labeling-django/manage.py seed_demo"),
                    (4, "Start the server", "— serves the app locally",
                     "python demos/labeling-django/manage.py runserver"),
                    (5, "Open it", "— alice/bob/admin, password demo-<name>-pw",
                     "http://127.0.0.1:8000/"),
                ],
                notes="All from the repo root. Nothing to configure by hand beyond these steps.",
                minutes=0,
            ),
            Slide(
                kind="ladder",
                title="Run it: FastAPI + React demo",
                icon="⌨️",
                ladder_rungs=[
                    (1, "Seed demo data", "— terminal 1, .venv active - creates alice/bob/admin",
                     "python demos/labeling-fastapi-react/api/seed.py"),
                    (2, "Start the API", "— terminal 1 - serves FastAPI, docs included",
                     "uvicorn main:app --reload --app-dir demos/labeling-fastapi-react/api"),
                    (3, "Install + start the front end", "— terminal 2 - npm install once, "
                     "then the dev server",
                     "cd demos/labeling-fastapi-react/web  →  npm install  →  npm run dev"),
                    (4, "Open it", "— same alice/bob/admin credentials as the Django demo",
                     "App: http://localhost:5173/   API docs: http://127.0.0.1:8000/docs"),
                ],
                notes="Two terminals, both starting at the repo root; terminal 2 then cds into "
                "the web/ folder.",
                minutes=0,
            ),
            Slide(
                kind="ladder",
                title="Run it: long-jobs demo",
                icon="⌨️",
                ladder_rungs=[
                    (1, "Start the API", "— terminal 1, .venv active - serves FastAPI",
                     "uvicorn app:app --reload --app-dir demos/long-jobs"),
                    (2, "Start the worker", "— terminal 2, .venv active - runs the queued jobs; "
                     "-k thread is required on Windows",
                     "cd demos/long-jobs  →  huey_consumer tasks.huey -k thread"),
                    (3, "Open it", "— no migrate/seed step needed; the jobs table is "
                     "created automatically on startup",
                     "http://127.0.0.1:8000/"),
                ],
                notes="Two terminals, both starting at the repo root; terminal 2 then cds into "
                "demos/long-jobs.",
                minutes=0,
            ),
            Slide(
                kind="ladder",
                title="Run it: PSA map demo",
                icon="⌨️",
                ladder_rungs=[
                    (1, "Install once", "— only if node_modules/ is absent; no .venv needed",
                     "npm install"),
                    (2, "Serve it", "— D3 needs a real server, not file://",
                     "npm run serve -- demos/psa-terminal-map"),
                    (3, "Open it", "— the URL http-server prints, in your browser",
                     "e.g. http://localhost:8080"),
                ],
                notes="Pure Node/static demo, run from the repo root.",
                minutes=0,
            ),
        ],
    ),
]


def total_minutes() -> float:
    return sum(slide.minutes for section in SECTIONS for slide in section.slides)


def total_slides() -> int:
    return sum(len(section.slides) for section in SECTIONS)
