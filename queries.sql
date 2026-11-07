-- Intent evaluation queries (SQLite).
--
-- Load the CSVs first, in the sqlite3 shell from the project root:
--   .mode csv
--   .import data/gold.csv gold
--   .import results/model_a.csv model_a
--   .import results/model_b.csv model_b
--   .read queries.sql
--
-- Tables: gold(id, language, text, intent), model_a(id, language, pred_intent), model_b(id, language, pred_intent)

-- One row per scored message, both models stacked.
-- Rows with gold label 'ambiguous' are excluded, per the rubric.
DROP VIEW IF EXISTS scored;
CREATE VIEW scored AS
SELECT 'model_a' AS model, g.id, g.language, g.intent AS gold, p.pred_intent AS pred
FROM gold g JOIN model_a p ON p.id = g.id
WHERE g.intent <> 'ambiguous'
UNION ALL
SELECT 'model_b', g.id, g.language, g.intent, p.pred_intent
FROM gold g JOIN model_b p ON p.id = g.id
WHERE g.intent <> 'ambiguous';

-- 1. Overall accuracy per model
SELECT model,
       COUNT(*) AS rows_scored,
       SUM(gold = pred) AS correct,
       ROUND(1.0 * SUM(gold = pred) / COUNT(*), 3) AS accuracy
FROM scored
GROUP BY model;

-- 2. Accuracy by language per model
SELECT model, language,
       COUNT(*) AS rows_scored,
       ROUND(1.0 * SUM(gold = pred) / COUNT(*), 3) AS accuracy
FROM scored
GROUP BY model, language
ORDER BY model, language;

-- 3. Accuracy by gold intent per model
SELECT model, gold AS intent,
       COUNT(*) AS rows_scored,
       ROUND(1.0 * SUM(gold = pred) / COUNT(*), 3) AS accuracy
FROM scored
GROUP BY model, gold
ORDER BY model, gold;

-- 4. Confusion matrix per model (rows = gold, columns = predicted)
SELECT model, gold,
       SUM(pred = 'order_status')   AS pred_order_status,
       SUM(pred = 'cancel_order')   AS pred_cancel_order,
       SUM(pred = 'refund_request') AS pred_refund_request
FROM scored
GROUP BY model, gold
ORDER BY model, gold;

-- 5. Misclassified rows, with the message text
SELECT s.model, s.id, s.language, g.text, s.gold, s.pred
FROM scored s JOIN gold g ON g.id = s.id
WHERE s.gold <> s.pred
ORDER BY s.model, s.id;

-- 6. Most common error pairs per model
SELECT model, gold, pred, COUNT(*) AS n
FROM scored
WHERE gold <> pred
GROUP BY model, gold, pred
ORDER BY model, n DESC;
