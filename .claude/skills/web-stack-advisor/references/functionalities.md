# The 12 web functionalities

Break any use case into these. Each row says what it means, and what to reach for.

| # | Functionality | What it means | Lightest tool | Heavier option |
|---|---|---|---|---|
| 1 | Presentation | Show static content | HTML/CSS | Any framework template |
| 2 | Styling and layout | Make it look decent and consistent | Tailwind + component kit | Plain CSS, Bootstrap |
| 3 | Client interactivity | Filters, tooltips, drill-down without a page reload | D3 or vanilla JS; Streamlit/Dash if you want no JS | React, Angular |
| 4 | API: providing | Expose data or a model over HTTP | FastAPI or Flask | Django REST Framework |
| 5 | API: consuming | A page or service calls an API | `fetch` in JS | React data hooks, Angular HttpClient |
| 6 | Server-side compute | Run pandas or a model per request | Streamlit/Dash, or any Python web framework | Same, plus a job queue (#12) |
| 7 | Persistence | Save records | SQLite via Django ORM or SQLAlchemy | Postgres |
| 8 | Forms and CRUD | Validated create/edit/delete | Django forms + admin | Pydantic + React forms |
| 9 | Authentication | Who is this user? | Django built-in; Streamlit `st.login` | FastAPI OAuth2/JWT, Flask-Login |
| 10 | Authorization | What may they do or see? | Django groups/permissions | Hand-written checks per endpoint |
| 11 | Session and state | Remember a user's choices | Django sessions, Streamlit `session_state` | React state, a database |
| 12 | Background and long jobs | Work that outlives one HTTP request | See `background-jobs.md` | Task queue + worker |

## How to use the table

1. Tick the rows the use case genuinely needs. Most peer-facing tools need only 3 and 6.
2. Each extra tick from 7 onward (persistence, forms, auth) is a reason to move up the
   ladder toward Django, because it ships all of them together.
3. Ticks at 4 and 5 together (a front end calling your own API) mean two projects. Only
   accept that cost if the UI is app-like or another system needs the API.

## Not covered (mention as gaps when they come up)

- Real-time updates (websockets, server-sent events).
- File upload and large-file handling.
- Email/notifications.
- Observability (logging, monitoring).
