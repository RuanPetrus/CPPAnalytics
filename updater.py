import csv, json
from datetime import datetime
from pprint import pprint

from core import Bucket_Range
from atcoder import update_atcoder
from cses import update_cses

from cf import update_cf_contest

atcoder_problem_ranges = [
    Bucket_Range(low=1200, high=1600, max_count=50),
    Bucket_Range(low=1600, high=2000, max_count=150),
    Bucket_Range(low=2000, high=100000, max_count=1000000),
]

atcoder_rating_ranges = [
    Bucket_Range(low=1200, high=1600, max_count=10),
    Bucket_Range(low=1600, high=2000, max_count=20),
    Bucket_Range(low=2000, high=100000, max_count=30),
]

cses_problem_ranges = [
    Bucket_Range(low=0, high=1, max_count=300),
]

cses_rating_ranges = [
    Bucket_Range(low=0, high=1, max_count=0),
]

cf_problem_ranges = [
    Bucket_Range(low=1200, high=1600, max_count=50),
    Bucket_Range(low=1600, high=2000, max_count=150),
    Bucket_Range(low=2000, high=100000, max_count=1000000),
]

cf_rating_ranges = [
    Bucket_Range(low=1200, high=1600, max_count=10),
    Bucket_Range(low=1600, high=2000, max_count=20),
    Bucket_Range(low=2000, high=100000, max_count=30),
]

begin_date = datetime(year=2026, month=1, day=1)
deadline = datetime(year=2026, month=6, day=30)

rules = [
    "Todas as questões do CSES contam.",
    "Pro Atcoder até 50 questões entre 1200–1599, até 150 entre 1600–1999, e livre acima de 1999.",
    "Pontucao por rating no Atcoder: acima de 1200 no atcoder ganham 10 pontos, acima de 1600 no atcoder ganham 20 pontos, acima de 2000 no atcoder ganham 30 pontos"
]

def load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = csv.DictReader(f)
        return list(data)

def main() -> None:
    users_table = load_csv("users.csv")

    atcoder_handles = list(set(r.get("atcoder", "").strip() for r in users_table))
    atcoder_data = update_atcoder(atcoder_handles, begin_date, atcoder_problem_ranges, atcoder_rating_ranges)

    cses_handles = list(set(r.get("cses", "").strip() for r in users_table))
    cses_data = update_cses(cses_handles, begin_date, cses_problem_ranges, cses_rating_ranges)

    cf_handles = list(set(r.get("codeforces", "").strip() for r in users_table))
    cf_data = update_cf_contest(cf_handles, begin_date, cf_problem_ranges, cf_rating_ranges)

    competitors_data = [
        {
            "nome": user["nome"],
            "meta": user["meta"],
            "scores_sources": {
                "atcoder" : atcoder_data[user["atcoder"]],
                "cses" : cses_data[user["cses"]],
                "codeforces" : cf_data[user["codeforces"]],
            }
        }
        for user in users_table
    ]

    site_data = {
        "begin_date": f"{begin_date.year}-{begin_date.month}-{begin_date.day}",
        "deadline": f"{deadline.year}-{deadline.month}-{deadline.day}",
        "rules": rules,
        "competitors": competitors_data,
    }

    with open("site_data.json", "w", encoding="utf-8") as f:
        json.dump(site_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
