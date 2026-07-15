# -*- coding: utf-8 -*-
"""Build final CSV: folder_name,file_name,hangul,hanja"""
import csv
from pathlib import Path
from PIL import Image
from _ocr_results_raw import OCR_CPS

# hash -> hanja for glyphs
hash_to_hanja = {}
labels = {}
with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        idx = int(r["idx"])
        labels[idx] = r
        hash_to_hanja[r["hash"]] = chr(OCR_CPS[idx])

# hangul map from markdown
hangul_map = {}
with open("_image_hangul_map.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        hangul_map[(r["folder_name"], r["file_name"])] = r["hangul"]

# all images
all_rows = []
with open("_ocr_work/all_images.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        all_rows.append(r)

out_rows = []
cluster_meta = []
for r in all_rows:
    folder, fname, h = r["folder"], r["file"], r["hash"]
    hangul = hangul_map.get((folder, fname), r.get("hangul", ""))
    if h in hash_to_hanja:
        out_rows.append([folder, fname, hangul, hash_to_hanja[h]])
    else:
        # cluster table image — placeholder row; filled later
        cluster_meta.append(r)
        out_rows.append([folder, fname, hangul, ""])

out_path = Path("변환결과_markdown/이미지한자_OCR결과.csv")
with out_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["folder_name", "file_name", "hangul", "hanja"])
    w.writerows(out_rows)

# also refresh glyph_ocr.csv
with open("_ocr_work/glyph_ocr.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["idx", "hash", "hangul", "hanja", "unicode_hex"])
    for idx, cp in sorted(OCR_CPS.items()):
        lab = labels[idx]
        w.writerow([idx, lab["hash"], lab["hangul"], chr(cp), f"U+{cp:04X}"])

print(f"Wrote {out_path} rows={len(out_rows)} filled={sum(1 for r in out_rows if r[3])} clusters={len(cluster_meta)}")

# Prepare downscaled previews for cluster OCR
preview_dir = Path("_ocr_work/cluster_preview")
preview_dir.mkdir(parents=True, exist_ok=True)
seen = set()
for r in cluster_meta:
    if r["hash"] in seen:
        continue
    seen.add(r["hash"])
    src = Path(r["path"])
    im = Image.open(src).convert("RGB")
    # downscale for vision while keeping readability
    w, h = im.size
    scale = min(1.0, 1600 / max(w, h))
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = preview_dir / f"{r['folder']}_{r['file']}.png"
    im.save(out, optimize=True)
    print("preview", out, im.size)
