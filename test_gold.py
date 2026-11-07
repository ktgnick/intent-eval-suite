import csv
import sys
from pathlib import Path

from fastapi import HTTPException

import main

GOLD = Path.home() / "Desktop" / "LLMeval" / "data" / "gold.csv"
OUT = Path(__file__).parent / "gold_predictions.csv"


def main_run():
    rows = [r for r in csv.DictReader(GOLD.open(encoding="utf-8")) if r["intent"] != "ambiguous"]
    results = []
    failures = 0
    for r in rows:
        try:
            out = main.classify(main.ClassifyRequest(text=r["text"]))
            pred, reason = out.intent, out.reason
        except HTTPException as exc:
            pred, reason = "error", str(exc.detail)
            failures += 1
        results.append({"id": r["id"], "language": r["language"], "gold": r["intent"], "pred": pred, "reason": reason})
        print(f"{r['id']:8} gold={r['intent']:15} pred={pred:15} {'ok' if pred == r['intent'] else 'MISS'}", flush=True)

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "language", "gold", "pred", "reason"])
        w.writeheader()
        w.writerows(results)

    correct = sum(x["gold"] == x["pred"] for x in results)
    print(f"\nAccuracy: {correct}/{len(results)} = {correct / len(results):.3f}")
    print(f"Model/API failures: {failures}")
    print(f"Predictions written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main_run())
