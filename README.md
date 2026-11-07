# Customer intent classifier API

FastAPI service that labels a customer message with one intent: `order_status`, `cancel_order`, `refund_request`, or `ambiguous`. The system prompt is built from `rubric.md`, a snapshot of the labeling rubric from the LLMeval project.

## Setup

```bash
cd intent-api
source .venv/bin/activate
export ANTHROPIC_API_KEY=your-key-here   # keep this out of the repo
uvicorn main:app --reload
```

## Use

```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Where is my package? It was supposed to arrive yesterday."}'
```

Response:

```json
{"intent": "order_status", "reason": "Asks where the package is."}
```

`GET /health` returns the status and the model in use. Set `INTENT_MODEL` to change the model (default `claude-haiku-5-5`).

## Status

- Step 1 done: endpoint, rubric prompt, output validation. Tested without a model call.
- Not yet run against the model. That needs `ANTHROPIC_API_KEY`.
