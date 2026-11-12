# 오더21 — 12~15강 타임라인 v2 → v3 : 지금_규칙 7(문장 텀)만 반영. 방식 = 11강 pR align_v5.py 그대로
#  · 본문(2 ~ L-1) 메모 대본 문장 끝(. ? !) 뒤 줄 = 쉼(−40dB ≥0.04) 이 1.505 보다 짧으면 쉼 가운데 무음 넣어 1.505 · 길면 그대로 · 문장 안 쉼 그대로
#  · 넘김: 말 끝 → 1.71 → 컷+새 자막 → 0.09 → 말 · 확인문제 5.5 · 스스로 3.0 그대로
#  · 표지(1)·표지→2 컷 = v2 그대로(pS 통일 규칙) · 마지막 장(끝인사 warp) = v2 통째로 D 만큼 밀기(클립 안 쉼 그대로)
#  · 소리 조각: 넣은 자리 p 에서 시작하는 조각은 무음 뒤 → `p <= t`
# 실행(_작업 에서): python3 오더21/fix21_tl.py NN
import sys, os, json, re, subprocess, numpy as np
N = int(sys.argv[1]); D_ = f"{N}강"
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD = 0.09; SENT_MIN = 1.505; TURN = 1.71
v2 = json.load(open(f"{D_}/타임라인_v2.json")); NOTES = json.load(open(f"{D_}/notes_clean.json"))
LOUD = json.load(open("오더09_공용/loud09.json"))
S2 = {s["slide"]: s for s in v2["slides"]}; L = max(S2)
# 규칙2 개정(11/2 23:1x): 음성에 통째로 없는 메모 문장 = 자막에서 뺌(_작업/음성에없는문장.md) · 받아쓰기로 확인한 줄 시작 고침(v090 초)
DROP = {}.get(N, [])   # 🆕11/3 01:xx 12강 33번 = 음성에 있음(4/5 소리 경계가 그 문장 앞이었음) → 안 뺌(v3c)
OUTN = os.environ.get("OUT", "타임라인_v3.json")
ONSET = {15: {"지금 관찰한 것과 더 알아봐야 할 것을 나눠 보세요": 514.393}}.get(N, {})   # mlx: 「넣겠습니까?」 끝 513.34 · 쉼 513.46~514.39 · 「지금」
AU2 = {}
for a in v2["audio"]: AU2.setdefault(a["slide"], []).append(a)
assert all(len(v) == 1 for v in AU2.values())
AU2 = {k: dict(v[0]) for k, v in AU2.items()}
# 🆕11/3 v3c: 장 경계 소리 조각 옮김(v090 초) — 12강 4/5: 「이름만 맞추지 말고 … 확인하세요」(103.577~108.142)는 4번 장 메모 문장인데 v1 부터 5번 조각 앞머리에 있었음
BMOVE = {12: [(4, 108.65, 108.142, {"이름만 맞추지 말고 높이와 통행, 고정 상태까지 확인하세요": 103.577}, {"실리콘은 적용 가능한 재료인지와": 109.165}, 109.165)]}.get(N, [])
SUBFIX = {}
for k, cut_src, ve_src, on_k, on_n, vs_src in BMOVE:
    S2[k] = dict(S2[k]); S2[k + 1] = dict(S2[k + 1])
    AU2[k]["src_to"] = cut_src; AU2[k + 1]["src_from"] = cut_src
    S2[k]["voice_end"] = round(ve_src + S2[k]["src_offset"], 4); S2[k + 1]["voice_start"] = round(vs_src + S2[k + 1]["src_offset"], 4)
    for t, v in on_k.items(): SUBFIX[(k, t)] = v + S2[k]["src_offset"]
    for t, v in on_n.items(): SUBFIX[(k + 1, t)] = v + S2[k + 1]["src_offset"]

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

tl = {"slides": [], "subs": [], "audio": [], "anchors": [], "pauses": [], "skipped": [], "dropped": []}
tl["slides"].append(S2[1]); tl["subs"] += [dict(x) for x in v2["subs"] if x["slide"] == 1]
tl["audio"].append(AU2[1]); tl["anchors"].append(next(a for a in v2["anchors"] if a["name"] == "인삿말"))
cut = S2[2]["start"]
for s in range(2, L):
    ls = [dict(x) for x in v2["subs"] if x["slide"] == s]; sv = S2[s]; off2 = sv["src_offset"]; au = AU2[s]
    assert not au.get("src")
    a = sv["voice_start"] - off2; b = sv["voice_end"] - off2
    starts = sent_starts(s); ins = []
    for x in ls:
        if (s, x["text"]) in SUBFIX: x["voice_on"] = round(SUBFIX[(s, x["text"])], 3); x["how"] = "v3c 장 경계 소리 옮김"
    for x in ls:
        if x["text"] in ONSET: x["voice_on"] = round(ONSET[x["text"]] + off2, 3); x["how"] = "오더21 받아쓰기 고침"
    for x in ls:
        if x["text"] in DROP: tl["dropped"].append(dict(slide=s, n_v2=x["n"], text=x["text"])); x["drop"] = True
    ls = [x for x in ls if not x.get("drop")]
    for x in ls:
        if x["n"] not in starts: continue
        on = x["voice_on"] - off2
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
        on = mp(x["voice_on"] - off2); y = dict(x)
        y.update(start=start if j == 0 else q(on - LEAD), voice_on=round(on, 3), sent_start=x["n"] in starts); y.pop("end", None)
        tl["subs"].append(y)
    wait = 5.5 if sv.get("quiz_wait") else (3.0 if sv.get("self_check_wait") else TURN)
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
# 🆕11/3 01:3x 팀장 결정: hold 원음 확인(오더21/hold_원음확인.md)에서 0.16 넘게 먼저 뜬 줄만 줄 시작 = 말 −0.09 (출력 초, 소리·장 그대로) → 12강 v3d · 15강 v3c
OUTFIX = {12: {"각도에서 비교하면 상태를 이해하기 쉽습니다": 461.628 + 0.28}, 15: {"원인 가설, 가설을 좁히기 위한 조사 계획을": 242.743 + 0.36}}.get(N, {}) if os.environ.get("OUTFIX") else {}
for x in tl["subs"]:
    for t, on in OUTFIX.items():
        if x["text"].startswith(t[:12]): x["voice_on"] = round(on, 3); x["start"] = q(on - LEAD); x["how"] = "오더21 hold 원음 고침"
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else T
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
bg = dict(v2["bgm"]); song = bg["file"].split("/")[-1][:-4]
bg["loops"] = int(np.ceil(tl["total"] / (LOUD["bgm_dur"][song] - 3.0))); tl["bgm"] = bg
tl["params"] = dict(v2["params"], 문장텀="규칙7(pR 11강 v5 방식): 메모 문장 끝 뒤 쉼 ≥1.505(무음 삽입) · 넘김 말끝→컷 1.71 + 컷→말 0.09 · 표지→2·끝인사 클립 안 = v2 그대로", D_last=round(D, 4))
json.dump(tl, open(f"{D_}/{OUTN}", "w"), ensure_ascii=False, indent=1)
P = np.array([p["before"] for p in tl["pauses"]])
print(N, "자막", len(tl["subs"]), "(v2", len(v2["subs"]), ") 총", tl["total"], "(v2", v2["total"], f") 문장끝 {len(P)}곳 원래 최소 {P.min():.2f} 중앙 {np.median(P):.2f} 넣음 {sum(d for s in tl['slides'] for _, d in s.get('inserts', [])):.1f}초 · 조각 {len(tl['audio'])} · BGM loops {bg['loops']}")
for k in tl["skipped"] + tl["dropped"]: print("  건너뜀/뺌", k)
