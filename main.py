import json
import os
from pathlib import Path
from typing import Literal

import anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Rubric is a snapshot of LLMeval's data/rubric.md, loaded into the system prompt.
RUBRIC = (Path(__file__).parent / "rubric.md").read_text(encoding="utf-8")
MODEL = os.environ.get("INTENT_MODEL", "claude-haiku-5-5")
LABELS = ("order_status", "cancel_order", "refund_request", "ambiguous")

SYSTEM = f"""You classify customer support messages into exactly one intent label.
Follow this rubric exactly:

{RUBRIC}

Reply with only a JSON object, no other text:
{{"intent": "<label>", "reason": "<under 15 words>"}}

The intent must be one of: order_status, cancel_order, refund_request, ambiguous.
Use ambiguous only when the rubric's escalation rule applies.
Messages may be in English, Spanish, or French."""

app = FastAPI(title="Customer intent classifier")


class ClassifyRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class ClassifyResponse(BaseModel):
    intent: Literal["order_status", "cancel_order", "refund_request", "ambiguous"]
    reason: str


def parse_model_output(raw: str) -> dict:
    # Accept the JSON object even if the model wraps it in extra text or code fences.
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    data = json.loads(raw[start : end + 1])
    if not isinstance(data, dict) or data.get("intent") not in LABELS:
        raise ValueError("intent missing or not a known label")
    return data


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic()
    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM,
            messages=[{"role": "user", "content": req.text}],
        )
    except anthropic.APIError as exc:
        raise HTTPException(status_code=502, detail=f"model call failed: {type(exc).__name__}")

    # The model can return thinking blocks before the answer; use only the text blocks.
    raw = "".join(block.text for block in msg.content if block.type == "text")
    try:
        data = parse_model_output(raw)
    except (ValueError, json.JSONDecodeError):
        # Include the start of the raw reply so failures can be diagnosed (dev aid).
        raise HTTPException(status_code=502, detail=f"unusable model reply: {raw[:200]!r}")

    return ClassifyResponse(intent=data["intent"], reason=str(data.get("reason", "")))
