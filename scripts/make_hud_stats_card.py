"""
Creative GitHub stats card v3 - animated radar/HUD "system scan" dashboard.
A pentagon radar chart of 5 stats with a rotating scan sweep, glowing data
polygon, and your monogram at the center. Much more visually distinct
from a plain stat-row card.
Output: stats-card.svg
"""
import os
import math
import requests

USERNAME = "Lochang03"
INITIALS = "LG"
BG = "#0d1117"
GREEN = "#39d353"
GREEN_DIM = "#1f6b32"
CYAN = "#58d3f7"
TEXT = "#c9d1d9"
DIM = "#6e7681"
SIZE = 480
CX, CY = SIZE / 2, SIZE / 2 + 14
R_MAX = 130

HEADERS = {}
token = os.environ.get("GITHUB_TOKEN")
if token:
    HEADERS["Authorization"] = f"token {token}"


def fetch_json(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def get_stats(username):
    user = fetch_json(f"https://api.github.com/users/{username}")
    repos = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100")
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    return {
        "repos": user.get("public_repos", 0),
        "stars": total_stars,
        "followers": user.get("followers", 0),
        "forks": total_forks,
        "following": user.get("following", 0),
    }


AXES = [
    ("REPOS", "repos", 10),
    ("STARS", "stars", 10),
    ("FOLLOWERS", "followers", 20),
    ("FORKS", "forks", 6),
    ("FOLLOWING", "following", 15),
]


def point(angle_deg, radius, cx=CX, cy=CY):
    a = math.radians(angle_deg)
    return cx + radius * math.sin(a), cy - radius * math.cos(a)


def build_svg(username, stats):
    n = len(AXES)
    angles = [i * (360 / n) for i in range(n)]

    # grid rings (pentagon outlines at 25/50/75/100%)
    grid_polys = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(a, R_MAX * frac) for a in angles))
        grid_polys.append(
            f'<polygon points="{pts}" fill="none" stroke="{DIM}" stroke-width="1" opacity="0.5"/>'
        )

    # axis spokes
    spokes = "".join(
        f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-width="1" opacity="0.5"/>'
        for a in angles for x, y in [point(a, R_MAX)]
    )

    # data polygon
    data_pts = []
    label_els = []
    for (label, key, cap), a in zip(AXES, angles):
        val = stats[key]
        frac = min(1.0, val / cap) if cap else 0
        px, py = point(a, R_MAX * max(frac, 0.06))
        data_pts.append((px, py))

        lx, ly = point(a, R_MAX + 34)
        anchor = "middle"
        if math.sin(math.radians(a)) > 0.3:
            anchor = "start"
        elif math.sin(math.radians(a)) < -0.3:
            anchor = "end"
        label_els.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{TEXT}" font-size="11" '
            f'text-anchor="{anchor}" font-weight="bold">{label}</text>'
        )
        # stack the value directly under the label with a fixed vertical
        # gap (not a radial one) so horizontal-ish axes don't collide
        vx, vy = lx, ly + 18
        label_els.append(
            f'<text x="{vx:.1f}" y="{vy:.1f}" fill="{GREEN}" font-size="13" '
            f'text-anchor="{anchor}">{val}</text>'
        )
        # dot on the data point
        label_els.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{GREEN}"/>')

    data_poly_pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_pts)

    svg = [
        f'<svg viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace">',
        '<defs>',
        f'  <radialGradient id="glow" cx="50%" cy="50%" r="50%">',
        f'    <stop offset="0%" stop-color="{GREEN}" stop-opacity="0.35"/>',
        f'    <stop offset="100%" stop-color="{GREEN}" stop-opacity="0"/>',
        f'  </radialGradient>',
        f'  <linearGradient id="sweep" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>',
        f'    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0.35"/>',
        f'  </linearGradient>',
        '</defs>',
        f'<rect width="{SIZE}" height="{SIZE}" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{SIZE-1}" height="{SIZE-1}" fill="none" stroke="#21262d" stroke-width="1"/>',

        # header
        f'<text x="24" y="30" fill="{GREEN}" font-size="13" font-weight="bold">SYSTEM: {username.upper()}</text>',
        f'<circle cx="{SIZE-32}" cy="26" r="4" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/></circle>',
        f'<text x="{SIZE-42}" y="30" fill="{DIM}" font-size="10" text-anchor="end">ONLINE</text>',

        # outer glow behind radar
        f'<circle cx="{CX}" cy="{CY}" r="{R_MAX+10}" fill="url(#glow)"/>',
    ]

    svg.extend(grid_polys)
    svg.append(spokes)

    # rotating scan sweep (clipped to a circle)
    svg.append(f'<clipPath id="radarClip"><circle cx="{CX}" cy="{CY}" r="{R_MAX}"/></clipPath>')
    svg.append(
        f'<g clip-path="url(#radarClip)">'
        f'<g transform="rotate(0 {CX} {CY})">'
        f'<path d="M {CX} {CY} L {CX} {CY-R_MAX} A {R_MAX} {R_MAX} 0 0 1 {CX+R_MAX} {CY} Z" fill="url(#sweep)"/>'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {CX} {CY}" to="360 {CX} {CY}" dur="4s" repeatCount="indefinite"/>'
        f'</g></g>'
    )

    # data polygon with glow + pulse
    svg.append(
        f'<polygon points="{data_poly_pts}" fill="{GREEN}" fill-opacity="0.22" '
        f'stroke="{GREEN}" stroke-width="2">'
        f'<animate attributeName="fill-opacity" values="0.22;0.4;0.22" dur="2.5s" repeatCount="indefinite"/>'
        f'</polygon>'
    )

    svg.extend(label_els)

    # center monogram badge
    svg.append(f'<circle cx="{CX}" cy="{CY}" r="26" fill="{BG}" stroke="{GREEN}" stroke-width="2"/>')
    svg.append(
        f'<text x="{CX}" y="{CY+7}" fill="{GREEN}" font-size="18" font-weight="bold" '
        f'text-anchor="middle">{INITIALS}</text>'
    )

    # footer
    svg.append(
        f'<text x="{SIZE/2}" y="{SIZE-16}" fill="{DIM}" font-size="10" '
        f'text-anchor="middle">scan complete _ github.com/{username}</text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)


if __name__ == "__main__":
    stats = get_stats(USERNAME)
    svg = build_svg(USERNAME, stats)
    with open("stats-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved: stats-card.svg")
    print(stats)