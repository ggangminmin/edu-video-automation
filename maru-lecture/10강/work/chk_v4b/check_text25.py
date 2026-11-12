# 10강(오더43) 사본: 20강/work/chk_v4c — 이름 v4c→v1 · gap_check 기준판 = 타임라인_v1_텀전
# (오더34 19·20강 v4c 사본: 파일 이름 v4→v4c 만 바꿈 · 원본 오더25)
# 오더09 공용(15강 check_text.py 복사 · 강 번호 인자 · 타임라인_v3 · 인삿말만 제외) 검사① 자막 글자 = PPT 메모 대본 (허용 차이: 문장 끝 마침표 삭제 · 줄 나눔 공백만)
import json, re, os, sys, unicodedata as u
N = sys.argv[1]
from pptx import Presentation
PD = "../../강의자료"
f = [x for x in os.listdir(PD) if u.normalize("NFC", x).startswith(f"261030_마루시공전문가_{N}강") and x.endswith(".pptx")][0]
tl = json.load(open(f"../{N}강/타임라인_v4b.json"))
bad = 0
for i, s in enumerate(Presentation(f"{PD}/{f}").slides, 1):
    raw = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ""
    body = raw.split("교재:")[0]
    paras = [l.strip() for l in body.splitlines() if l.strip() and not re.match(r"\s*\d{2}-\d{3}", l.strip())]
    want = " ".join(paras)
    want = re.sub(r"\.(\s|$)", r"\1", want).strip()                  # 문장 끝 마침표만 지움
    for d in tl.get("dropped", []):                                    # 🆕오더21 규칙2 개정: 음성에 없어 뺀 문장(음성에없는문장.md)은 대본에서도 빼고 대조
        if d["slide"] == i: assert d["text"] in want, d; want = want.replace(d["text"], " ").strip()
    got = " ".join(x["text"] for x in tl["subs"] if x["slide"] == i and x.get("part") != "인삿말").strip()
    if re.sub(r"\s+", " ", want) != re.sub(r"\s+", " ", got):
        bad += 1; print("차이 슬라이드", i); print(" 대본:", want); print(" 자막:", got)
lines = [x for x in tl["subs"] if x.get("part") != "인삿말"]
over = [x for x in lines if len(x["text"]) > 35]
gaps = [(a["n"], round(b["start"] - a["end"], 3)) for a, b in zip(lines, lines[1:]) if a["slide"] == b["slide"] and abs(b["start"] - a["end"]) > 0.001]
print("뺀 줄:", [(d["slide"], d["text"]) for d in tl.get("dropped", [])]); print(f"슬라이드 차이 {bad}개 · 35자 넘는 줄 {len(over)}개 · 같은 슬라이드 안 자막 틈 {len(gaps)}개 · 자막 {len(lines)}줄")
