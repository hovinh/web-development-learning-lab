# FastAPI

**Status: written from documentation and general knowledge; not run in the user's repo.**

## What it is for

A typed Python HTTP API. Request and response shapes are declared with Pydantic models,
and FastAPI generates validation plus an interactive docs page at `/docs` (Swagger UI)
and `/redoc`. Best for serving a model or data, and for the back end of a React/Angular
front end. Compared with Flask: more structure and type checking up front, async
support, and automatic docs.

## Minimal model-serving example

```python
# pip install fastapi uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Features(BaseModel):
    # Pydantic validates the JSON body against these fields and types.
    age: float
    income: float


class Prediction(BaseModel):
    score: float


@app.post("/predict", response_model=Prediction)
def predict(features: Features) -> Prediction:
    # Replace with a real model call. A plain `def` runs in a worker thread,
    # which is right for blocking pandas/sklearn code.
    score = 0.01 * features.age + 0.00001 * features.income
    return Prediction(score=score)
```

Run locally: `uvicorn main:app --reload`, then open `http://127.0.0.1:8000/docs` to try
the endpoint from the browser.

## Gotchas

- Use `def` (not `async def`) for CPU-bound or blocking code, or it blocks the event loop.
- `BackgroundTasks` is for tiny post-response work; it has no persistence or retries.
  See `../background-jobs.md`.
- No auth is built in. The docs show an OAuth2 + JWT pattern; `fastapi-users` is in
  maintenance mode (Sept 2026). See `../multi-user.md`.
- To let a browser page on another origin call it, add `CORSMiddleware`.
