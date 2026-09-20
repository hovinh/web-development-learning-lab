---
layout: post
title: "Web Dev for Data Scientists: A Survey of Options and a Way to Choose"
description: >
  The web development world is huge, and an LLM can write the boilerplate for any of it. What it cannot do for you is choose. This post surveys the popular options, breaks any use case into twelve functionalities, and ends with a skill file you can hand to your own assistant.
author: author1
comments: true
---

**Prerequisite**: Python and pandas, a rough idea of what an HTTP API is, no web development background needed

- [Why a Data Scientist Should Care](#why-a-data-scientist-should-care)
- [A Field Too Wide to Browse](#a-field-too-wide-to-browse)
- [Ask What the App Must Do, Not Which Framework](#ask-what-the-app-must-do-not-which-framework)
- [From Functionalities to a Stack](#from-functionalities-to-a-stack)
- [Pretty Enough for Business Users](#pretty-enough-for-business-users)
- [Two Gaps That Bite Later](#two-gaps-that-bite-later)
- [Two Real Stacks, One Problem](#two-real-stacks-one-problem)
- [Try It: A Skill File](#try-it-a-skill-file)
- [Summary](#summary)

## Why a Data Scientist Should Care

Most of my analysis ends the same way: someone needs to *see* it. A chart in a notebook convinces me, but it rarely convinces a stakeholder who will not open a notebook. A small web app does. It lets a colleague move a slider, filter a region, or feed a value to a model and watch the answer change. That is a different quality of argument from a screenshot.

The same skill helps three other jobs I keep meeting: exploring a dataset interactively, demonstrating a model as a live service, and prototyping a product idea before anyone commits engineering time to it.

The reason this is easier now than it used to be is that an LLM can write most of the boilerplate. Ask for a form, a route, or a chart callback and you get working code. But that shifts the difficulty rather than removing it. The assistant will happily build whatever you name, so the expensive mistake moves upstream: choosing the wrong tool for the job, and only finding out three days in. Choosing well is now the part that is still yours.

## A Field Too Wide to Browse

Search for "how to build a web app" and you will meet dozens of tools with overlapping claims. It helps to sort them by the layer they occupy, because most of the confusion comes from comparing tools that are not competitors.

| Layer | Popular options |
|---|---|
| Static front end | HTML/CSS/JavaScript, jQuery, D3 |
| Styling | Plain CSS, **Tailwind CSS** |
| Single-page app (SPA) front end | React, Angular |
| Python HTTP API | Flask, **FastAPI** |
| Full-stack Python framework | Django |
| Python-native UI | **Streamlit**, **Dash** |

Two things in this table are easy to miss. First, Tailwind is not a rival to Django or React. It only styles, so it combines with any row. Second, React and Angular sit on the same rung. Both are front ends that still need something else to supply data and handle login. They are not alternatives to Flask or Django.

For a data scientist, the Python-native rows deserve special attention. Streamlit and Dash let you stay in Python, with no JavaScript at all, and for many tasks that is the whole answer.

## Ask What the App Must Do, Not Which Framework

The way out of the option overload is to stop asking "which framework?" and start asking "what does this app have to do?" Any web app is some combination of the same twelve capabilities.

| # | Functionality | What it means |
|---|---|---|
| 1 | Presentation | Show static content |
| 2 | Styling and layout | Make it look decent and consistent |
| 3 | Client interactivity | Filters and tooltips without a page reload |
| 4 | API: providing | Expose data or a model over HTTP |
| 5 | API: consuming | A page or service calls an API |
| 6 | Server-side compute | Run pandas or a model per request |
| 7 | Persistence | Save records |
| 8 | Forms and CRUD | Validated create, edit and delete |
| 9 | Authentication | Who is this user? |
| 10 | Authorization | What may they do or see? |
| 11 | Session and state | Remember a user's choices |
| 12 | Background and long jobs | Work that outlives one request |

Take a use case and tick the rows it needs. A chart you want to share needs 1, 2 and 3. A dataset explorer needs 3 and 6. A labeling tool needs 7 through 10 on top. The number of ticks is the signal. Each extra tick from persistence onward is a reason to reach for a heavier tool, because that is where a framework that ships several of them together starts paying for itself.

## From Functionalities to a Stack

Once you have the ticks, pick the *lightest* tool that covers them. I think of it as a ladder, and you should only climb when a rung fails you.

> Start at the lowest rung that covers every functionality you ticked. Climb only when you can name the specific thing the rung below cannot do.

1. **Static HTML and D3**: show a finished result. No server at all.
2. **Streamlit or Dash**: explore data, or build a tool for peers. Python only.
3. **Flask or FastAPI**: serve a model or data over HTTP.
4. **Django with a Tailwind kit**: users, a database, forms, and an admin. A multi-user prototype.
5. **React or Angular over an API**: only when the UI is genuinely app-like.

Applied to concrete cases:

| Use case | Functions | Pick |
|---|---|---|
| Share a finished chart | 1, 2, 3 | Static HTML and D3 |
| Explore a dataset | 3, 6 | Streamlit |
| Peer dashboard | 3, 6 | Dash |
| Demo a model | 4, 6 | FastAPI, whose `/docs` page is a free test form |
| Labeling or review tool | 7 to 10 | Django |
| Pipeline that ends in a page | 1, 3 | Python writes JSON, D3 renders it |

Your audience shifts the pick too. A raw Streamlit page is fine for fellow data scientists and can look unfinished to a manager. If the people using the tool are not technical, they judge by polish, and that pushes you toward the next section.

There is an honest caveat about the top rung. React with Tailwind is a very common combination and a good one, but it is two projects (a front end and a back end), a build step, and authentication you write yourself. Django gives you the whole thing in one project. I would choose the SPA when the interface needs instant, keyboard-driven or drag-and-drop behaviour, or when other systems also need the API, and not before.

## Pretty Enough for Business Users

Raw Tailwind gives you utility classes, not a design. To get a look that people recognise as standard, add a **component kit** on top: ready-made buttons, cards, tables and navigation bars.

| Option | Good for |
|---|---|
| Django templates, Tailwind and daisyUI | A clean prototype with no React. My default suggestion |
| React, Tailwind and shadcn/ui | The best-looking and most customisable, at the highest setup cost |
| Dash with dash-bootstrap-components | Tidy dashboards out of the box |
| Django admin | Back-office screens for free |

Tailwind normally needs Node to compile, which is a barrier if you are a Python person. It has a standalone command-line build that needs no Node<sup><a href="https://tailwindcss.com/blog/standalone-cli">(1)</a></sup>, and you can even install it through `pip`. daisyUI 5 is designed for Tailwind 4<sup><a href="https://daisyui.com/docs/v5/">(2)</a></sup>. I have not verified running daisyUI with the standalone build and no npm at all, so treat that combination as something to test rather than a promise.

## Two Gaps That Bite Later

Two topics rarely appear in "build a dashboard in ten minutes" tutorials, and both arrive the moment a demo becomes a product.

### Multi-user

A tool with several users has to solve six things. **Authentication** verifies who someone is. **Authorization** decides what each user may do. **Data isolation** makes sure user A never sees user B's rows. There is also per-user state, concurrent writes (SQLite is fine locally, and a real app usually wants Postgres), and an audit trail.

The tools differ sharply here:

| Tool | What you get |
|---|---|
| Django | Authentication, sessions, groups and permissions, all built in |
| FastAPI | Nothing built in. The docs show an OAuth2 and JWT pattern. The popular `fastapi-users` package is in maintenance mode<sup><a href="https://github.com/fastapi-users/fastapi-users">(3)</a></sup> |
| Streamlit | Built-in OpenID Connect login with providers such as Google or Microsoft<sup><a href="https://docs.streamlit.io/develop/api-reference/user/st.login">(4)</a></sup>, but no roles |
| Dash | `dash-auth` offers HTTP Basic Auth only, with no logout<sup><a href="https://dash.plotly.com/authentication">(5)</a></sup> |
| React, Angular | Login screens only. Real security lives on the server |

The rule I keep repeating to myself: **authorization is enforced on the server.** Hiding a button in React protects nothing. And a Streamlit detail worth knowing early: its data cache is shared across all users, so caching something tied to one person hands it to the next.

### Long-running jobs

A web request has to answer in seconds. Retraining a model does not. The shape of the fix is always the same: the request starts the job and returns at once, the job runs somewhere else, its status is stored, and the page checks back every few seconds.

The tooling has surprising traps, especially on Windows:

| Need | Tool | Catch |
|---|---|---|
| Tiny work after a response | FastAPI `BackgroundTasks` | Runs in the web process, no persistence or retries<sup><a href="https://fastapi.tiangolo.com/tutorial/background-tasks/">(6)</a></sup> |
| Simple queue, no Redis | Huey with SQLite storage<sup><a href="https://huey.readthedocs.io/en/1.11.0/sqlite.html">(7)</a></sup> | Smaller ecosystem |
| Simple queue with Redis | RQ | Uses `os.fork`, so no native Windows support<sup><a href="https://github.com/rq/rq/issues/226">(8)</a></sup> |
| Full-featured queue | Celery | Windows is unsupported by the project<sup><a href="https://celery.school/celery-on-windows">(9)</a></sup> |
| Django's own API | `django.tasks` in Django 6.0 | Defines how to enqueue, but ships no worker and no retries<sup><a href="https://docs.djangoproject.com/en/6.0/topics/tasks/">(10)</a></sup> |

My default for a data scientist on a laptop: polling plus a job-status table, and Huey with SQLite for the worker. Reach for Celery, or for a pipeline tool such as Prefect or Dagster, when you actually need retries and scheduling.

## Two Real Stacks, One Problem

To make the trade-offs concrete, take a labeling tool. Reviewers label rows and the results are saved. Admins see everyone's labels and manage users. A reviewer sees only the rows assigned to them. A long job re-scores the data with a new model.

That touches almost all twelve functionalities, so it is a fair test. Compare Django (one project) with FastAPI, React and Tailwind (two projects):

| Concern | Django | FastAPI, React, Tailwind |
|---|---|---|
| Login and users | Built in | You build it |
| Ownership filtering | A queryset filter, one line | A check in every endpoint |
| Forms and validation | Automatic | Pydantic plus client-side form state |
| Back-office screens | The admin gives users and labels for free | You build them |
| API for other systems | Add Django REST Framework | Built in, with automatic docs |
| Interface feel | Page loads, plus a little JavaScript | Instant, app-like |

For a small team, Django wins on time: the admin alone covers user management and label export. FastAPI and React win when the labeling interface has to be fast and keyboard-driven, when another system also needs the API, or when a front-end engineer will own the UI. If you start with Django and outgrow it, you can add an API later and put React in front without throwing away the data model.

## Try It: A Skill File

Reading a survey is not the same as using one. So I turned this whole structure into a **skill**: a Markdown file that an AI coding assistant loads when you describe an app idea. It asks about your audience and whether users log in, breaks the idea into the twelve functionalities, and recommends the lightest tool for each, while flagging the gaps above.

The head of the file looks like this:

```yaml
---
name: web-stack-advisor
description: Recommend the lightest web tooling for a data scientist's use case (share a chart, explore data, serve a model, labeling tool, dashboard, multi-user product prototype). Breaks the use case into 12 web functionalities and maps each to a tool. Use when the user asks "what should I build this with" or describes an app idea for a demo, data exploration or product prototype.
---
```

Download the skill from <a href="TODO-GITHUB-URL-OF-SKILL">TODO-GITHUB-URL-OF-SKILL</a> and drop the folder into the `.claude/skills/` directory of any project, then describe an app you have been meaning to build. The reference notes it ships with are written from documentation, and I have not run every starter snippet myself, so treat them as a first draft to check.

One limit to be upfront about: everything here assumes the app runs on your own machine. Deployment is a separate decision that depends on your team, but if your end users are business people, "it works on my laptop" will not survive contact with them.

## Summary

The throughline is to **decompose before you choose**. Web development is not one decision but twelve small ones, and most tools only cover some of them. Once a use case is written as a set of functionalities, the tool choice mostly falls out: the fewest tools that cover every tick, starting from the lightest rung and climbing only for a reason you can name.

Three lessons recur. Audience matters as much as architecture, because a peer forgives a plain page and a business user does not. Multi-user concerns and long-running jobs are the two places where a demo silently becomes a product, and each tool handles them very differently. And an LLM makes writing the code cheap, which makes the choice of what to write the one part worth your careful attention.

---

(1) <a href="https://tailwindcss.com/blog/standalone-cli">https://tailwindcss.com/blog/standalone-cli</a>

(2) <a href="https://daisyui.com/docs/v5/">https://daisyui.com/docs/v5/</a>

(3) <a href="https://github.com/fastapi-users/fastapi-users">https://github.com/fastapi-users/fastapi-users</a>

(4) <a href="https://docs.streamlit.io/develop/api-reference/user/st.login">https://docs.streamlit.io/develop/api-reference/user/st.login</a>

(5) <a href="https://dash.plotly.com/authentication">https://dash.plotly.com/authentication</a>

(6) <a href="https://fastapi.tiangolo.com/tutorial/background-tasks/">https://fastapi.tiangolo.com/tutorial/background-tasks/</a>

(7) <a href="https://huey.readthedocs.io/en/1.11.0/sqlite.html">https://huey.readthedocs.io/en/1.11.0/sqlite.html</a>

(8) <a href="https://github.com/rq/rq/issues/226">https://github.com/rq/rq/issues/226</a>

(9) <a href="https://celery.school/celery-on-windows">https://celery.school/celery-on-windows</a>

(10) <a href="https://docs.djangoproject.com/en/6.0/topics/tasks/">https://docs.djangoproject.com/en/6.0/topics/tasks/</a>
