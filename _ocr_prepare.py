# -*- coding: utf-8 -*-
"""Hash images, convert BMP->PNG for OCR, group duplicates."""
import hashlib
import csv
from pathlib import Path
from collections import defaultdict
from PIL import Image

base = Path("변환결과_markdown")
png_dir = Path("_ocr_work/pngs")
png_dir.mkdir(parents=True, exist_ok=True)

# Load hangul map
hangul_map = {}
with open("_image_hangul_map.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        hangul_map[(row["folder_name"], row["file_name"])] = row["hangul"]

hash_to_items = defaultdict(list)
all_items = []

for folder in sorted([p for p in base.iterdir() if p.is_dir()]):
    img_dir = folder / "images"
    if not img_dir.exists():
        continue
    for img_path in sorted(img_dir.iterdir()):
        if img_path.suffix.lower() not in {".bmp", ".jpg", ".jpeg", ".png"}:
            continue
        data = img_path.read_bytes()
        h = hashlib.md5(data).hexdigest()
        hangul = hangul_map.get((folder.name, img_path.name), "")
        item = {
            "folder": folder.name,
            "file": img_path.name,
            "path": str(img_path),
            "hash": h,
            "hangul": hangul,
            "size": len(data),
        }
        all_items.append(item)
        hash_to_items[h].append(item)

# Convert each unique hash once to PNG
unique_pngs = {}
for h, items in hash_to_items.items():
    src = Path(items[0]["path"])
    out = png_dir / f"{h}.png"
    if not out.exists():
        im = Image.open(src)
        # upscale small glyphs for OCR
        w, ht = im.size
        if w < 64 or ht < 64:
            scale = max(64 // max(w, 1), 64 // max(ht, 1), 3)
            im = im.resize((w * scale, ht * scale), Image.NEAREST)
        # ensure RGB
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.save(out)
    unique_pngs[h] = str(out)

# Classify: cluster vs glyph by size (clusters are large BMPs)
print(f"Total images: {len(all_items)}")
print(f"Unique hashes: {len(hash_to_items)}")

# Show size distribution of unique
sizes = sorted({(h, Path(items[0]["path"]).stat().st_size, items[0]["file"], items[0]["folder"])
                for h, items in hash_to_items.items()}, key=lambda x: -x[1])
print("Largest 15 unique by file size:")
for h, sz, fn, folder in sizes[:15]:
    print(f"  {folder}/{fn} {sz} bytes hash={h[:8]}")

# Write unique list for OCR
with open("_ocr_work/unique_images.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["hash", "png_path", "sample_folder", "sample_file", "byte_size", "count", "folders"])
    for h, items in sorted(hash_to_items.items(), key=lambda x: x[1][0]["folder"] + x[1][0]["file"]):
        folders = sorted({i["folder"] for i in items})
        w.writerow([
            h,
            unique_pngs[h],
            items[0]["folder"],
            items[0]["file"],
            Path(items[0]["path"]).stat().st_size,
            len(items),
            "|".join(folders),
        ])

with open("_ocr_work/all_images.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["folder", "file", "path", "hash", "hangul", "size"])
    w.writeheader()
    w.writerows(all_items)

print("Wrote _ocr_work/unique_images.csv and all_images.csv")
