import csv
from collections import Counter

# Read each CSV row into a dict keyed by the header names
with open("data/gold.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("Total rows:", len(rows))

# Count how many rows have each intent
intent_counts = Counter(row["intent"] for row in rows)
print("Per intent:", intent_counts)

language_counts = Counter(row["language"] for row in rows)
print("Per language:", language_counts)

pair_counts = Counter((row["intent"], row["language"]) for row in rows)
print("Per intent and language:", pair_counts)