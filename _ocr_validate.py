# -*- coding: utf-8 -*-
"""Validate OCR candidates against markdown text cells and current list."""
import csv
import re
from pathlib import Path
from collections import defaultdict

HANJA_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"
    r"\U00020000-\U0002A6DF\U0002A700-\U0002B73F"
    r"\U0002B740-\U0002B81F\U0002B820-\U0002CEAF]"
)


def extract_hanja(s: str) -> list[str]:
    return HANJA_RE.findall(s)


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
        for ch in extract_hanja(content):
            cell_hanja[hangul].add(ch)
        i += 2

current = defaultdict(set)
with open("인명용한자_현행전체목록.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        keys = list(r.keys())
        hgl, han = r[keys[0]], r[keys[1]]
        if hgl and han:
            current[hgl].add(han)

ocr = {
    0: "㯳",
    1: "跭",
    2: "�].add(han)

ocr = {
    0: "㯳",
    1: "跭",
    2: "𣃽",
    3: "䏧",
    4: "䤥",
    5: "㛦",
    6: "𢻠",
    7: "麐",
    8: "撛",
    9: "砇",
    10: "碈",
    11: "𩔉",
    12: "�砇",
    10: "碈",
    11: "𩔉",
    12: "𩠻",
    13: "樣",
    14: "㠘",
    15: "禼",
    16: "穦",
    17: "晠",
    18: "��",
    19: "忕",
    20: "蛸",
    21: "鎖",
    22: "�
    16: "穦",
    17: "晠",
    18: "𦖤",
    19: "忕",
    20: "蛸",
    21: "鎖",
    22: "䳠",
    23: "睟",
    24: "榺",
    25: "暚",
    26: "㜣",
    27: "䨒",
    28: "琟",
    29: "閠",
    30: "𤨒",
    31: "訢",
    32: "㒚",
    33: "圻",
    34: "��",
    35: "靘",
    36: "佂",
    37: "� 32: "㒚",
    33: "圻",
    34: "𥌾",
    35: "靘",
    36: "佂",
    37: "䚾",
    38: "睭",
    39: "純",
    40: "竴",
    41: "䑐",
    42: "眕",
    43: "釥",
    44: "總",
    45: "琗",
    46: "𡽜",
    47: "䡣",
    48: "焱",
    49: "怰",
    50: "毀",
    51: "惠",
    52: "㜯",
    53: "囍",
    54: "凛",
    55: "𣫙",
}

labels = {}
with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        labels[int(r["idx"])] = r

print("idx hangul ocr in_text? in_current? any_hangul miss_sample")
for idx, ch in sorted(ocr.items()):
    hgl = labels[idx]["hangul"]
    in_text = ch in cell_hanja.get(hgl, set())
    in_cur = ch in current.get(hgl, set())
    any_hgl = [h for h, s in current.items() if ch in s]
    missing = sorted(current.get(hgl, set()) - cell_hanja.get(hgl, set()))
    flag = ""
    if in_text:
        flag = "DUPLICATE_OF_TEXT"
    elif not in_cur:
        flag = "NOT_IN_CURRENT"
    print(
        f"{idx:02d} {hgl} {ch} U+{ord(ch):04X} text={in_text} cur={in_cur} "
        f"any={any_hgl} {flag} miss={''.join(missing[:20])}"
    )
