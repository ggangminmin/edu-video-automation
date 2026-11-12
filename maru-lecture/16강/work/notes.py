# 16강 pptx 메모 → notes_raw.json(원문) · notes_clean.json(슬라이드별 대본 문단, 「13-001 …」 제목줄·교재: 이하 제외)
import os, re, json, unicodedata as u
from pptx import Presentation
PD = "../../../강의자료"
f = [x for x in os.listdir(PD) if u.normalize("NFC", x).startswith("261030_마루시공전문가_16강") and x.endswith(".pptx")][0]
P = Presentation(f"{PD}/{f}")
raw, clean = [], []
for s in P.slides:
    t = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    raw.append(t)
    body = t.split("교재:")[0]
    paras = [l.strip() for l in body.splitlines() if l.strip() and not re.match(r"\s*\d{2}-\d{3}", l)]
    clean.append(paras)
json.dump(raw, open("../notes_raw.json", "w"), ensure_ascii=False, indent=1)
json.dump(clean, open("../notes_clean.json", "w"), ensure_ascii=False, indent=1)
print("slides", len(P.slides))
for i, (r, c) in enumerate(zip(raw, clean), 1):
    head = [l for l in r.splitlines() if re.match(r"\s*\d{2}-\d{3}", l)]
    print(i, head, len(c), "문단", sum(len(x) for x in c), "자", (c[0][:30] if c else "(없음)"))
