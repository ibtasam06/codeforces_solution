import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

USERNAME = os.environ["ibtasam"]

API_URL = f"https://codeforces.com/api/user.status?handle={USERNAME}&from=1&count=1000"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(API_URL, headers=headers)
response.raise_for_status()

data = response.json()

if data["status"] != "OK":
    raise Exception("Could not access Codeforces API")

submissions = data["result"]

solutions_dir = Path("solutions")
solutions_dir.mkdir(exist_ok=True)

for submission in submissions:

    if submission.get("verdict") != "OK":
        continue

    submission_id = submission["id"]
    contest_id = submission["contestId"]

    problem = submission["problem"]

    index = problem.get("index", "")
    problem_name = problem.get("name", "Unknown Problem")

    language = submission.get("programmingLanguage", "")

    safe_name = "".join(
        c if c.isalnum() or c in " _-" else "_"
        for c in problem_name
    ).strip()

    if "Python" in language:
        extension = ".py"
    elif "GNU C++" in language or "C++" in language:
        extension = ".cpp"
    elif "Java" in language:
        extension = ".java"
    elif "C#" in language:
        extension = ".cs"
    elif "Kotlin" in language:
        extension = ".kt"
    elif "JavaScript" in language:
        extension = ".js"
    else:
        extension = ".txt"

    filename = solutions_dir / f"{contest_id}_{index}_{safe_name}{extension}"

    if filename.exists():
        continue

    submission_url = (
        f"https://codeforces.com/contest/"
        f"{contest_id}/submission/{submission_id}"
    )

    print(f"Downloading: {problem_name}")

    try:
        page = requests.get(
            submission_url,
            headers=headers,
            timeout=30
        )

        page.raise_for_status()

        soup = BeautifulSoup(page.text, "html.parser")

        source = soup.find("pre", id="program-source-text")

        if source is None:
            print(f"Could not find source for submission {submission_id}")
            continue

        code = source.get_text()

        filename.write_text(
            code,
            encoding="utf-8"
        )

        print(f"Saved: {filename}")

        time.sleep(1)

    except Exception as e:
        print(f"Error with submission {submission_id}: {e}")
