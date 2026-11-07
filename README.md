# LLMeval: customer message intent labeling

A small evaluation project for customer-support intent classification in English, Spanish, and French. It covers the full loop: a labeling rubric, a gold-labeled set, model predictions, and accuracy and agreement scoring.

## Contents

| Path | What it is |
|---|---|
| `data/rubric.md` | Labeling rubric: intent definitions, includes and excludes, tie-break rules, escalation to `ambiguous` |
| `data/gold.csv` | 36 gold-labeled messages: 12 each in English, Spanish, and French; 12 each of `order_status`, `cancel_order`, `refund_request` |
| `data/check_labels.py` | Prints each gold row with its label for manual review against the rubric |
| `summarize_gold.py` | Counts gold labels by intent and by language |
| `results/model_a.csv`, `results/model_b.csv` | Predicted intent per message ID for two models |
| `eval.py` | Scores a prediction file against gold |

## Labels

Each message gets one of three intents, or `ambiguous`:

- `order_status`: asks about shipping or delivery
- `cancel_order`: wants an order or subscription stopped
- `refund_request`: wants money back

`ambiguous` rows are excluded from scoring. Rules for the tricky cases (a cancel request that also asks for status, a refund on an unshipped order) are in the rubric's tie-break section.

## Run the evaluation

Requires Python 3 and no extra packages.

```bash
python3 eval.py results/model_a.csv
python3 eval.py results/model_b.csv
```

Output: accuracy, Cohen's kappa, accuracy by language and by gold intent, and a list of misclassified rows.

Prediction files need the columns `id,language,pred_intent`, with one row for every gold ID.

## Results

| Model | Accuracy | Cohen's kappa |
|---|---|---|
| A | 0.750 (27/36) | 0.625 |
| B | 0.944 (34/36) | 0.917 |

**Model A** misses most on `refund_request` (7/12). Its main confusions are refund vs. cancel and refund vs. order status, in all three languages. French is its weakest language at 0.667.

**Model B** gets every `refund_request` right. Its two errors are `es-07` (cancel predicted as order status) and `fr-03` (order status predicted as cancel).

## Notes

- Gold labels were checked against the rubric by hand, including the Spanish and French rows.
- Results come from a single 36-row set. Treat the gap between models as directional, not statistically established.
