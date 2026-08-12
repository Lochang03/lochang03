"""
Step 3a: Prep the source photo for ASCII conversion.
- Removes background (rembg)
- Boosts local contrast (CLAHE)
- Composites onto pure white
Output: source-prepped.png (grayscale)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

def prep_photo(input_path: str, output_path: str = "source-prepped.png"):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    print("Removing background...")
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)

    rgba = Image.open(__import__("io").BytesIO(output_bytes)).convert("RGBA")

    print("Compositing onto white background...")
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)

    print("Boosting local contrast (CLAHE)...")
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    Image.fromarray(contrasted).save(output_path)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <input-photo>")
        sys.exit(1)
    prep_photo(sys.argv[1])