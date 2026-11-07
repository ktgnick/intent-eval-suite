# Customer intent classifier API

A FastAPI service that labels a customer support message with one intent: `order_status`, `cancel_order`, `refund_request`, or `ambiguous`. The system prompt is built from a labeling rubric, so changing the rubric changes the classifier's behavior. The rubric and gold-labeled data live in the companion repo [LLMeval](https://github.com/ktgnick/LLMeval).

## Live demo

- **Try it in the browser:** https://intent-api-fft0.onrender.com/docs
- **Health check:** https://intent-api-fft0.onrender.com/health

The root URL returns 404 by design. Use `/docs` for the interactive page.

## Results

| Test set | Messages | Correct | Notes |
|---|---|---|---|
| Gold set (from LLMeval) | 36 | 36/36 | English, Spanish, French. The rubric was written from these examples. |
| Held-out set | 15 | 15/15 | New messages, written after the rubric. Labels are the author's reading of the rubric. |

Both are single runs. The gold set was used to build the rubric, so treat its score as optimistic. A harder test set with ambiguous and messy messages is the next step.

## How it works

1. A request hits `POST /classify` with a `text` field.
2. The service checks a per-client rate limit (30 requests per minute by default).
3. The model receives the rubric as its system prompt and returns a JSON object with `intent` and `reason`.
4. The service checks the label is one of the four allowed values and returns the result. Malformed replies return a 502 with the start of the raw reply, to aid debugging.

## Use

```bash
curl -X POST https://intent-api-fft0.onrender.com/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Where is my package? It was supposed to arrive yesterday."}'
```

Response:

```json
{"intent": "order_status", "reason": "Customer asks where their package is."}
```

## Run locally

```bash
cd intent-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here   # keep this out of the repo
uvicorn main:app --reload
```

To score a labeled CSV through the classifier (columns `id,language,text,intent`):

```bash
python test_gold.py held_out.csv
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | none (required) | Model API key. Set as a secret in production, never in the repo. |
| `INTENT_MODEL` | `claude-haiku-5-5` | Model to use |
| `RATE_LIMIT_PER_MIN` | `30` | Requests per client per minute |

## Deployment

Deployed on Render from `render.yaml`. The API key is set in the Render dashboard. A monthly spend limit is also set on the Anthropic key.

## Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI app, prompt construction, validation, rate limit |
| `rubric.md` | Labeling rubric, copied from LLMeval |
| `test_gold.py` | Runs a labeled CSV through the classifier and reports accuracy |
| `held_out.csv` | 15 held-out messages, with labels |
| `render.yaml` | Render deploy configuration |
| `requirements.txt` | Pinned dependencies |
