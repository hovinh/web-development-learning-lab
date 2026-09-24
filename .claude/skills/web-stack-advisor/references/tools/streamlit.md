# Streamlit

**Status: written from documentation and general knowledge; not verified by running.**

## What it is for

The fastest path from a DataFrame or model to an interactive page, in pure Python. You
write a top-to-bottom script; widgets rerun it on every interaction. Best for data
exploration and tools for peers. Weaker for custom layout, multi-page product UX and
multi-user products.

## Minimal example

```python
# pip install streamlit pandas
import pandas as pd
import streamlit as st

st.title("Sales explorer")

# st.cache_data memoises on the function arguments and is SHARED ACROSS ALL USERS.
@st.cache_data
def load(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

df = load("sales.csv")
region = st.selectbox("Region", sorted(df["region"].unique()))
st.bar_chart(df[df["region"] == region].set_index("month")["revenue"])
```

Run locally: `streamlit run app.py`.

## Gotchas

- **The script reruns top to bottom on every interaction.** Keep expensive work behind
  `st.cache_data` (data) or `st.cache_resource` (models, connections).
- Caches are shared across users. Never cache something specific to one user unless
  the user is a function argument. `st.session_state` is per browser session.
- Login: built-in OIDC (`st.login()`, `st.user`) configured in `secrets.toml`, with
  providers such as Google, Microsoft, Okta (verified Sept 2026). There is no role
  system; compare `st.user.email` against your own list.
- Long jobs: do not block the script. Use a thread or subprocess and poll.
- Styling is limited to themes and a few options; expect the default look.
