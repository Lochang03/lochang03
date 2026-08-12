"""
Step 4: Build a neofetch-style info card SVG.
Set STATIC=1 env var to emit a frozen frame (for local previews).
Output: info-card.svg
"""
import os

WIDTH = 490
HEIGHT = 300
BG = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#58a6ff"
KEY_COLOR = "#7ee787"
VAL_COLOR = "#c9d1d9"
FONT = "monospace"

FIELDS = [
    ("Role", "AI & ML Engineering Student"),
    ("Now", "Building Multimodal RAG Chatbot (GenAI)"),
    ("Learning", "Machine Learning, DSA"),
    ("Stack", "Python, C++, Flask, OpenCV, NumPy, Pandas"),
    ("Cert", "Pursuing DRISHTI CPS (IIT Indore)"),
    ("CGPA", "9.09 (Sem 3)"),
]
STATIC = os.environ.get("STATIC") == "1"

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}" font-size="14">'
    )
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')

    # Title bar
    parts.append(f'<circle cx="24" cy="24" r="6" fill="#ff5f56"/>')
    parts.append(f'<circle cx="44" cy="24" r="6" fill="#ffbd2e"/>')
    parts.append(f'<circle cx="64" cy="24" r="6" fill="#27c93f"/>')
    parts.append(
        f'<text x="20" y="55" fill="{TITLE_COLOR}" font-size="16" font-weight="bold">'
        f'lochan@github ~ $ neofetch</text>'
    )
    parts.append(f'<line x1="20" y1="66" x2="{WIDTH-20}" y2="66" stroke="{BORDER}" stroke-width="1"/>')

    row_h = 38
    start_y = 100
    fade_dur = 0.5
    stagger = 0.35

    for i, (key, val) in enumerate(FIELDS):
        y = start_y + i * row_h
        delay = i * stagger
        key_esc = esc(key)
        val_esc = esc(val)

        if STATIC:
            opacity_attr = ''
            transform = ''
            anim = ''
        else:
            opacity_attr = 'opacity="0"'
            transform = f'transform="translate(-12,0)"'
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="{fade_dur}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-12,0" to="0,0" begin="{delay:.2f}s" dur="{fade_dur}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.3 0 0.2 1"/>'
            )

        parts.append(f'<g {opacity_attr} {transform}>')
        parts.append(
            f'<text x="20" y="{y}" fill="{KEY_COLOR}" font-weight="bold">{key_esc}:</text>'
        )
        parts.append(
            f'<text x="140" y="{y}" fill="{VAL_COLOR}">{val_esc}</text>'
        )
        parts.append(anim)
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)

if __name__ == "__main__":
    svg = build_svg()
    with open("info-card.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved: info-card.svg" + (" (static)" if STATIC else ""))