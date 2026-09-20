# What "multi-user" means

A product with several users has to solve all of these:

1. **Authentication.** Verifying who someone is: login, password hashing, sessions or tokens.
2. **Authorization.** What each user may do: roles (admin vs viewer) and per-action permissions.
3. **Data ownership and isolation.** User A must never see user B's rows. Every query is
   filtered by owner (or by team/tenant, if there are organisations).
4. **Per-user state.** Saved filters, preferences, history, uploaded files.
5. **Concurrency.** Two people writing at once. SQLite is fine locally; a real
   multi-user app usually needs Postgres.
6. **Auditability.** Who changed what, and when.

Even locally this can be tested: create several accounts and switch browsers.

## Support by tool

| Tool | Authentication | Authorization / isolation |
|---|---|---|
| **Django** | Built in (login pages, sessions, password hashing) | Groups and permissions built in; you still write the ownership filter |
| **FastAPI** | Nothing built in. The official docs show an OAuth2 + JWT pattern. `fastapi-users` exists but is in maintenance mode (verified Sept 2026), so prefer the documented pattern or check its successor | Hand-written dependencies per endpoint |
| **Flask** | Add Flask-Login or a JWT extension | Hand-written |
| **React / Angular** | Client side only (login screens, route guards). Depend on a backend for real security | Client checks are cosmetic |
| **Streamlit** | Built-in OIDC login (`st.login`, `st.user`) against providers such as Google, Microsoft, Okta | No roles. You compare `st.user.email` to your own allow-list |
| **Dash** | `dash-auth`: HTTP Basic Auth only (no logout); richer needs mean Flask-Login or SSO | Hand-written |
| **Static / D3** | None | None |

## Rules of thumb

- Enforce authorization on the **server**. A hidden button is not security.
- Put the ownership filter in one place (a Django model manager or mixin, a FastAPI
  dependency) so one forgotten `.filter()` does not leak data.
- Streamlit's `st.cache_data` and `st.cache_resource` are **shared across all users**.
  Never cache something tied to one user without passing the user as an argument.
  `st.session_state` is per browser session.
- Test isolation explicitly: log in as user A, request user B's record id, expect 403/404.
