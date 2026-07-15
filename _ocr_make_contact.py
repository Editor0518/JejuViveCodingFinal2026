# -*- coding: utf-8 -*-
"""Make labeled contact sheets of unique glyph images for batch OCR."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

glyph_rows = []
with open("_ocr_work/unique_images.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if int(r["byte_size"]) < 100000:
            glyph_rows.append(r)

# Load hangul for sample folder/file
hangul = {}
with open("_image_hangul_map.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        hangul[(r["folder_name"], r["file_name"])] = r["hangul"]

cell_w, cell_h = 160, 180
cols = 8
rows_n = (len(glyph_rows) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cell_w, rows_n * cell_h), "white")
draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("malgun.ttf", 14)
except Exception:
    font = ImageFont.load_default()

labels = []
for idx, r in enumerate(glyph_rows):
    col, row = idx % cols, idx // cols
    x0, y0 = col * cell_w, row * cell_h
    im = Image.open(r["png_path"]).convert("RGB")
    # fit into 100x100 box
    im.thumbnail((100, 100), Image.NEAREST)
    px = x0 + (cell_w - im.width) // 2
    py = y0 + 20
    sheet.paste(im, (px, py))
    hgl = hangul.get((r["sample_folder"], r["sample_file"]), "")
    label = f"{idx:02d}:{r['sample_file'][:12]}\n{hgl}"
    draw.text((x0 + 4, y0 + 125), label, fill="black", font=font)
    draw.rectangle([x0, y0, x0 + cell_w - 1, y0 + cell_h - 1], outline="#cccccc")
    labels.append({
        "idx": idx,
        "hash": r["hash"],
        "sample_folder": r["sample_folder"],
        "sample_file": r["sample_file"],
        "hangul": hgl,
        "png_path": r["png_path"],
    })

out = Path("_ocr_work/glyph_contact.png")
sheet.save(out)
print("Wrote", out, "size", sheet.size)

with open("_ocr_work/glyph_labels.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(labels[0].keys()))
    w.writeheader()
    w.writerows(labels)
print("Wrote glyph_labels.csv", len(labels))
