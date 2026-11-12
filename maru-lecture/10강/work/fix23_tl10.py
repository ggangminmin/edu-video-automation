# 10강(오더43) 사본: 오더23/fix23_tl.py — 타임라인_v1_텀전 → 타임라인_v1_문장텀(규칙7). 바뀐 것 = 입출력 이름 · loud10 · 손값(END/SPLIT/FIRST_MAN)은 10강 없음
# 오더23(오더21 fix21_tl.py 복사) — 16~20강 타임라인 v2b → v3 · LOUD = loud15
# 오더21 — 12~15강 타임라인 v2 → v3 : 지금_규칙 7(문장 텀)만 반영. 방식 = 11강 pR align_v5.py 그대로
#  · 본문(2 ~ L-1) 메모 대본 문장 끝(. ? !) 뒤 줄 = 쉼(−40dB ≥0.04) 이 1.505 보다 짧으면 쉼 가운데 무음 넣어 1.505 · 길면 그대로 · 문장 안 쉼 그대로
#  · 넘김: 말 끝 → 1.71 → 컷+새 자막 → 0.09 → 말 · 확인문제 5.5 · 스스로 3.0 그대로
#  · 표지(1)·표지→2 컷 = v2 그대로(pS 통일 규칙) · 마지막 장(끝인사 warp) = v2 통째로 D 만큼 밀기(클립 안 쉼 그대로)
#  · 소리 조각: 넣은 자리 p 에서 시작하는 조각은 무음 뒤 → `p <= t`
# 실행(_작업 에서): python3 오더21/fix21_tl.py NN
import sys, json, re, subprocess, numpy as np
N = int(sys.argv[1]); D_ = f"{N}강"
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD = 0.09; SENT_MIN = 1.505; TURN = 1.71
v2 = json.load(open(f"{D_}/타임라인_v1_텀전.json")); NOTES = json.load(open(f"{D_}/notes_clean.json"))
LOUD = json.load(open(f"{D_}/work/loud10.json"))
S2 = {s["slide"]: s for s in v2["slides"]}; L = max(S2)
AU2 = {}
for a in v2["audio"]: AU2.setdefault(a["slide"], []).append(a)
assert all(len(v) == 1 for v in AU2.values())
AU2 = {k: dict(v[0]) for k, v in AU2.items()}
# 오더23(pS 00:5x · 깨끗한 음성 v090 실측): 장 말끝·조각 경계 손값
#  END_MAN = 장 실제 말끝(타임라인 말끝이 쉼 안으로 늦게 잡힘 → 대기가 그만큼 길어짐) · 17강 21장 641.465 → 641.219(−40dB 무음 시작)
#  SPLIT_MAN = 장 사이 소리 조각 경계(앞 장 조각이 다음 장 첫 말까지 포함) · 19강 2장: 「보겠습니다」 17.11 끝 · 3장 「MSDS」 18.04 시작인데 경계 18.726 → 쉼 가운데 17.6
END_MAN = {17: {21: 641.219}, 19: {2: 17.11}, 18: {13: 571.189}, 10: {23: 768.837}}   # 🆕10강 23장(문제 5) 말끝 = 「적셔 둔다」 끝 768.837 — v090 무음(768.837~769.839) 안 1샘플 블립(769.62)에 silencedetect 가 무음을 갈라 769.62 로 늦게 잡음(대기 6.285 → 5.5)   # 18강 13장(스스로) 말끝 = 「말해 보겠습니다」 끝 571.189(cx-18강 · v090 −53dB)
SPLIT_MAN = {19: {2: 17.6}, 18: {13: 571.65}, 10: {23: 769.2}}   # 🆕10강 23→24 조각 경계 = 무음 앞쪽 가운데(블립 769.62 앞, 무음 0.78초 안)   # 18강 13→14: 14장 첫 단어 「작업」(572.108~572.423)이 13장 조각(~572.473)에 들어 있었음
for k, t in SPLIT_MAN.get(N, {}).items(): AU2[k]["src_to"] = t; AU2[k + 1]["src_from"] = t
if N == 10: AU2[24]["src_from"] = 769.66   # 🆕10강: v090 769.61~769.63 −40dBFS 클릭(타입캐스트 이음매, 무음 안) 건너뜀 → 23장 조각 끝 769.2 · 24장 조각 시작 769.66(둘 다 무음 −60dB)

def sent_starts(s):
    """메모 대본에서 줄 바로 앞 글자가 . ? ! 인 줄의 n (공백 무시)"""
    ls = [x for x in v2["subs"] if x["slide"] == s]; ns = re.sub(r"\s", "", " ".join(NOTES[s - 1])); pos = 0; out = []
    for j, x in enumerate(ls):
        tx = re.sub(r"\s", "", x["text"]); k = pos; i = 0
        while i < len(tx):
            if ns[k] == tx[i]: i += 1; k += 1
            elif ns[k] in ".?!": k += 1
            else: raise SystemExit(f"메모 대조 실패 {N}강 {s}번 {x['text']} @{ns[k:k+10]}")
        if j > 0 and ns[pos - 1] in ".?!": out.append(x["n"])
        while k < len(ns) and ns[k] in ".?!": k += 1
        pos = k
    return set(out)

o = subprocess.run(["ffmpeg", "-i", f"{D_}/work/v090.wav", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], capture_output=True, text=True).stderr
SIL = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))

tl = {"slides": [], "subs": [], "audio": [], "anchors": [], "pauses": [], "skipped": [], "fixed_on": []}
FIX = {}
FIRST_MAN = {20: {22: 697.665}, 19: {3: 18.04}, 18: {14: 572.108}}   # 19강 3장 첫 말 = SPLIT 뒤 「MSDS」 시작(v090 18.04, −20dB)
tl["slides"].append(S2[1]); tl["subs"] += [dict(x) for x in v2["subs"] if x["slide"] == 1]
tl["audio"].append(AU2[1]); tl["anchors"].append(next(a for a in v2["anchors"] if a["name"] == "인삿말"))
cut = S2[2]["start"]
for s in range(2, L):
    ls = [x for x in v2["subs"] if x["slide"] == s]; sv = S2[s]; off2 = sv["src_offset"]; au = AU2[s]
    assert not au.get("src")
    a = sv["voice_start"] - off2; b = sv["voice_end"] - off2
    if s in END_MAN.get(N, {}): tl["fixed_on"].append(dict(slide=s, end_old=round(b, 3), end_new=END_MAN[N][s])); b = END_MAN[N][s]
    if s in FIRST_MAN.get(N, {}):                         # 오더23: 장 첫 말 손 확인값(쉼 안 −51dB 블립으로 silencedetect 가 쉼을 끊어 자동 규칙이 못 잡음 · 20강 22번 697.449 → 697.665)
        v0 = FIRST_MAN[N][s]; tl["fixed_on"].append(dict(slide=s, n=ls[0]["n"], old=round(a, 3), new=v0, text=ls[0]["text"], first=True, manual=True)); FIX[ls[0]["n"]] = v0 + off2; a = v0
    else:
     for u0, v0 in SIL:                                    # 오더23: 장 첫 말 시작이 쉼(≥0.3) 안 = 무음 끝으로(17강 22번 「정답은」 0.76초 늦게 들림)
        if u0 <= a < v0 - 0.12 and v0 - u0 >= 0.3 and v0 - a <= 1.2:
             tl["fixed_on"].append(dict(slide=s, n=ls[0]["n"], old=round(a, 3), new=round(v0, 3), text=ls[0]["text"], first=True)); FIX[ls[0]["n"]] = v0 + off2; a = v0; break
    starts = sent_starts(s); ins = []
    for x in ls:
        if x["n"] not in starts: continue
        on = x["voice_on"] - off2
        for u0, v0 in SIL:                                # 오더23: 문장 시작이 쉼(≥0.3) 안에 찍힘 = 무음 끝으로(메모리 🩸 「문장 시작 = 무음 끝」, 17강 147)
            if u0 <= on < v0 - 0.12 and v0 - u0 >= 0.3 and v0 - on <= 1.2 and u0 > a:
                tl["fixed_on"].append(dict(slide=s, n=x["n"], old=round(on, 3), new=round(v0, 3), text=x["text"])); FIX[x["n"]] = v0 + off2; on = v0; break
        if on >= b - 0.05:
            tl["skipped"].append(dict(slide=s, n=x["n"], why="말 끝 뒤 줄(음성 없음)", text=x["text"])); continue
        c = [(u, v) for u, v in SIL if on - 0.35 <= v <= on + 0.12 and u > a]
        if not c:
            tl["skipped"].append(dict(slide=s, n=x["n"], why="앞 쉼 못 찾음", text=x["text"])); continue
        u, v = max(c, key=lambda z: z[1] - z[0]); g = v - u; add = max(0.0, SENT_MIN - g)
        p = (u + v) / 2; assert au["src_from"] < p < au["src_to"]
        ins.append((p, add)); tl["pauses"].append(dict(slide=s, n=x["n"], before=round(g, 3), after=round(g + add, 3)))
    ins.sort()
    start = cut; off = start + LEAD - a
    def mp(t): return t + off + sum(d for p, d in ins if p <= t)
    prev = au["src_from"]
    for p, d in ins + [(au["src_to"], 0.0)]:
        tl["audio"].append(dict(slide=s, out=round(mp(prev), 4), src_from=round(prev, 4), src_to=round(p, 4))); prev = p
    for j, x in enumerate(ls):
        on = mp(FIX.get(x["n"], x["voice_on"]) - off2); y = dict(x)
        y.update(start=start if j == 0 else q(on - LEAD), voice_on=round(on, 3), sent_start=x["n"] in starts); y.pop("end", None)
        tl["subs"].append(y)
    # 오더23: 16~20 v2 는 quiz_wait 대신 wait="문제" · 스스로 = self_check_wait 또는 wait="스스로"
    wait = 5.5 if (sv.get("quiz_wait") or sv.get("wait") == "문제") else (3.0 if (sv.get("self_check_wait") or sv.get("wait") == "스스로") else TURN)
    end = q(mp(b) + wait)
    ns = dict(sv); ns.update(start=start, end=end, voice_start=round(mp(a), 3), voice_end=round(mp(b), 3), gap_after_voice=round(end - mp(b), 3),
                             gap_before_voice=round(mp(a) - start, 3), src_offset=round(off, 4), inserts=[[round(p, 4), round(d, 4)] for p, d in ins])
    tl["slides"].append(ns); cut = end
# 마지막 장 = v2 통째로 밀기
D = cut - S2[L]["start"]; sl = dict(S2[L])
for k in ("end", "voice_start", "voice_end", "src_offset"): sl[k] = round(sl[k] + D, 4)
sl["start"] = cut; sl["end"] = q(S2[L]["end"] + D); tl["slides"].append(sl)
tl["subs"] += [dict(x, start=(cut if i == 0 else q(x["start"] + D)), voice_on=round(x["voice_on"] + D, 3)) for i, x in enumerate(x for x in v2["subs"] if x["slide"] == L)]
tl["audio"].append(dict(AU2[L], out=round(AU2[L]["out"] + D, 4)))
an = dict(next(a for a in v2["anchors"] if a["name"] == "끝인사")); an["in"] = cut; an["clip_t0"] = round(an["clip_t0"] + D, 4); an["out"] = q(an["out"] + D)
tl["anchors"].append(an)
T = sl["end"]
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else T
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
bg = dict(v2["bgm"]); song = bg["file"].split("/")[-1][:-4]
bg["loops"] = int(np.ceil(tl["total"] / (LOUD["bgm_dur"][song] - 3.0))); tl["bgm"] = bg
tl["params"] = dict(v2["params"], 문장텀="규칙7(pR 11강 v5 방식): 메모 문장 끝 뒤 쉼 ≥1.505(무음 삽입) · 넘김 말끝→컷 1.71 + 컷→말 0.09 · 표지→2·끝인사 클립 안 = v2 그대로", D_last=round(D, 4))
json.dump(tl, open(f"{D_}/타임라인_v1_문장텀.json", "w"), ensure_ascii=False, indent=1)
P = np.array([p["before"] for p in tl["pauses"]])
print(N, "자막", len(tl["subs"]), "(v2", len(v2["subs"]), ") 총", tl["total"], "(v2", v2["total"], f") 문장끝 {len(P)}곳 원래 최소 {P.min():.2f} 중앙 {np.median(P):.2f} 넣음 {sum(d for s in tl['slides'] for _, d in s.get('inserts', [])):.1f}초 · 조각 {len(tl['audio'])} · BGM loops {bg['loops']}")
for k in tl["skipped"]: print("  건너뜀", k)
for k in tl["fixed_on"]: print("  시작고침", k)
