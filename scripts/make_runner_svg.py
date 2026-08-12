"""
Bonus: Self-playing pixel-art runner scene.
Loops indefinitely — no score counter, no end caption, just a continuous
run-and-jump animation.
Output: runner-scene.svg
"""

WIDTH = 860
HEIGHT = 160
BG = "#0d1117"
GROUND_Y = 120
PIXEL = "#39d353"
OBSTACLE_COLOR = "#f85149"

RUN_DURATION = 4.5  # seconds for one full pass across the screen

def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" shape-rendering="crispEdges">'
    )
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>')

    parts.append(
        f'<line x1="0" y1="{GROUND_Y}" x2="{WIDTH}" y2="{GROUND_Y}" '
        f'stroke="#30363d" stroke-width="2" stroke-dasharray="6,6"/>'
    )

    obstacle_positions = [280, 480, 650]
    for ox in obstacle_positions:
        parts.append(
            f'<rect x="{ox}" y="{GROUND_Y-24}" width="14" height="24" fill="{OBSTACLE_COLOR}"/>'
        )

    runner_parts = [
        '<rect id="legL" x="-6" y="-16" width="6" height="16" fill="{c}"/>',
        '<rect id="legR" x="0" y="-16" width="6" height="16" fill="{c}"/>',
        '<rect x="-7" y="-34" width="14" height="18" fill="{c}"/>',
        '<rect x="-5" y="-44" width="10" height="10" fill="{c}"/>',
    ]
    runner_svg = "".join(p.format(c=PIXEL) for p in runner_parts)

    run_span = (WIDTH - 40)
    jump_events = [ox / run_span for ox in obstacle_positions]
    jump_height = 30
    jump_half_width = 0.06

    parts.append('<g id="runner-x">')
    parts.append(
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0,0" to="{run_span},0" '
        f'begin="0s" dur="{RUN_DURATION}s" repeatCount="indefinite" calcMode="linear"/>'
    )
    parts.append(f'<g id="runner-y" transform="translate(0,{GROUND_Y})">')
    parts.append(runner_svg)

    for frac in jump_events:
        t_start = max(0, frac - jump_half_width) * RUN_DURATION
        t_end = min(1, frac + jump_half_width) * RUN_DURATION
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'additive="sum" '
            f'values="0,0; 0,{-jump_height}; 0,0" '
            f'keyTimes="0;0.5;1" '
            f'keySplines="0.3 0 0.7 1;0.3 0 0.7 1" '
            f'calcMode="spline" '
            f'begin="{t_start:.2f}s" dur="{t_end - t_start:.2f}s" '
            f'repeatCount="indefinite"/>'
        )

    parts.append('</g>')
    parts.append('</g>')

    parts.append(
        f'<style>'
        f'#legL {{ animation: legswap 0.3s steps(2) infinite; }}'
        f'#legR {{ animation: legswap 0.3s steps(2) infinite reverse; }}'
        f'@keyframes legswap {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}'
        f'</style>'
    )

    parts.append('</svg>')
    return "\n".join(parts)

if __name__ == "__main__":
    svg = build_svg()
    with open("runner-scene.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved: runner-scene.svg (looping version, no score)")