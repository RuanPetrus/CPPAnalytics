import os, sys, time, re
import json
from datetime import datetime
from core import Bucket_Range, get_bucket_from_diff

import requests

hostsite = 'https://codeforces.com/'

def get_all_contest_submissions(handle: str, date: datetime) -> set[tuple[str, int]]:
    unix_second = time.mktime(date.timetuple())
    gotjson = requests.get(hostsite+'api/user.status?handle='+handle)
    if not gotjson.ok:
        raise Exception(handle)
    time.sleep(2)
    info = json.loads(gotjson.text)['result']
    results = set()
    for submission in info:
        if submission['verdict'] != 'OK' or submission['creationTimeSeconds'] < unix_second:
            continue  #not AC or too old
        problem_info = submission['problem']
        pid = problem_info['index']
        rating = 0
        if 'contestId' in problem_info:
            pid += str(problem_info['contestId'])
        elif 'problemsetName' in problem_info:
            pid += str(problem_info['problemsetName'])
        else:
            continue #i dont know what is this problem
        if 'rating' in problem_info:
            rating = int(problem_info['rating'])
        else:
            continue
        results.add((pid, rating))
    return results

def get_contest_problem_buckets(handle: str, date: datetime, bucket_ranges: list[Bucket_Range]) -> dict[Bucket_Range, int]:
    ac_problems = get_all_contest_submissions(handle, date)

    # Dictionary now uses the Bucket_Range object as the key
    buckets: dict[Bucket_Range, int] = {} 
    for (pid, diff) in ac_problems:
        b = get_bucket_from_diff(diff, bucket_ranges)
        if b:
            # We use 'b' directly instead of 'str(b)'
            buckets[b] = min(buckets.get(b, 0) + 1, b.max_count)

    return buckets

def get_max_rating(handle: str) -> int:
    gotjson = requests.get(hostsite+'api/user.info?handles='+handle)
    if not gotjson.ok:
        raise Exception(handle)
    time.sleep(2)
    info = json.loads(gotjson.text)['result'][0]
    return int(info['maxRating'])

def update_cf_contest(handles: list[str], date: datetime, problem_buckets: list[Bucket_Range], rating_buckets: list[Bucket_Range]) -> dict[str, dict]:
    cf_data = {}
    for h in handles:
        buckets = get_contest_problem_buckets(h, date, problem_buckets)
        
        questions_score = 0
        # Iterate through the bucket objects and their problem counts
        for b, count in buckets.items():
            # Multiply the number of problems by the points they are worth
            questions_score += count * b.points 

        max_rating = get_max_rating(h)
        max_rating_score = 0
        b = get_bucket_from_diff(max_rating, rating_buckets)
        if b:
            max_rating_score = b.max_count

        cf_data[h] = {
            "rating_score" : max_rating_score,
            "questions_score" : questions_score,
        }
    return cf_data

if __name__ == "__main__":
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
    cf_handles = ["MagePetrus"]
    cf_data = update_cf_contest(cf_handles, begin_date, cf_problem_ranges, cf_rating_ranges)
