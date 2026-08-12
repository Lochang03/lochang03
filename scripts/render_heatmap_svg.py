"""
Step 5b: Render the contribution JSON as an animated heatmap SVG.
Reads: data/contributions.json
Output: contrib-heatmap.svg
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# level 0 (none) -> level 5 (neon top end, custom beyond GitHub's usual 4 levels)

BG = "#0d1117"
BOX = 11
GAP = 4
CELL = BOX + GAP
LEFT_PAD = 30
TOP_PAD = 20
BOTTOM_PAD = 50

def load_data():
    with open("data/contributions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_week_grid(days):
    # Map date -> day info
    by_date = {d["date"]: d for d in days}
    if not days:
        return []

    all_dates = sorted(by_date.keys())
    start = datetime.strptime(all_dates[0], "%Y-%m-%d")
    end = datetime.strptime(all_dates[-1], "%Y-%m-%d")

    # Align start to the preceding Sunday so weeks are clean columns
    start -= timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    current = start
    week = []
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        info = by_date.get(date_str, {"count": 0, "level": 0})
        week.append({"date": date_str, "count": info["count"], "level": min(info["level"], 5)})
        if len(week) == 7:
            weeks.append(week)
            week = []
        current += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    return weeks

def build_svg(weeks, stats):
    cols = len(weeks)
    width = LEFT_PAD + cols * CELL + 20
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="11">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    delay_step = 0.012  # stagger per box, diagonal-ish via (col+row) order

    for c, week in enumerate(weeks):
        for r, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + c * CELL
            y = TOP_PAD + r * CELL
            level = day["level"]
            color = PALETTE[level]
            delay = (c + r) * delay_step

            parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.4s" fill="freeze"/>'
                f'</rect>'
            )

    # Legend: Less -> More
    legend_y = TOP_PAD + 7 * CELL + 20
    legend_x = LEFT_PAD
    parts.append(f'<text x="{legend_x}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = legend_x + 40
    for level, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{legend_y - 10}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
        lx += CELL
    parts.append(f'<text x="{lx + 6}" y="{legend_y}" fill="#8b949e">More</text>')

    # Stats footer
    total = stats["total_contributions"]
    footer_y = legend_y + 22
    parts.append(
        f'<text x="{legend_x}" y="{footer_y}" fill="#c9d1d9">'
        f'{total} contributions in the last year</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)

def main():
    data = load_data()
    weeks = build_week_grid(data["days"])
    svg = build_svg(weeks, data["stats"])
    Path("contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print("Saved: contrib-heatmap.svg")

if __name__ == "__main__":
    main()