# -*- coding: utf-8 -*-
import re
from pathlib import Path
from collections import Counter

base = Path("변환결과_markdown")
results = []

for folder in sorted([p for p in base.iterdir() if p.is_dir()]):
    mds = list(folder.glob("*.md"))
    if not mds:
        continue
    text = mds[0].read_text(encoding="utf-8")

    rows = re.split(r"<tr[^>]*>", text, flags=re.I)
    for row in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        i = 0
        while i + 1 < len(cells):
            hangul = re.sub(r"<[^>]+>", "", cells[i]).strip()
            content = cells[i + 1]
            imgs = re.findall(r'src=["\']([^"\']+)["\']', content)
            imgs += re.findall(r"!\[[^\]]*\]\(([^)]+)\)", content)
            for img in imgs:
                fname = Path(img).name
                results.append((folder.name, fname, hangul))
            i += 2

    md_imgs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    for img in md_imgs:
        fname = Path(img).name
        if not any(r[0] == folder.name and r[1] == fname for r in results):
            results.append((folder.name, fname, ""))

print(f"Total mapped: {len(results)}")
print("By folder:", Counter(r[0] for r in results))
print("Empty hangul:", sum(1 for r in results if not r[2]))
print("Sample 2119:")
for r in results:
    if r[0] == "2119":
        print(r)

out = Path("_image_hangul_map.csv")
with out.open("w", encoding="utf-8", newline="") as f:
    f.write("folder_name,file_name,hangul\n")
    for folder, fname, hangul in results:
        f.write(f"{folder},{fname},{hangul}\n")
print("Wrote", out)
