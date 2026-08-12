"""
Step 5a: Fetch real GitHub contribution data — no token needed.
Scrapes the public contributions HTML fragment GitHub itself uses.
Output: data/contributions.json
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = "lochang03"  # change if needed

def fetch_contributions(username: str):
    url = f"https://github.com/users/{username}/contributions"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text

def parse_contributions(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    cells = soup.find_all("td", class_="ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        if date is None:
            continue

        level_attr = cell.get("data-level")
        try:
            level = int(level_attr) if level_attr is not None else 0
        except ValueError:
            level = 0

        # Count lives in the paired <tool-tip>'s text, not a data attribute
        cell_id = cell.get("id")
        count = 0
        if cell_id:
            tooltip = soup.find("tool-tip", attrs={"for": cell_id})
            if tooltip:
                text = tooltip.get_text(strip=True)
                match = re.search(r"(\d+)\s+contribution", text)
                if match:
                    count = int(match.group(1))
                # "No contributions on ..." -> count stays 0

        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days

def compute_stats(days):
    total = sum(d["count"] for d in days)

    # Current streak: consecutive days with count > 0, ending at the most recent day
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # Longest streak
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda d: d["count"], default=None)

    # Monthly totals (last 12 months present in data)
    monthly = {}
    for d in days:
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly,
    }

def main():
    username = sys.argv[1] if len(sys.argv) > 1 else GITHUB_USERNAME
    print(f"Fetching contributions for: {username}")
    html = fetch_contributions(username)
    days = parse_contributions(html)

    if not days:
        print("Warning: no contribution cells found — GitHub markup may have changed.")
        sys.exit(1)

    stats = compute_stats(days)

    output = {
        "username": username,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    Path("data").mkdir(exist_ok=True)
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Saved: data/contributions.json ({len(days)} days, {stats['total_contributions']} total contributions)")

if __name__ == "__main__":
    main()