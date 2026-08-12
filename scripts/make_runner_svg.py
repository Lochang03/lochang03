"""
Bonus: Self-playing pixel-art runner scene.
No real interactivity (GitHub strips JS) — plays once, freezes on HIGH SCORE.
Output: runner-scene.svg
"""

WIDTH = 860
HEIGHT = 160
BG = "#0d1117"
GROUND_Y = 120
PIXEL = "#39d353"
OBSTACLE_COLOR = "#f85149"
TEXT_COLOR = "#c9d1d9"

RUN_DURATION = 4.5  # seconds for the full run across the screen

def build_svg() -> str:
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" shape-rendering="crispEdges">'
    )
    parts.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>')

    # Ground line
    parts.append(
        f'<line x1="0" y1="{GROUND_Y}" x2="{WIDTH}" y2="{GROUND_Y}" '
        f'stroke="#30363d" stroke-width="2" stroke-dasharray="6,6"/>'
    )

    # Obstacles (simple blocks) at fixed x positions along the track
    obstacle_positions = [280, 480, 650]
    for ox in obstacle_positions:
        parts.append(
            f'<rect x="{ox}" y="{GROUND_Y-24}" width="14" height="24" fill="{OBSTACLE_COLOR}"/>'
        )

    # Runner: simple blocky figure built from rects, grouped so we can animate the group
    # Origin (0,0) of the group = bottom-center of the figure at ground level
    runner_parts = [
        # legs (two alternating rects for a simple running look via animate)
        '<rect id="legL" x="-6" y="-16" width="6" height="16" fill="{c}"/>',
        '<rect id="legR" x="0" y="-16" width="6" height="16" fill="{c}"/>',
        # body
        '<rect x="-7" y="-34" width="14" height="18" fill="{c}"/>',
        # head
        '<rect x="-5" y="-44" width="10" height="10" fill="{c}"/>',
    ]
    runner_svg = "".join(p.format(c=PIXEL) for p in runner_parts)

# Compute jump timing: each obstacle's x-position maps to a time fraction
    # of the total run, so the jump peak lines up with the obstacle.
    run_span = (WIDTH - 40)
    jump_events = []  # (time_fraction, obstacle_x)
    for ox in obstacle_positions:
        frac = ox / run_span
        jump_events.append(frac)

    jump_height = 30
    jump_half_width = 0.06  # fraction of total duration each jump takes to rise/fall

    # Build keyTimes/keyPoints style animation using multiple <animate> segments
    # for simplicity: one <animate> per obstacle jump, all on the same 'y' via
    # a nested translate group, plus the outer horizontal translate.
    parts.append(f'<g id="runner-x">')
    parts.append(
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0,0" to="{run_span},0" '
        f'begin="0s" dur="{RUN_DURATION}s" fill="freeze" calcMode="linear"/>'
    )
    parts.append(f'<g id="runner-y" transform="translate(0,{GROUND_Y})">')
    parts.append(runner_svg)

    # One vertical bounce animation per obstacle
    for frac in jump_events:
        t_start = max(0, frac - jump_half_width) * RUN_DURATION
        t_peak = frac * RUN_DURATION
        t_end = min(1, frac + jump_half_width) * RUN_DURATION
        parts.append(
            f'<animateTransform attributeName="transform" type="translate" '
            f'additive="sum" '
            f'values="0,0; 0,{-jump_height}; 0,0" '
            f'keyTimes="0;0.5;1" '
            f'keySplines="0.3 0 0.7 1;0.3 0 0.7 1" '
            f'calcMode="spline" '
            f'begin="{t_start:.2f}s" dur="{t_end - t_start:.2f}s" fill="freeze"/>'
        )

    parts.append('</g>')  # runner-y
    parts.append('</g>')  # runner-x    # Simple leg-swap animation to fake a running motion (toggle visibility)
    parts.append(
        f'<style>'
        f'#legL {{ animation: legswap 0.3s steps(2) infinite; }}'
        f'#legR {{ animation: legswap 0.3s steps(2) infinite reverse; }}'
        f'@keyframes legswap {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} }}'
        f'</style>'
    )

    # Score text ticking up, then freezing
# Score text ticking up in discrete steps, then freezing at a final value
    final_score = 480
    steps = 24
    score_values = ";".join(str(int(final_score * i / steps)) for i in range(steps + 1))
# Score "ticking up" via opacity-swapped pre-rendered numbers (no textContent
    # animation needed — same technique as the ASCII portrait's row reveal).
    final_score = 480
    steps = 12
    step_dur = RUN_DURATION / steps

    score_group = ['<g>']
    for i in range(steps + 1):
        value = int(final_score * i / steps)
        t_show = i * step_dur
        t_hide = (i + 1) * step_dur

        score_group.append(
            f'<text x="20" y="30" fill="{TEXT_COLOR}" font-size="16" opacity="0">'
            f'SCORE: {value}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{t_show:.2f}s" dur="0.01s" fill="freeze"/>'
        )
        if i < steps:
            score_group.append(
                f'<animate attributeName="opacity" from="1" to="0" '
                f'begin="{t_hide:.2f}s" dur="0.01s" fill="freeze"/>'
            )
        score_group.append('</text>')
    score_group.append('</g>')
    parts.append("".join(score_group))    # End caption, hidden then revealed at the end of the run
    caption_x = WIDTH / 2 - 70
    caption_y = 60
    parts.append(
        f'<text x="{caption_x}" y="{caption_y}" fill="#ffbd2e" font-size="22" '
        f'font-weight="bold" opacity="0">HIGH SCORE!'
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{RUN_DURATION}s" dur="0.6s" fill="freeze"/>'
        f'</text>'
    )

    parts.append('</svg>')
    return "\n".join(parts)

if __name__ == "__main__":
    svg = build_svg()
    with open("runner-scene.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("Saved: runner-scene.svg")