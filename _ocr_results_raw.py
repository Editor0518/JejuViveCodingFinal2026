# -*- coding: utf-8 -*-
"""OCR results as Unicode code points."""
import csv

OCR_CPS = {
    0: 0x3BF3,  # gyeong
    1: 0x8DED,  # gang; image is foot+feng
    2: 0x230FD,  # na
    3: 0x43E7,  # na; moon+duo
    4: 0x4925,  # gwi
    5: 0x36E6,  # ram
    6: 0x22EE0,  # ri
    7: 0x2A2AD,  # rin; deer+lin variant (麟 already in text as compat)
    8: 0x649B,  # rin
    9: 0x7807,  # min
    10: 0x40C9,  # min; stone+min
    11: 0x29509,  # min
    12: 0x2983B,  # byeol
    13: 0x6A23,  # sang
    14: 0x3818,  # seo
    15: 0x79BC,  # seol
    16: 0x7A66,  # bin
    17: 0x6660,  # seong
    18: 0x265A4,  # seong
    19: 0x5FD5,  # se
    20: 0x86F8,  # so
    21: 0x9396,  # swae
    22: 0x4CE0,  # su
    23: 0x775F,  # su
    24: 0x69BA,  # seung
    25: 0x669A,  # yo
    26: 0x3723,  # yeon
    27: 0x4A12,  # u
    28: 0x741F,  # yu
    29: 0x95A0,  # yun
    30: 0x24A12,  # eun
    31: 0x8A22,  # eun
    32: 0x349A,  # eun
    33: 0x573B,  # eun
    34: 0x2533E,  # eung
    35: 0x9758,  # jeong
    36: 0x4F42,  # jeong
    37: 0x46D8,  # im; speech+im
    38: 0x776D,  # ju
    39: 0x7D14,  # jun
    40: 0x7AF4,  # jun
    41: 0x4450,  # jin
    42: 0x7715,  # jin
    43: 0x91E5,  # cho
    44: 0x7E3D,  # chong
    45: 0x7417,  # chae
    46: 0x21F5C,  # han
    47: 0x4863,  # heon
    48: 0x7131,  # hyeok
    49: 0x6030,  # hyeon
    50: 0x6BC0,  # hwe
    51: 0x60E0,  # hye
    52: 0x372F,  # hui
    53: 0x56CD,  # hui
    54: 0x51DB,  # reum; 2181 has 凜 in text, image is 凛
    55: 0x23AD9,  # ye
}

if __name__ == "__main__":
    labels = {}
    with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            labels[int(r["idx"])] = r

    with open("_ocr_work/glyph_ocr.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["idx", "hash", "hangul", "hanja", "unicode_hex"])
        for idx, cp in sorted(OCR_CPS.items()):
            lab = labels[idx]
            ch = chr(cp)
            w.writerow([idx, lab["hash"], lab["hangul"], ch, f"U+{cp:04X}"])
    print("wrote _ocr_work/glyph_ocr.csv")
