"""
Step 3 (revised): Render initials as a clean block-letter ASCII monogram.
No photo needed — text is drawn directly, then converted to ASCII the same
way the portrait pipeline does, and animated with the same self-typing wipe.
Output: avi-ascii.svg (same filename/slot as the portrait, so README needs no change)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

RAMP = " .`:-=+*cs#%@"
GRID_COLS = 60
GRID_ROWS = 40
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL_COLOR = "#9da5b4"
INITIALS = "GL"

def render_initials_image(text: str, size=(600, 400)) -> Image.Image:
    img = Image.new("L", size, color=255)  # white background
    draw = ImageDraw.Draw(img)

    # Try a bold system font; fall back to default if unavailable
    font = None
    for candidate in [
        "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf",
    ]:
        try:
            font = ImageFont.truetype(candidate, 260)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - tw) / 2 - bbox[0]
    y = (size[1] - th) / 2 - bbox[1]
    draw.text((x, y), text, fill=0, font=font)  # black text on white
    return img

def image_to_ascii_grid(img: Image.Image, cols: int = GRID_COLS, rows: int = GRID_ROWS):
    img = img.resize((cols, rows), Image.LANCZOS)
    arr = np.array(img)
    ramp_len = len(RAMP)
    grid = []
    for row in arr:
        line = ""
        for pixel in row:
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

    row_delay_step = 0.06
    wipe_duration = 0.9

    for r, line in enumerate(grid):
        y = (r + 1) * CHAR_H
        clip_id = f"clip{r}"
        delay = r * row_delay_step
        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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
    img = render_initials_image(INITIALS)
    grid = image_to_ascii_grid(img)
    build_svg(grid, "avi-ascii.svg")