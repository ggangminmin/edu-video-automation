# 15강 v1 타임라인 — 11강 align_v3.py(오더 06) 방식 그대로, 15강 재료로
#  · 텀은 장면 바뀌기 전에: 말 끝 → 1.21 → 다음 장면 + 새 자막 같은 프레임 → 0.09 → 말 (말 사이 1.30 = 11강과 같음)
#  · 문제 대기 = 문제 낭독 끝 → 컷 5.5 · 마지막 장 말 끝 → 엔딩 3.5
#  · 자막 시작 = 말 시작 − 0.09 (본문 말 시작 = align.py + check_bound/fix_bound 받아쓰기 보정 → 타임라인_초안.json)
#  · 구조(민석 확정 11/2 20:1x): 표지(1) + 팀장 인삿말 클립 → 2(아나운서 없음) → … → 25 = 팀장 끝인사 클립(자체 음성, 타입캐스트 25번 안 씀) → 엔딩
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
D = json.load(open("../타임라인_초안.json"))
LEAD = 0.09; POST, PRE, QUIZ_WAIT, HOLD_END = 0.30, 1.00, 5.5, 3.5
GAP = POST + PRE - LEAD
QUIZ = {15, 17, 19, 21, 23}
LAST = 25
ANN = "../아나운서"          # work 기준
# 줄 시작 = 무음 끝·음량 골짜기 뒤 상승 + 짧은 구간 받아쓰기 확인(onset_clip_check*.py)
G = dict(clip=f"{ANN}/15_인삿말_090.mp4", wav="아나운서/15_인삿말_090.wav", dur=16.933, voice_end=16.078,
         lines=[(1.207, "안녕하세요"), (2.373, "마루시공전문가 민간자격 온라인 강의"), (5.36, "제15강에 오신 여러분을 환영합니다"),
                (8.554, "15강에서는 마루에 발생하는 하자의 종류를 알아보고,"), (12.37, "현장 상태를 바탕으로 원인을 조사하는 방법을 살펴봅니다")],
         gain=0.813)                                     # −17.1 LUFS → 본문 −18.9 (−1.8dB)
BYE = dict(clip=f"{ANN}/15_끝인사_090.mp4", wav="아나운서/15_끝인사_090.wav", dur=17.689, voice_end=16.576,
           on=[1.214, 5.486, 8.951, 13.928], gain=0.841)  # −17.4 → −18.9 (−1.5dB)

off0 = {s["slide"]: s.get("src_offset", 0) for s in D["slides"]}
body = [x for x in D["subs"] if "part" not in x]
lines = [dict(slide=x["slide"], text=x["text"], on=round(x["voice_on"] - off0[x["slide"]], 3)) for x in body]
bye_txt = [x["text"] for x in D["subs"] if x.get("part") == "끝인사"]
assert len(bye_txt) == len(BYE["on"])
lines += [dict(slide=LAST, text=t, on=o) for t, o in zip(bye_txt, BYE["on"])]
src_end = {s["slide"]: round(s["voice_end"] - s["src_offset"], 3) for s in D["slides"] if "src_offset" in s}
seg = {a["slide"]: a for a in D["audio"]}

tl = {"slides": [], "subs": [], "audio": [], "anchors": []}
tl["audio"].append(dict(slide=1, out=0.0, src_from=0.0, src_to=G["dur"], src=G["wav"], gain=G["gain"]))
tl["anchors"].append(dict(name="인삿말", **{"in": 0.0, "clip": G["clip"], "clip_t0": 0.0}))
cut = q(G["dur"])        # 인삿말 클립 끝 = 표지→2 컷 (말 끝→컷 0.86 + 컷→말 0.09 = 0.95, 00강 표지→2 0.97)
for t, txt in G["lines"]:
    tl["subs"].append(dict(slide=1, start=q(t - LEAD), voice_on=round(t, 3), text=txt, part="인삿말"))
tl["slides"].append(dict(slide=1, start=0.0, end=cut, note="표지 + 인삿말 아나운서"))

for s in sorted(set(l["slide"] for l in lines)):
    ls = [l for l in lines if l["slide"] == s]
    a = ls[0]["on"]; b = BYE["voice_end"] if s == LAST else src_end[s]
    start = cut; off = start + LEAD - a
    if s == LAST:
        tl["audio"].append(dict(slide=s, out=round(off, 4), src_from=0.0, src_to=BYE["dur"], src=BYE["wav"], gain=BYE["gain"]))
    else:
        s0 = 0.0 if s == 2 else max(a - 0.05, seg[s]["src_from"]); s1 = seg[s]["src_to"]
        tl["audio"].append(dict(slide=s, out=round(s0 + off, 4), src_from=round(s0, 4), src_to=round(s1, 4)))
    for j, l in enumerate(ls):
        st = start if j == 0 else q(l["on"] + off - LEAD)
        d = dict(slide=s, start=st, voice_on=round(l["on"] + off, 3), text=l["text"])
        if s == LAST: d["part"] = "끝인사"
        tl["subs"].append(d)
    wait = QUIZ_WAIT if s in QUIZ else (HOLD_END if s == LAST else GAP)
    end = q(b + off + wait)
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(a + off, 3), voice_end=round(b + off, 3),
                             gap_after_voice=round(end - (b + off), 3), gap_before_voice=round(a + off - start, 3),
                             quiz_wait=s in QUIZ, src_offset=round(off, 4)))
    if s == LAST:
        tl["anchors"].append(dict(name="끝인사", **{"in": start, "clip": BYE["clip"], "clip_t0": round(off, 4), "out": q(off + BYE["dur"])}))
    cut = end
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1
    x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut   # 11강 v3 와 같음
T = cut
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(LEAD=LEAD, GAP_voice_to_cut=GAP, QUIZ_WAIT=QUIZ_WAIT, HOLD_END=HOLD_END, voice="v090.wav(15강 0.9배)",
                    bgm="BGM/Approxima.mp3 -20dB(배정표 없음 → 11강과 같게)", 구조="민석 확정 B안")
json.dump(tl, open("../타임라인_v1.json", "w"), ensure_ascii=False, indent=1)
print("자막", len(tl["subs"]), "총길이", tl["total"])
for x in tl["slides"]: print(x["slide"], round(x["start"], 3), round(x["end"], 3), x.get("gap_before_voice"), x.get("gap_after_voice"))
