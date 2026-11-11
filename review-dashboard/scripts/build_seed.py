"""Build the database seed CSVs from the LLMeval and intent-api projects.

Usage (from review-dashboard/):
    python3 scripts/build_seed.py ../LLMeval ../intent-api

Writes:
    api/src/main/resources/db/seed/examples.csv
    api/src/main/resources/db/seed/runs.csv
    api/src/main/resources/db/seed/predictions.csv

A run whose prediction file contains error rows is skipped, so a failed
API call never shows up as a wrong answer on the dashboard.
"""

import csv
import sys
from pathlib import Path

SEED_DIR = Path(__file__).resolve().parent.parent / "api" / "src" / "main" / "resources" / "db" / "seed"


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main(llmeval: Path, intent_api: Path):
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    # Examples: the gold set (LLMeval) and the held-out set (intent-api).
    examples = []
    for r in read(llmeval / "data" / "gold.csv"):
        examples.append({"id": r["id"], "language": r["language"], "text": r["text"], "intent": r["intent"], "set_name": "gold"})
    for r in read(intent_api / "held_out.csv"):
        examples.append({"id": r["id"], "language": r["language"], "text": r["text"], "intent": r["intent"], "set_name": "held_out"})
    gold_ids = {e["id"] for e in examples if e["set_name"] == "gold"}
    held_ids = {e["id"] for e in examples if e["set_name"] == "held_out"}
    write(SEED_DIR / "examples.csv", ["id", "language", "text", "intent", "set_name"], examples)

    # Runs and their predictions.
    runs = [
        ("model_a", "Model A (LLMeval baseline)", "Predictions from the earlier project, scored on the gold set."),
        ("model_b", "Model B (LLMeval baseline)", "Predictions from the earlier project, scored on the gold set."),
        ("haiku_gold", "Claude Haiku 5.5 with rubric prompt: gold set", "intent-api classifier on the 36-row gold set."),
        ("haiku_held_out", "Claude Haiku 5.5 with rubric prompt: held-out set", "intent-api classifier on 15 messages written after the rubric."),
    ]
    sources = {
        "model_a": (llmeval / "results" / "model_a.csv", "pred_intent", None),
        "model_b": (llmeval / "results" / "model_b.csv", "pred_intent", None),
        "haiku_gold": (intent_api / "gold_predictions.csv", "pred", "reason"),
        "haiku_held_out": (intent_api / "held_out_predictions.csv", "pred", "reason"),
    }

    run_rows, pred_rows = [], []
    for run_id, label, description in runs:
        path, pred_col, reason_col = sources[run_id]
        rows = read(path)
        if any(r[pred_col] == "error" for r in rows):
            print(f"SKIP {run_id}: {path.name} contains error rows. Rerun its test first.")
            continue
        ids = {r["id"] for r in rows}
        allowed = gold_ids if run_id.endswith("gold") or run_id.startswith("model_") else held_ids
        if not ids <= allowed:
            sys.exit(f"{run_id}: ids in {path.name} do not match the expected example set")
        run_rows.append({"id": run_id, "label": label, "description": description})
        for r in rows:
            pred_rows.append({
                "run_id": run_id,
                "example_id": r["id"],
                "pred_intent": r[pred_col],
                "reason": r[reason_col] if reason_col else "",
            })
        print(f"OK   {run_id}: {len(rows)} predictions")

    write(SEED_DIR / "runs.csv", ["id", "label", "description"], run_rows)
    write(SEED_DIR / "predictions.csv", ["run_id", "example_id", "pred_intent", "reason"], pred_rows)
    print(f"Wrote {len(examples)} examples, {len(run_rows)} runs, {len(pred_rows)} predictions to {SEED_DIR}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python3 scripts/build_seed.py <path to LLMeval> <path to intent-api>")
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
