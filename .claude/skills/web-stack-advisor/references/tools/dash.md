# Dash (Plotly)

**Status: written from documentation and general knowledge; not run in the user's repo.**

## What it is for

Python dashboards built on Flask, React and Plotly. You declare a layout, then write
**callbacks** that map inputs (dropdowns, sliders) to outputs (figures, tables). More
explicit than Streamlit, so more layout and state control; more code for the same page.
Best for peer or business dashboards that need to look tidy.

## Minimal example

```python
# pip install dash pandas plotly
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

df = pd.read_csv("sales.csv")

app = Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(sorted(df["region"].unique()), df["region"].iloc[0], id="region"),
    dcc.Graph(id="chart"),
])


# A callback: whenever the dropdown value changes, rebuild the figure.
@app.callback(Output("chart", "figure"), Input("region", "value"))
def update(region):
    subset = df[df["region"] == region]
    return px.bar(subset, x="month", y="revenue")


if __name__ == "__main__":
    app.run(debug=True)
```

Run locally: `python app.py`, then open `http://127.0.0.1:8050`.

## Gotchas

- `app.run` is the current name; older tutorials use `app.run_server`.
- Callback state lives in the browser; module-level globals are shared by all users.
- Auth: `dash-auth` gives HTTP Basic Auth only (no logout button). For real login use
  Flask-Login or SSO (Dash Enterprise offers it). See `../multi-user.md`.
- For a cleaner look, use `dash-bootstrap-components`.
