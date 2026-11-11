import csv

with open("data/gold.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(row["id"], "|", row["text"], "| gold:", row["intent"])