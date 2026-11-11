import csv
import sys
from collections import Counter

# Usage: python3 eval.py results/model_a.csv
# Rows with gold label `ambiguous` are excluded, per the rubric.


def load(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cohen_kappa(pairs):
    n = len(pairs)
    observed = sum(g == p for g, p in pairs) / n
    gold_counts = Counter(g for g, _ in pairs)
    pred_counts = Counter(p for _, p in pairs)
    labels = set(gold_counts) | set(pred_counts)
    expected = sum(gold_counts[l] * pred_counts[l] for l in labels) / (n * n)
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def main(pred_path):
    gold = {r["id"]: r for r in load("data/gold.csv") if r["intent"] != "ambiguous"}
    preds = {r["id"]: r for r in load(pred_path)}

    missing = set(gold) - set(preds)
    if missing:
        sys.exit(f"missing predictions for: {sorted(missing)}")

    pairs = [(gold[i]["intent"], preds[i]["pred_intent"]) for i in sorted(gold)]
    correct = sum(g == p for g, p in pairs)
    print(f"File: {pred_path}")
    print(f"Rows scored: {len(pairs)}")
    print(f"Accuracy: {correct / len(pairs):.3f} ({correct}/{len(pairs)})")
    print(f"Cohen's kappa: {cohen_kappa(pairs):.3f}")

    print("\nAccuracy by language:")
    for lang in sorted({gold[i]["language"] for i in gold}):
        ids = [i for i in sorted(gold) if gold[i]["language"] == lang]
        hits = sum(gold[i]["intent"] == preds[i]["pred_intent"] for i in ids)
        print(f"  {lang}: {hits / len(ids):.3f} ({hits}/{len(ids)})")

    print("\nAccuracy by gold intent:")
    for intent in sorted({g for g, _ in pairs}):
        sub = [(g, p) for g, p in pairs if g == intent]
        hits = sum(g == p for g, p in sub)
        print(f"  {intent}: {hits / len(sub):.3f} ({hits}/{len(sub)})")

    print("\nErrors (id, language, gold -> predicted):")
    for i in sorted(gold):
        if gold[i]["intent"] != preds[i]["pred_intent"]:
            print(f"  {i}, {gold[i]['language']}, {gold[i]['intent']} -> {preds[i]['pred_intent']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python3 eval.py <predictions.csv>")
    main(sys.argv[1])
