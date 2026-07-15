# -*- coding: utf-8 -*-
import csv
from collections import defaultdict
from pathlib import Path
from unicodedata import name as uname

current = defaultdict(set)
han_to_h = defaultdict(list)
with open("인명용한자_현행전체목록.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        keys = list(r.keys())
        hgl, han = r[keys[0]], r[keys[1]]
        current[hgl].add(han)
        han_to_h[han].append(hgl)

candidates = [
    ("跭", 0x8DEE),
    ("跫", 0x8E0F),
    ("踭", 0x8DED),
    ("䏧", 0x45E7),
    ("𦙏", 0x2664F),
    ("𡖔", 0x21594),
    ("麐", 0x9E90),
    ("麟", 0x9E9F),
    ("𪊭", 0x2A2AD),
    ("碈", 0x7888),
    ("䃉", 0x40C9),
    ("䚾", 0x46BE),
    ("䛘", 0x46D8),
    ("飪", 0x98EA),
    ("凛", 0x51DB),
    ("凜", 0x51DC),
    ("㯳", 0x3BF3),
    ("檠", 0x7C23),
]

lines = []
for name, cp in candidates:
    ch = chr(cp)
    lines.append(
        f"{name} U+{cp:04X} hanguls={han_to_h.get(ch, [])}"
    )

for hgl in ["강", "나", "린", "민", "임", "름"]:
    lines.append(f"\n=== ALL current[{hgl}] rare/relevant ===")
    for ch in sorted(current[hgl], key=ord):
        cp = ord(ch)
        try:
            n = uname(ch)
        except ValueError:
            n = "?"
        # print more selectively
        if hgl == "강" and (0x8B00 <= cp <= 0x8F40 or cp >= 0x20000 or "FOOT" in n):
            lines.append(f"  {ch} U+{cp:04X} {n}")
        elif hgl == "나" and (
            0x43E0 <= cp <= 0x4600
            or 0x80A0 <= cp <= 0x8200
            or cp >= 0x20000
            or "FLESH" in n
            or "MEAT" in n
        ):
            lines.append(f"  {ch} U+{cp:04X} {n}")
        elif hgl == "린" and (0x9E80 <= cp <= 0x9EFF or cp >= 0x20000 or "DEER" in n):
            lines.append(f"  {ch} U+{cp:04X} {n}")
        elif hgl == "민" and (0x40C0 <= cp <= 0x4100 or 0x7800 <= cp <= 0x7900):
            lines.append(f"  {ch} U+{cp:04X} {n}")
        elif hgl == "임" and (0x46A0 <= cp <= 0x4700 or 0x8A00 <= cp <= 0x8C00):
            lines.append(f"  {ch} U+{cp:04X} {n}")
        elif hgl == "름":
            lines.append(f"  {ch} U+{cp:04X} {n}")

Path("_ocr_work/fix_candidates.txt").write_text("\n".join(lines), encoding="utf-8")
print("wrote", len(lines), "lines")
