import os, sys, time, re
import requests
from datetime import datetime
from core import Bucket_Range, get_bucket_from_diff

SEP = os.path.sep
DIR_PATH = os.getcwd()
if not hasattr(sys, "ps1"):
    DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + SEP

RESOURCES_PATH = DIR_PATH + "resources" + SEP
ATCODER_PROBLEM_INFORMATION_PATH = RESOURCES_PATH + "problem_info.json"

CURR_RATING_REGEX = re.compile("""<th class=["']no-break["']>Rating<\\/th><td><span class=["']user-.*["']>(\\d*)<\\/span>""")
MAX_RATING_REGEX = re.compile("""<th class=["']no-break["']>Highest Rating<\\/th>\\s*<td>.*\\s*<span class=["']user-.*["']>(\\d*)<\\/span>""")

def get_problems_info() -> dict[str, int]:
    problem_information_url = "https://kenkoooo.com/atcoder/resources/problem-models.json"
    r = requests.get(problem_information_url)
    info = r.json()
    problem_information = {
            name: info[name]["difficulty"]
            for name in info.keys()
            if "difficulty" in info[name]
    }
    return problem_information

def get_all_submissions(handle: str, date: datetime) -> dict:
    unix_second = time.mktime(date.timetuple())
    subs = []

    while True:
        url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={handle}&from_second={int(unix_second)}"
        r = requests.get(url)
        r.raise_for_status()
        batch = r.json()
        if not batch: break

        subs.extend(batch)
        unix_second = batch[-1]["epoch_second"] + 1

        if len(batch) < 500: break
        time.sleep(1.1)
    return subs

def get_problem_buckets(handle: str, date: datetime, problems_info: dict[str, int], bucket_ranges: list[Bucket_Range]) -> dict[str, int]:
    submissions = get_all_submissions(handle, date)

    ac_problems_id = set(
        s["problem_id"]
        for s in submissions
        if s["result"] == "AC"
    )

    buckets: dict[str, int] = {}
    for pid in ac_problems_id:
        diff = problems_info.get(pid, 0)
        b = get_bucket_from_diff(diff, bucket_ranges)
        if b:
            buckets[str(b)] = min(buckets.get(str(b), 0) + 1, b.max_count)

    return buckets

def get_max_rating(handle: str) -> int:
    user_info_url = f"https://atcoder.jp/users/{handle}"
    r = requests.get(user_info_url)
    m = MAX_RATING_REGEX.search(r.text)
    if m is None:
        return 0
    return int(m.group(1))

def update_atcoder(handles: list[str], date: datetime, problem_buckets: list[Bucket_Range], rating_buckets: Bucket_Range) -> dict[str, dict]:
    problems_info = get_problems_info()

    atcoder_data = {}
    for h in handles:
        buckets = get_problem_buckets(h, date, problems_info, problem_buckets)
        questions_score = 0
        for b in buckets:
            questions_score += buckets[b]

        max_rating =  get_max_rating(h)
        max_rating_score = 0
        b = get_bucket_from_diff(max_rating, rating_buckets)
        if b:
            max_rating_score = b.max_count

        atcoder_data[h] = {
            "rating_score" : max_rating_score,
            "questions_score" : questions_score,
        }
    return atcoder_data
