"""
Step 3b: Convert the prepped grayscale photo into a self-typing ASCII SVG.
Reads: source-prepped.png
Writes: avi-ascii.svg (self-contained, animated via SMIL)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"

GRID_COLS = 100
GRID_ROWS = 53

FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0

FILL_COLOR = "#9da5b4"  # monochrome light gray

def image_to_ascii_grid(image_path: str, cols: int = GRID_COLS, rows: int = GRID_ROWS):
    img = Image.open(image_path).convert("L")
    img = img.resize((cols, rows), Image.LANCZOS)
    arr = np.array(img)

    ramp_len = len(RAMP)
    grid = []
    for row in arr:
        line = ""
        for pixel in row:
            # pixel 255 (white/bright) -> index 0 (space), pixel 0 (dark) -> last char
            idx = int((255 - pixel) / 255 * (ramp_len - 1))
            line += RAMP[idx]
        grid.append(line)
    return grid

def build_svg(grid, output_path: str):
    cols = len(grid[0])
    rows = len(grid)
    width = cols * CHAR_W
    height = rows * CHAR_H

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width:.1f} {height:.1f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="monospace" font-size="{FONT_SIZE}">'
    )
    svg_parts.append(f'<rect width="{width:.1f}" height="{height:.1f}" fill="#0d1117"/>')

    row_delay_step = 0.05  # stagger between rows
    wipe_duration = 0.9    # how long each row's wipe takes

    for r, line in enumerate(grid):
        y = (r + 1) * CHAR_H
        row_id = f"row{r}"
        clip_id = f"clip{r}"
        delay = r * row_delay_step

        escaped = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(f'  <rect x="0" y="{y - CHAR_H:.1f}" width="0" height="{CHAR_H:.1f}">')
        svg_parts.append(
            f'    <animate attributeName="width" from="0" to="{width:.1f}" '
            f'begin="{delay:.2f}s" dur="{wipe_duration}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.4 0 0.2 1"/>'
        )
        svg_parts.append(f'  </rect>')
        svg_parts.append(f'</clipPath>')

        svg_parts.append(f'<g clip-path="url(#{clip_id})">')
        svg_parts.append(
            f'  <text x="0" y="{y:.1f}" fill="{FILL_COLOR}" xml:space="preserve">{escaped}</text>'
        )
        svg_parts.append(f'</g>')

    svg_parts.append('</svg>')

    Path(output_path).write_text("\n".join(svg_parts), encoding="utf-8")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    grid = image_to_ascii_grid(input_path)
    build_svg(grid, "avi-ascii.svg")