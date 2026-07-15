# -*- coding: utf-8 -*-
import csv
import re
from pathlib import Path
from collections import defaultdict
from _ocr_results_raw import OCR_CPS

HANJA_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"
    r"\U00020000-\U0002A6DF\U0002A700-\U0002B73F"
    r"\U0002B740-\U0002B81F\U0002B820-\U0002CEAF]"
)

md = Path("변환결과_markdown/2119/규칙제2119호.md").read_text(encoding="utf-8")
cell_hanja = defaultdict(set)
rows = re.split(r"<tr[^>]*>", md, flags=re.I)
for row in rows:
    cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
    i = 0
    while i + 1 < len(cells):
        hangul = re.sub(r"<[^>]+>", "", cells[i]).strip()
        content = re.sub(r"<img[^>]*>", "", cells[i + 1])
        content = re.sub(r"\[이미지:[^\]]*\]", "", content)
        for ch in HANJA_RE.findall(content):
            cell_hanja[hangul].add(ch)
        i += 2

current = defaultdict(set)
unicode_to_hangul = defaultdict(list)
with open("인명용한자_현행전체목록.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        keys = list(r.keys())
        hgl, han = r[keys[0]], r[keys[1]]
        if hgl and han:
            current[hgl].add(han)
            unicode_to_hangul[han].append(hgl)

labels = {}
with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        labels[int(r["idx"])] = r

problems = []
ok = []
for idx, cp in sorted(OCR_CPS.items()):
    ch = chr(cp)
    hgl = labels[idx]["hangul"]
    in_text = ch in cell_hanja.get(hgl, set())
    in_cur = ch in current.get(hgl, set())
    any_hgl = unicode_to_hangul.get(ch, [])
    missing = sorted(current.get(hgl, set()) - cell_hanja.get(hgl, set()))
    status = "OK" if in_cur and not in_text else ("DUP_TEXT" if in_text else "CHECK")
    line = (
        f"{idx:02d} {hgl} {ch} U+{cp:04X} {status} "
        f"cur={in_cur} any={any_hgl} miss={''.join(missing[:25])}"
    )
    print(line)
    if status != "OK":
        problems.append((idx, hgl, ch, status, missing))

print("\n=== PROBLEMS ===", len(problems))
for p in problems:
    print(p[0], p[1], p[2], p[3], "missing_candidates=", "".join(p[4][:40]))
