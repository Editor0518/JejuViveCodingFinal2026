# -*- coding: utf-8 -*-
"""Build 이미지한자_OCR결과.csv in example format: folder,file,hangul,hanja (1 hanja/row)."""
import csv
import re
from pathlib import Path
from collections import defaultdict, Counter
from _ocr_results_raw import OCR_CPS

HANJA_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF"
    r"\U00020000-\U0002A6DF\U0002A700-\U0002B73F"
    r"\U0002B740-\U0002B81F\U0002B820-\U0002CEAF]"
)

hangul_map = {}
with open("_image_hangul_map.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        hangul_map[(r["folder_name"], r["file_name"])] = r["hangul"]

hash_to_hanja = {}
with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        hash_to_hanja[r["hash"]] = chr(OCR_CPS[int(r["idx"])])

hanja_by_hangul = defaultdict(list)


def add_hanja(hgl: str, chars: str):
    if not hgl:
        return
    seen = set(hanja_by_hangul[hgl])
    for ch in HANJA_RE.findall(chars):
        if ch not in seen:
            hanja_by_hangul[hgl].append(ch)
            seen.add(ch)


for folder in ["2119", "2181", "2188", "2227", "2242"]:
    md = next(Path(f"변환결과_markdown/{folder}").glob("*.md")).read_text(encoding="utf-8")
    for row in re.split(r"<tr[^>]*>", md, flags=re.I):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.I | re.S)
        i = 0
        while i + 1 < len(cells):
            hgl = re.sub(r"<[^>]+>", "", cells[i]).strip()
            content = re.sub(r"<img[^>]*>", "", cells[i + 1])
            content = re.sub(r"\[이미지:[^\]]*\]", "", content)
            add_hanja(hgl, content)
            i += 2

with open("_ocr_work/glyph_labels.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add_hanja(r["hangul"], chr(OCR_CPS[int(r["idx"])]))

CLUSTER_PAGE_HANGUL = {
    "image_001.bmp": [
        "가", "각", "간", "갈", "감", "갑", "강", "개", "객", "갱", "갹", "거", "건", "걸", "검", "겁",
        "견", "결", "겸", "경", "계", "고", "곡", "곤", "골", "공", "곶", "과", "곽", "관", "괄", "광",
    ],
    "image_002.bmp": [
        "게", "격", "굉", "교", "구", "국", "군", "굴", "궁", "권", "궐", "궤", "귀", "규", "균", "귤",
        "극", "근", "글", "금", "괘", "괴", "길", "김", "끽", "나", "난", "날", "남", "납", "낭", "내",
        "년", "념", "녕", "노", "농", "뇨", "눈", "눌",
    ],
    "image_003.bmp": [
        "급", "긍", "기", "다", "단", "달", "담", "답", "당", "대", "댁", "도", "독", "돈", "돌", "동",
        "두", "둔", "등", "뉴", "니", "닉", "람", "랍", "랑", "래", "량", "려", "력", "련", "렬", "렴",
        "령", "례", "로", "록", "롱", "뢰", "료",
    ],
    "image_004.bmp": [
        "라", "락", "란", "랄", "률", "륵", "름", "릉", "리", "린", "림", "립", "마", "막", "만", "말",
        "망", "매", "맥", "맹", "멱", "루", "류", "륙", "륜", "목", "몰", "몽", "묘", "무", "문", "물",
        "미", "민", "밀", "박", "반", "발", "방", "배", "백", "번",
    ],
    "image_005.bmp": [
        "면", "멸", "명", "몌", "모", "별", "병", "보", "복", "볼", "봉", "부", "분", "불", "붕", "비",
        "빈", "벌", "범", "법", "벽", "변", "삼", "삽", "상", "새", "색", "생", "서", "석", "선", "설",
        "섬", "섭",
    ],
    "image_006.bmp": [
        "빙", "사", "삭", "산", "살", "솔", "송", "쇄", "쇠", "수", "숙", "순", "술", "숭", "슬", "습",
        "승", "시", "성", "세", "소", "속", "손", "악", "안", "알", "암", "압", "앙", "애", "액", "앵",
        "야", "약", "양", "어",
    ],
    "image_007.bmp": [
        "식", "신", "실", "심", "십", "아", "여", "역", "연", "열", "염", "엽", "영", "예", "오", "옥",
        "온", "억", "언", "얼", "엄", "업", "욕", "용", "우", "욱", "운", "울", "웅", "원", "월", "위",
        "유",
    ],
    "image_008.bmp": [
        "올", "옹", "와", "완", "왕", "왜", "외", "요", "응", "의", "이", "익", "인", "일", "임", "육",
        "윤", "율", "융", "은", "을", "음", "읍", "전", "절", "점", "접", "정", "제", "조",
    ],
    "image_009.bmp": [
        "입", "잉", "자", "작", "잔", "잠", "장", "재", "쟁", "저", "적", "지", "직", "진", "질", "짐",
        "집", "족", "졸", "종", "좌", "주", "죽", "준", "줄", "즐", "즙", "증", "청", "체", "초", "촉",
        "촌", "총",
    ],
    "image_010.bmp": [
        "징", "차", "착", "찬", "찰", "참", "창", "채", "책", "처", "척", "천", "철", "첨", "첩", "칭",
        "쾌", "타", "탁", "탄", "탐", "촬", "최", "추", "축", "춘", "출", "충", "췌", "취", "측", "치",
        "칙", "칠", "침", "칩", "팔", "패", "팽", "퍅", "편", "폄",
    ],
    "image_011.bmp": [
        "탑", "탕", "태", "택", "탱", "터", "토", "통", "퇴", "투", "특", "틈", "파", "판", "함", "합",
        "항", "해", "핵", "행", "평", "폐", "포", "폭", "표", "품", "풍", "피", "필", "핍", "하", "학",
        "한", "할", "홀", "홍", "화", "확", "환", "활",
    ],
    "image_012.bmp": [
        "향", "허", "헌", "헐", "혁", "현", "혈", "협", "형", "혜", "호", "혹", "혼", "흔", "흘", "흠",
        "황", "회", "횡", "효", "후", "훈", "훙", "훤", "훼", "휘", "휴", "휼", "흉", "흡", "희", "힐",
    ],
}

rows = []
with open("_ocr_work/all_images.csv", encoding="utf-8") as f:
    all_images = list(csv.DictReader(f))

for r in all_images:
    folder, fname, h = r["folder"], r["file"], r["hash"]
    hangul = hangul_map.get((folder, fname), "")
    if h in hash_to_hanja:
        rows.append([folder, fname, hangul, hash_to_hanja[h]])
        continue
    for hgl in CLUSTER_PAGE_HANGUL.get(fname, []):
        chars = hanja_by_hangul.get(hgl, [])
        if not chars:
            rows.append([folder, fname, hgl, ""])
        else:
            for ch in chars:
                rows.append([folder, fname, hgl, ch])

out_path = Path("변환결과_markdown/이미지한자_OCR결과.csv")
with out_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["folder_name", "file_name", "hangul", "hanja"])
    w.writerows(rows)

# one-row-per-image summary also kept for convenience
per_image = []
for r in all_images:
    folder, fname, h = r["folder"], r["file"], r["hash"]
    hangul = hangul_map.get((folder, fname), "")
    if h in hash_to_hanja:
        per_image.append([folder, fname, hangul, hash_to_hanja[h]])
    else:
        chars = []
        seen = set()
        for hgl in CLUSTER_PAGE_HANGUL.get(fname, []):
            for ch in hanja_by_hangul.get(hgl, []):
                if ch not in seen:
                    seen.add(ch)
                    chars.append(ch)
        per_image.append([folder, fname, "", "".join(chars)])

sum_path = Path("변환결과_markdown/이미지한자_OCR결과_파일이행.csv")
with sum_path.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["folder_name", "file_name", "hangul", "hanja"])
    w.writerows(per_image)

print("main", out_path, "rows", len(rows), dict(Counter(r[0] for r in rows)))
print("per-image", sum_path, "rows", len(per_image))
print("glyph samples:")
for row in rows[:10]:
    print(",".join(row))
print("cluster samples:")
n = 0
for row in rows:
    if row[0] == "2299" and row[1] == "image_001.bmp":
        print(",".join(row))
        n += 1
        if n >= 5:
            break
