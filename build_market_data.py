"""Reproduce the year-end 2021 market-entry dashboard data from the Kaggle ZIP."""
import argparse
import csv
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path


def family(category):
    name = " ".join(category.casefold().split())
    for label, words in [
        ("Tequila", r"tequila"),
        ("Liqueurs & schnapps", r"liqueur|cordial|schnapps|triple sec|sloe gin"),
        ("Whiskey", r"whisk|bourbon|single malt scotch"),
        ("Vodka", r"vodka"),
        ("Rum", r"\brum\b"),
        ("Brandy", r"brandies|brandy"),
        ("Gin", r"\bgins?\b"),
        ("Cocktails / RTD", r"cocktails"),
    ]:
        if re.search(words, name):
            return label
    return "Specialty & other"


def summarize(archive):
    categories, monthly_market, monthly_tequila, monthly_bottles = (Counter() for _ in range(4))
    stores = defaultdict(Counter)
    names = {}
    rows = 0
    with zipfile.ZipFile(archive) as bundle:
        [entry] = [name for name in bundle.namelist() if name.lower().endswith(".csv")]
        with io.TextIOWrapper(bundle.open(entry), encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                date = row["date"]
                if not date.startswith("2021-"):
                    continue
                rows += 1
                month = int(date[5:7])
                store = row["store_number"]
                cents = int(Decimal(row["sale_dollars"].lstrip("$")) * 100)
                category = row["category_name"].strip()
                categories[category] += cents
                monthly_market[month] += cents
                stores[store]["market"] += cents
                if store not in names or date >= names[store][0]:
                    names[store] = (date, row["store_name"].strip(), row["city"].strip())
                if "tequila" in category.casefold():
                    monthly_tequila[month] += cents
                    monthly_bottles[month] += int(row["bottles_sold"])
                    stores[store]["tequila"] += cents

    market = sum(monthly_market.values())
    tequila = sum(monthly_tequila.values())
    assert rows == 2_622_712 and len(monthly_market) == 12
    assert tequila == 3_458_449_125 and sum(monthly_bottles.values()) == 1_616_872
    assert sum(v["market"] for v in stores.values()) == market
    assert sum(v["tequila"] for v in stores.values()) == tequila
    groups = Counter()
    for category, cents in categories.items():
        groups[family(category)] += cents
    assert sum(groups.values()) == market and groups["Tequila"] == tequila

    share = tequila / market
    ordered_spend = sorted(v["market"] for v in stores.values())
    cutoff = ordered_spend[(3 * len(ordered_spend) + 3) // 4 - 1]
    targets = []
    for key, values in stores.items():
        total, segment = values["market"], values["tequila"]
        if total >= cutoff and segment >= 1_000_000 and segment / total < share:
            _, name, city = names[key]
            targets.append((round(total * share - segment), key, name, city, total, segment))
    targets.sort(key=lambda record: (-record[0], record[1]))
    return {
        "rows": rows, "stores": len(stores), "cutoff_cents": cutoff,
        "eligible": len(targets), "targets": targets[:3],
        "families": groups,
        "category_map": [[name, family(name), cents] for name, cents in sorted(categories.items())],
        "months": [[m, monthly_bottles[m], monthly_tequila[m], monthly_market[m]] for m in range(1, 13)],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = summarize(args.archive)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print({key: value for key, value in result.items() if key not in ("category_map", "months")})
