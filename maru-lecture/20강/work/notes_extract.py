# NN강 PPT 메모 → notes_raw.json(원문) · notes_clean.json(제목줄 NN-NNN·「교재:」 이하 제외, 문단 리스트) — 15강 판 그대로, 강 번호만 자동
import json, os, re, unicodedata as u
from pptx import Presentation
from lec import N
PD = "../../../강의자료"
f = [x for x in os.listdir(PD) if u.normalize("NFC", x).startswith(f"261030_마루시공전문가_{N}강") and x.endswith(".pptx")][0]
print(u.normalize("NFC", f))
raw, clean = [], []
for s in Presentation(f"{PD}/{f}").slides:
    t = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    raw.append(t)
    body = t.split("교재:")[0]
    clean.append([l.strip() for l in body.splitlines() if l.strip() and not re.match(r"\s*\d{2}-\d{3}", l.strip())])
json.dump(raw, open("../notes_raw.json", "w"), ensure_ascii=False, indent=1)
json.dump(clean, open("../notes_clean.json", "w"), ensure_ascii=False, indent=1)
print("슬라이드", len(raw), "· PNG", len([x for x in os.listdir("../slides") if x.endswith(".png")]))
