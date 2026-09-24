# Shared sample data

`predictions.json` is a fixed set of 30 rows shared by `../labeling-django/` and
`../labeling-fastapi-react/`. See `../README.md` for why it is deliberately shared instead of
each demo generating its own (Demos 1 and 2 are only a fair head-to-head if they label
byte-identical rows).

Each row is one model prediction over a support ticket, the blog's "is this prediction
correct?" scenario:

```json
{ "id": 1, "text": "Card was charged twice...", "model_label": "billing", "model_score": 0.62 }
```

| Field | Meaning |
|---|---|
| `id` | Stable row id. Both demos' seed scripts use this as the primary key, so `id=7` in Demo 1 and `id=7` in Demo 2 are the same ticket. |
| `text` | The support ticket text a reviewer reads to decide if the prediction is right. |
| `model_label` | The category a (fictional) triage model predicted — one of `billing`, `technical`, `account`, `shipping`, `refund`. |
| `model_score` | The model's confidence in that label, 0-1. Deliberately mixed: some rows are high-confidence and correct, some are low-confidence and wrong, so labeling the set isn't a rubber-stamp exercise. |

Nothing writes to this file. Each demo's `seed_demo`/`seed.py` script only reads it (relative
path from the stage folder) and assigns rows to reviewers round-robin — see each demo's own
README for exactly how.
