# 11강 v5 타임라인 — 오더 19 · 지금_규칙 7(민석 11/2 22:4x 확정 문장 텀)만 v4 에 반영
#  · 확실한 문장 끝(메모 대본 마침표·물음표) 뒤 쉼 최소 1.5초(길면 그대로) — 쉼(−40dB) 가운데에 무음을 넣음. 문장 안 쉼은 그대로
#  · 페이지 넘김: 말 끝 → 1.71 → 컷+새 자막 → 0.09 → 말(합 1.8). 확인문제 5.5 · 스스로 확인하기 3.0 · 마지막 3.5 그대로
#  · 표지 인삿말(1번)·끝인사(27번) 아나운서 구간은 v4 그대로(입 싱크 warp 클립 · 오더 19-5 「v4 외 변경 금지」) — 27번은 시각만 통째로 밀림
#  · 소리 조각 배치는 넣은 자리 p 에서 시작하는 조각이 무음 뒤에 오도록 `p <= t`(인계 ④ 버그 주의)
import json, re, subprocess
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD = 0.09; SENT_MIN = 1.505; TURN = 1.71          # 1.5 + 반올림 여유 5ms
v4 = json.load(open("../타임라인_v4.json")); N = json.load(open("../notes_clean.json"))
S4 = {s["slide"]: s for s in v4["slides"]}; AU4 = {a["slide"]: a for a in v4["audio"]}

# --- 문장 시작 줄: 메모 대본에서 그 줄 바로 앞 글자가 . ? ! 인 줄(공백 무시)
def sent_starts(s):
    ls = [x for x in v4["subs"] if x["slide"] == s]; ns = re.sub(r"\s", "", " ".join(N[s - 1])); pos = 0; out = []
    for j, x in enumerate(ls):
        tx = re.sub(r"\s", "", x["text"]); k = pos; i = 0
        while i < len(tx):
            if ns[k] == tx[i]: i += 1; k += 1
            elif ns[k] in ".?!": k += 1
            else: raise SystemExit(f"메모 대조 실패 {s} {x['text']}")
        if j > 0 and ns[pos - 1] in ".?!": out.append(x["src_n"])
        while k < len(ns) and ns[k] in ".?!": k += 1
        pos = k
    return set(out)

o = subprocess.run(["ffmpeg", "-i", "v090.wav", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], capture_output=True, text=True).stderr
SIL = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))

tl = {"slides": [], "subs": [], "audio": [], "anchors": [], "pauses": []}
tl["slides"].append(S4[1]); tl["subs"] += [x for x in v4["subs"] if x["slide"] == 1]
tl["audio"].append(AU4[1]); tl["anchors"].append(next(a for a in v4["anchors"] if a["name"] == "인삿말"))
cut = S4[2]["start"]                                     # 표지→2 컷 = v4 그대로(인삿말 클립 끝)
for s in range(2, 27):
    ls = [x for x in v4["subs"] if x["slide"] == s]; s4 = S4[s]; off4 = s4["src_offset"]
    a = ls[0]["voice_on"] - off4; b = s4["voice_end"] - off4
    starts = sent_starts(s); ins = []
    for x in ls:
        if x["src_n"] not in starts: continue
        on = x["voice_on"] - off4
        c = [(u, v) for u, v in SIL if on - 0.35 <= v <= on + 0.12]
        u, v = max(c, key=lambda z: z[1] - z[0]); g = v - u; add = max(0.0, SENT_MIN - g)
        ins.append(((u + v) / 2, add)); tl["pauses"].append(dict(slide=s, src_n=x["src_n"], before=round(g, 3), after=round(g + add, 3)))
    start = cut; off = start + LEAD - a
    def mp(t): return t + off + sum(d for p, d in ins if p <= t)
    au = AU4[s]; prev = au["src_from"]
    for p, d in sorted(ins) + [(au["src_to"], 0.0)]:
        tl["audio"].append(dict(slide=s, out=round(mp(prev), 4), src_from=round(prev, 4), src_to=round(p, 4))); prev = p
    for j, x in enumerate(ls):
        on = mp(x["voice_on"] - off4)
        tl["subs"].append(dict(slide=s, start=start if j == 0 else q(on - LEAD), voice_on=round(on, 3), text=x["text"], src_n=x["src_n"],
                               sent_start=x["src_n"] in starts))
    wait = 5.5 if s4["quiz_wait"] else (3.0 if s4["self_check_wait"] else TURN)
    end = q(mp(b) + wait)
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(mp(a), 3), voice_end=round(mp(b), 3),
                             gap_after_voice=round(end - mp(b), 3), gap_before_voice=round(mp(a) - start, 3),
                             quiz_wait=s4["quiz_wait"], self_check_wait=s4["self_check_wait"], src_offset=round(off, 4),
                             inserts=[[round(p, 4), round(d, 4)] for p, d in ins]))
    cut = end
# --- 27번(끝인사) = v4 통째로 D 만큼 밀기
D = cut - S4[27]["start"]; s27 = dict(S4[27])
for k in ("start", "end", "voice_start", "voice_end", "src_offset"): s27[k] = round(s27[k] + D, 4) if k != "start" else cut
s27["end"] = q(S4[27]["end"] + D); tl["slides"].append(s27)
tl["subs"] += [dict(x, start=(cut if i == 0 else q(x["start"] + D)), voice_on=round(x["voice_on"] + D, 3)) for i, x in enumerate(x for x in v4["subs"] if x["slide"] == 27)]
tl["audio"].append(dict(AU4[27], out=round(AU4[27]["out"] + D, 4)))
an = dict(next(a for a in v4["anchors"] if a["name"] == "끝인사")); an["in"] = cut; an["clip_t0"] = round(an["clip_t0"] + D, 4); an["out"] = q(an["out"] + D)
tl["anchors"].append(an)
T = s27["end"]
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else T
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(v4["params"], 문장텀="규칙7: 메모 문장 끝 뒤 쉼 ≥1.5(무음 삽입) · 넘김 말끝→컷 1.71 + 컷→말 0.09", D27=round(D, 4))
json.dump(tl, open("../타임라인_v5.json", "w"), ensure_ascii=False, indent=1)
import numpy as np
P = np.array([p["before"] for p in tl["pauses"]])
print("자막", len(tl["subs"]), "총길이", tl["total"], "(v4", v4["total"], ") · 문장 끝 쉼", len(P), "개 원래 최소", P.min(), "중앙", np.median(P), "· 소리 조각", len(tl["audio"]))
for x in tl["slides"]: print(x["slide"], round(x["start"], 3), round(x["end"], 3), x.get("gap_before_voice"), x.get("gap_after_voice"))
