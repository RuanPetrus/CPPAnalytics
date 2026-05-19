#! python3

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from core import Bucket_Range, get_bucket_from_diff

hostsite = 'https://cses.fi/'

def login():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    username = secrets["cses_username"]
    password = secrets["cses_password"]

    browser = requests.session()
    login_page = browser.get(hostsite+"login")
    html = BeautifulSoup(login_page.text, "html.parser")
    csrf = html.find("input", {"name": "csrf_token"}).attrs['value']
    payload = {"csrf_token": csrf, "nick": username, "pass": password}
    home_page = browser.post(hostsite+"login", data=payload)
    time.sleep(2)
    return browser

def get_html(link, browser):
    return BeautifulSoup(browser.get(link).content, "html.parser")

def get_ac_problems(handle: str, browser):
    html = get_html(hostsite+"problemset/user/" + handle, browser)
    tasks = html.find_all('td')
    idx = 0
    results = []
    for i in range(len(tasks)):
        a = tasks[i].a
        if a is not None:
            if 'full' in a.attrs['class']:
                results.append(i)
    return results

def get_problem_buckets(handle: str, date: datetime, bucket_ranges: list[Bucket_Range], browser) -> dict[Bucket_Range, int]:
    ac_problems_id = get_ac_problems(handle, browser)

    # Dictionary now uses the Bucket_Range object as the key
    buckets: dict[Bucket_Range, int] = {}
    for pid in ac_problems_id:
        diff = 0 # CSES doesn't use difficulty ratings
        b = get_bucket_from_diff(diff, bucket_ranges)
        if b:
            # We use 'b' directly instead of 'str(b)'
            buckets[b] = min(buckets.get(b, 0) + 1, b.max_count)

    return buckets

def update_cses(handles: list[str], date: datetime, problem_buckets: list[Bucket_Range], rating_buckets: list[Bucket_Range]) -> dict[str, dict]:
    browser = login()
    cses_data = {}
    for h in handles:
        buckets = get_problem_buckets(h, date, problem_buckets, browser)
        
        questions_score = 0
        # Iterate through the bucket objects and multiply by points
        for b, count in buckets.items():
            questions_score += count * b.points

        cses_data[h] = {
            "rating_score" : 0, # CSES doesn't have user ratings
            "questions_score" : questions_score,
        }
    return cses_data

if __name__=="__main__":
    c = CSES()
    for a in ["138398", "137594"]:
    	print(len(c.get_problems(a)))
