# 14강 v5 자막 줄 나눔(팀장 오더 · 지적 #10~12) = 12강 resplit_v4.py 복사: 타임라인_v4 → 타임라인_v5
# 글자는 그대로, 한 문장(같은 장 안에서 문장 끝 없이 이어진 줄 묶음) 안의 나누는 자리만 바꾼다.
# 줄 끝 = 연결어미·쉼표 뒤(line_break_check.reason 이 위반 아님)만. 새 줄 시작 = 그 줄 첫 어절의 받아쓰기 시각(출력 시각) − 0.09.
# 묶음 첫 줄 시작 · 마지막 줄 끝 = v3d 그대로.
import json, re, sys, difflib, bisect, os
sys.path.insert(0, "../../검수/검사기")
from line_break_check import reason, TERM, QUIZ
from PIL import ImageFont

FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD = 0.09
MAXC = 35; MAXW_HARD = 1550          # 35자 넘는 줄은 다른 수가 없을 때만, 폭 1450px(자막바 안쪽 1760px) 이하
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
def W(t): return sum(F.getlength(c) for c in t) - 0.78 * (len(t) - 1)

tl = json.load(open("../타임라인_v4.json"))
S = tl["subs"]

# ---- 받아쓰기 단어 → 출력 시각
ASR = {None: [(a, w) for a, b, w in json.load(open("mlxwords.json"))],
       "work/greet_a13_090.wav": [(a, w) for w, a, b in json.load(open("greet_a13_090_words.json"))["words"]],
       "work/bye_tc_090.wav": [(a, w) for w, a, b in json.load(open("bye_tc_090_words.json"))["words"]]}
def words_out(t0, t1):
    """출력 시각 [t0,t1] 에 깔린 소리 조각들의 받아쓰기 단어 (출력 시각, 단어)"""
    out = []
    for seg in tl["audio"]:
        o0 = seg["out"]; o1 = o0 + seg["src_to"] - seg["src_from"]
        if o1 < t0 or o0 > t1: continue
        for a, w in ASR[seg.get("src")]:
            if seg["src_from"] - 0.05 <= a < seg["src_to"]:
                to = o0 + (max(a, seg["src_from"]) - seg["src_from"])
                if t0 - 0.5 <= to <= t1 + 0.5: out.append((to, w))
    out.sort(); return out

# 받아쓰기 단어 시작은 앞 쉼을 품는다 → 그 자리가 조용하면 실제 소리 시작(10ms RMS, 음성만 v090/인삿말/끝인사 조각을 깐 v3d 음성 mix)으로 민다
import numpy as np, subprocess as sp
_pcm = np.frombuffer(sp.run(["ffmpeg", "-v", "error", "-i", "mix_v4.wav", "-af", "pan=mono|c0=c0", "-f", "f32le", "-ar", "16000", "-"], capture_output=True).stdout, np.float32)
_db = 20 * np.log10(np.sqrt(np.mean(_pcm[:len(_pcm) // 160 * 160].reshape(-1, 160) ** 2, 1)) + 1e-9)
TH = -33.0
def onset(t, win=0.9, gap=8, head=0.25):
    """t 직후(head 초 안)에 쉼(gap×10ms 이상 조용)이 시작되면 그 뒤 첫 소리 시각, 아니면 t(이미 말 시작)"""
    i = int(round(t * 100)); q_ = 0; g0 = None
    for j in range(i - 3, i + int(win * 100)):
        if _db[j] < TH:
            if q_ == 0: g0 = j
            q_ += 1
        else:
            if q_ >= gap and g0 <= i + int(head * 100) and _db[j + 1] > TH: return j / 100
            if j > i + int(head * 100): return t
            q_ = 0
    return t

def norm(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]
def word_times(text, t0, t1):
    """text 의 어절마다 첫 글자 출력 시각"""
    ws = words_out(t0, t1)
    tch, tt = [], []
    for to, w in ws:
        for c in norm(w): tch.append(c); tt.append(to)   # 단어 첫 시각(어절 시작만 쓰므로 충분)
    toks = text.split(" ")
    sch, own = [], []
    for k, tok in enumerate(toks):
        for c in norm(tok): sch.append(c); own.append(k)
    sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False); st = [None] * len(sch)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): st[a + k] = tt[b + k]
    res = []
    for k in range(len(toks)):
        idx = [i for i, o in enumerate(own) if o == k]
        hit = [st[i] for i in idx if st[i] is not None]
        v = hit[0] if hit and st[idx[0]] is not None else (min(hit) if hit else None)
        res.append(onset(v) if v is not None else None)
    return res, ws

# ---- 문장 묶음
groups = []; cur = [0]
for i in range(1, len(S)):
    a, b = S[i - 1], S[i]
    same = a.get("slide") == b.get("slide") and a.get("part") == b.get("part") and not TERM.search(a["text"].strip()) \
        and not QUIZ.match(b["text"].strip()) and not QUIZ.match(a["text"].strip())
    if same: cur.append(i)
    else: groups.append(cur); cur = [i]
groups.append(cur)

PART = None
def ok_break(toks, k):  # k = 앞 줄 마지막 어절 번호
    bad, _ = reason(" ".join(toks[:k + 1]), " ".join(toks[k + 1:]), PART)
    return not bad

def weak(toks, k):   # 허용이지만 덜 자연스러운 자리(-로·-에서·-어·주제어·것과) — 다른 자리가 없을 때만
    w = toks[k].rstrip(",")
    if toks[k].endswith(","): return 0
    if re.search(r"(와|과)$", w): return 1
    if w.endswith(("에서", "로", "에는", "에서는", "것과", "것은", "것이", "것도")): return 1
    if re.search(r"(겨|춰|눠|쳐|져|켜|펴|워|해|돼|봐)$", w): return 1
    if w.endswith(("은", "는")): return 1
    return 0

WT = None   # 어절 시작 시각(묶음마다 채움) · 마지막 = 묶음 끝
def split_k(toks, k):
    """toks 를 정확히 k 줄로 — 자리는 허용된 곳만, 폭 ≤ MAXW_HARD. 점수 = 35자 넘김 벌점 + 고르기 + 짧은 줄 벌점"""
    n = len(toks); INF = float("inf"); mean = len(" ".join(toks)) / k
    dp = [[(INF, None)] * (n + 1) for _ in range(k + 1)]; dp[0][0] = (0, [])
    for m in range(1, k + 1):
        for i in range(1, n + 1):
            if i < n and not ok_break(toks, i - 1): continue
            for j in range(i):
                if dp[m - 1][j][0] == INF: continue
                line = " ".join(toks[j:i]); L = len(line)
                if W(line) > MAXW_HARD: continue
                c = dp[m - 1][j][0] + (L - MAXC) * 300 * (L > MAXC) + max(0, 8 - L) * 25 + 0.3 * (L - mean) ** 2 + (40 * weak(toks, i - 1) if i < n else 0) + (max(0, 1.2 - (WT[i] - WT[j])) * 5000 if WT else 0)
                if c < dp[m][i][0]: dp[m][i] = (c, dp[m - 1][j][1] + [i])
    return dp[k][n]

def best_split(toks, k0):
    best = None
    for k in [k0, k0 + 1, k0 - 1, k0 + 2]:   # 줄 수는 v3d 와 같게가 기본 — 늘리거나 줄이면 줄마다 벌점
        if k < 1: continue
        c, cuts = split_k(toks, k)
        if cuts is None: continue
        c += 150 * abs(k - k0)
        if best is None or c < best[0]: best = (c, cuts)
    return best[1] if best else None

new = []; changes = []; n_out = 0
for g in groups:
    subs = [S[i] for i in g]
    PART = subs[0].get("part")
    text = " ".join(x["text"].strip() for x in subs)
    toks = text.split(" ")
    old_cuts = []; c = 0
    for x in subs[:-1]: c += len(x["text"].strip().split(" ")); old_cuts.append(c)
    bad_old = any(not ok_break(toks, k - 1) for k in old_cuts)
    # 🔒 담당 결정(14강): 「관리하십시오」 = 문장 끝(-오, 검사기 TERM 에 없음 → 오검출) → v4 줄 그대로
    if text.startswith("날짜와 버전, 적용 범위를"): bad_old = False
    if len(subs) == 1 or not bad_old:
        for x in subs:
            y = dict(x); n_out += 1; y["n_v3d"] = x["n"]; y["n"] = n_out; new.append(y)
        continue
    # 🔒 담당 결정(14강, 민석 #16 「보고서에는」 단독 줄 = 이상): 한 단어 줄 대신 나열 중간점 뒤에서 나눔(12강 v5 와 같음)
    MID = {"견적은 자재비·시공비·부자재비·철거비": ("부자재비·철거비", "부자재비·", "철거비"),
           "견적서에는 공사 개요·수량·자재 명세·시공": ("명세·시공", "명세·", "시공")}
    mid = next((v for k, v in MID.items() if text.startswith(k)), None)
    if mid:
        i = next(j for j, t in enumerate(toks) if mid[0] in t); p = toks[i].index(mid[0]) + len(mid[1]); toks = toks[:i] + [toks[i][:p], toks[i][p:]] + toks[i + 1:]; text = " ".join(toks)
    t0, t1 = subs[0]["start"], subs[-1]["end"]
    wt, ws = word_times(text, t0, t1)
    wt = [subs[0]["voice_on"]] + wt[1:]
    WT = [x if x is not None else None for x in wt] + [subs[-1]["end"]]
    for z in range(len(WT)):
        if WT[z] is None: WT[z] = WT[z - 1]
    cuts = best_split(toks, len(subs))
    # 🔒 담당 결정(14강): 「철거 후 / 확인할」 대신 쉼표·주제어 자리로 3줄
    if text.startswith("색상과 로트 등 식별 정보도 남기고,"):
        k1 = toks.index("남기고,") + 1; k2 = toks.index("항목은") + 1; cuts = [k1, k2, len(toks)]
    if mid: cuts = [next(j for j, t in enumerate(toks) if t.endswith(mid[1])) + 1, len(toks)]
    if cuts is None: raise SystemExit(f"나눌 자리 없음: {text}")
    cuts = [k for k in cuts if k < len(toks)]
    lines = []; prev = 0
    for k in cuts + [len(toks)]:
        lines.append((prev, k)); prev = k
    starts = []
    for li, (a, b) in enumerate(lines):
        if li == 0: starts.append((subs[0]["start"], subs[0]["voice_on"])); continue
        v = wt[a]
        if v is None: raise SystemExit(f"단어 시각 없음: {toks[a]} in {text}")
        starts.append((q(v - LEAD), v))
    for li, (a, b) in enumerate(lines):
        st, von = starts[li]; en = starts[li + 1][0] if li + 1 < len(lines) else subs[-1]["end"]
        y = {k: v for k, v in subs[0].items() if k in ("slide", "part")}
        n_out += 1
        y.update({"start": st, "voice_on": round(von, 3), "text": " ".join(toks[a:b]), "n": n_out, "end": en,
                  "how": "문장시작" if li == 0 else "줄나눔v4(어절 받아쓰기 −0.09)", "sent_start": subs[0].get("sent_start") if li == 0 else False,
                  "n_v3d": [x["n"] for x in subs]})
        if "line" in subs[0]: y["line"] = subs[0]["line"]
        new.append(y)
    changes.append({"v3d": [(x["n"], round(x["start"], 3), x["text"]) for x in subs],
                    "v4": [(y["n"], round(y["start"], 3), y["text"]) for y in new[-len(lines):]],
                    "asr": [(round(a, 2), w) for a, w in ws]})

# 확인: 이어 붙인 글자 그대로
assert "".join(x["text"].replace(" ", "") for x in S) == "".join(x["text"].replace(" ", "") for x in new)
assert " ".join(x["text"] for x in S).replace("· ", "·") == " ".join(x["text"] for x in new).replace("· ", "·")   # 중간점 뒤 나눔 2곳만 공백 차이
for a, b in zip(new, new[1:]):
    assert abs(a["end"] - b["start"]) < 1e-6 or a["end"] <= b["start"], (a, b)
    assert b["start"] > a["start"] + 0.3, ("너무 짧은 줄", a, b)
out = dict(tl); out["subs"] = new
out["params"] = dict(tl["params"]); out["params"]["v5"] = "14강 v5(12강 오더25 방식): 자막 줄 나눔 = 연결어미·쉼표 뒤만(line_break_check) · 새 줄 시작 = 첫 어절 받아쓰기(mlxwords/greet/bye) 출력 시각 −0.09 · 끝인사 퇴장 = 말 끝 뒤 정지 → 페이드"
json.dump(out, open("../타임라인_v5.json", "w"), ensure_ascii=False, indent=1)
json.dump(changes, open("resplit_v5_changes.json", "w"), ensure_ascii=False, indent=1)
for ch in changes:
    v4 = ch["v4"]; ends = [x[1] for x in v4[1:]]
    print("len", [len(t) for n, s_, t in v4], "px", [round(W(t)) for n, s_, t in v4])
    print("v3d:", " / ".join(f"[{s}] {t}" for n, s, t in ch["v3d"]))
    print(" v4:", " / ".join(f"[{s}] {t}" for n, s, t in ch["v4"]))
print(len(S), "→", len(new), "줄 · 바뀐 묶음", len(changes))
