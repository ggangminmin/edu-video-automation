# 검사① 자막 글자 = PPT 메모 대본 (허용 차이: 문장 끝 마침표 삭제 · 줄 나눔 공백만)
import json, re, os, unicodedata as u
from pptx import Presentation
PD = "../../../강의자료"
f = [x for x in os.listdir(PD) if u.normalize("NFC", x).startswith("261030_마루시공전문가_12강") and x.endswith(".pptx")][0]
tl = json.load(open("../타임라인_초안.json"))
bad = 0
for i, s in enumerate(Presentation(f"{PD}/{f}").slides, 1):
    raw = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    body = raw.split("교재:")[0]
    paras = [l.strip() for l in body.splitlines() if l.strip() and not re.match(r"\s*\d{2}-\d{3}", l.strip())]
    want = " ".join(paras)
    want = re.sub(r"\.(\s|$)", r"\1", want).strip()                  # 문장 끝 마침표만 지움
    got = " ".join(x["text"] for x in tl["subs"] if x["slide"] == i).strip()
    if re.sub(r"\s+", " ", want) != re.sub(r"\s+", " ", got):
        bad += 1; print("차이 슬라이드", i); print(" 대본:", want); print(" 자막:", got)
lines = tl["subs"]
over = [x for x in lines if len(x["text"]) > 35]
gaps = [(a["n"], round(b["start"] - a["end"], 3)) for a, b in zip(lines, lines[1:]) if a["slide"] == b["slide"] and abs(b["start"] - a["end"]) > 0.001]
print(f"슬라이드 차이 {bad}개 · 35자 넘는 줄 {len(over)}개 · 같은 슬라이드 안 자막 틈 {len(gaps)}개 · 자막 {len(lines)}줄")
