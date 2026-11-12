# 05강 타임라인 한 번에(오더44 · 11~20강 최종 납품 방식 = 20강 align.py → fix23_tl(문장 텀) → resplit_v4(줄 나눔) → make_tl_v4c(새 줄 실소리) 를 한 파일로)
#  ① 줄: 메모 대본 문장(. ? ! 뒤) → 마침표만 뺌 → 35자 넘으면 line_break_check 허용 자리(연결어미·쉼표 뒤)만, 쉼 있는 자리 우대(resplit_v4 DP)
#  ② 시각: 글자 정렬(whisper.cpp + mlx) → 문장 시작 = 무음(−40dB ≥0.08) 끝 · 문장 안 줄 = 실소리(newline_onset_check 와 같은 정의: 쉼 끝 −50dB 30ms 상승 / 골짜기)
#  ③ 텀(규칙 7): 문장 끝 뒤 쉼 ≥1.505(쉼 가운데 무음 넣기) · 넘김 말끝 → 1.71 → 컷(새 자막 같은 프레임) → 0.09 → 말 · 확인문제 5.5 · 스스로 3.0 · 마지막 3.5
#  ④ 표지 = 인삿말 flow 클립 + 강의인삿말/0.9배/인삿말_05강_090.wav · 마지막 장 = 끝인사 flow 클립 + v090 마무리(bye_tc_090.wav) · fade_in 0.5 · bye_freeze
# 실행(cwd 05강/work): python3 make_tl05.py <판이름 v1> [--freeze 초]
import json, re, sys, os, difflib, bisect, subprocess, numpy as np
sys.path.insert(0, "../../검수/검사기")
from line_break_check import reason
from PIL import ImageFont
VER = sys.argv[1]
OVR = json.load(open("tl_override.json")) if os.path.exists("tl_override.json") else {}   # 손값(받아쓰기·실소리 확인 뒤): {"on": {"줄 앞글자": v090초}, "force": {"문장": [줄,…]}, "freeze": 초}
N = 5; FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD, SENT_MIN, TURN, QUIZ_WAIT, SELF_WAIT, HOLD_END = 0.09, 1.53, 1.71, 5.5, 3.0, 3.5
MAXC, MAXW_HARD = 35, 1550
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
def W(t): return sum(F.getlength(c) for c in t) - 0.78 * (len(t) - 1)
notes = json.load(open("../notes_clean.json")); raw = json.load(open("../notes_raw.json"))
HEAD = [r.strip().splitlines()[0] if r.strip() else "" for r in raw]
QUIZ = {i for i, h in enumerate(HEAD, 1) if re.search(r"-\d{3}\s+문제\s*\d+\s*$", h)}
SELF = {i for i, h in enumerate(HEAD, 1) if "스스로" in h}
L = len(notes)
def norm(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]

# ---------- 소리
def load16(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def sil(p, d, mono=False, n=-40):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, *(["-ac", "1"] if mono else []), "-af", f"silencedetect=n={n}dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return list(zip(st, en + [9999] * (len(st) - len(en))))
def dbcurve(y, H=80): return 20 * np.log10(np.sqrt(np.mean(y[:len(y) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
V = load16("v090.wav"); DB5 = dbcurve(V); DUR = len(V) / 16000
SIL8 = sil("v090.wav", 0.08); SIL4 = sil("v090.wav", 0.04, mono=True, n=-43)   # 검사기(gap_check)와 같은 모노 48k 측정 — 원음 쉼 안 −46dB 딸깍(375.297)이 쉼을 쪼갬
FR, TH, RUN, GAP, SHALLOW, VWIN = 200, -50.0, 6, 6, -45.0, 0.15
def real_onset(db, ref):
    """newline_onset_check.onset 그대로(검사기와 같은 정의)"""
    i0, i1 = max(0, int((ref - 0.3) * FR)), min(len(db) - RUN, int((ref + 0.3) * FR))
    seg = db[i0:i1]; runs = []; j = 0
    while j < len(seg):
        if seg[j] < TH:
            k = j
            while k < len(seg) and seg[k] < TH: k += 1
            if k - j >= GAP: runs.append((i0 + j, i0 + k))
            j = k
        else: j += 1
    if runs:
        s_, e_ = min(runs, key=lambda r: abs(r[1] / FR - ref)); m = e_
        while m < len(db) - RUN and not all(db[m:m + RUN] > TH): m += 1
        return m / FR, "쉼"
    v0, v1 = max(3, int((ref - VWIN) * FR)), min(len(db) - 4, int((ref + VWIN) * FR))
    vs = [m for m in range(v0, v1) if db[m] <= SHALLOW and db[m] == db[m - 3:m + 4].min()]
    if not vs: return None, "이어진 말"
    m = min(vs, key=lambda m: abs(m / FR - ref)); return m / FR, "골짜기"

# ---------- 문장 → 어절
SENTS = []   # (slide, [toks])
for s, paras in enumerate(notes, 1):
    for p in paras:
        for sent in re.split(r"(?<=[.?!])\s+", p.strip()):
            sent = sent.strip()
            if not sent: continue
            if sent.endswith("."): sent = sent[:-1]
            SENTS.append((s, sent.split(" ")))
# 글자 정렬(전체 본문)
sch, sown = [], []   # 글자, (문장 번호, 어절 번호)
for si, (s, toks) in enumerate(SENTS):
    for k, t in enumerate(toks):
        for c in norm(t): sch.append(c); sown.append((si, k))
def align(words):
    tch, tt = [], []
    for a, b, w in words:
        cs = norm(w)
        for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))
    sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False); st = [None] * len(sch)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): st[a + k] = tt[b + k]
    ok = [v is not None for v in st]; idx = [i for i, v in enumerate(st) if v is not None]
    for i in range(len(st)):
        if st[i] is None:
            j = bisect.bisect(idx, i); lo = idx[j - 1] if j > 0 else None; hi = idx[j] if j < len(idx) else None
            st[i] = st[hi] if lo is None else st[lo] if hi is None else st[lo] + (st[hi] - st[lo]) * (i - lo) / (hi - lo)
    return st, ok, sum(ok)
cpp = [(w["offsets"]["from"] / 1000, w["offsets"]["to"] / 1000, w["text"]) for w in json.loads(open("wfull.json", "rb").read().decode("utf-8", "replace"))["transcription"]]
Tc, OKc, mc = align(cpp); Tm, OKm, mm = align([tuple(x) for x in json.load(open("mlxwords.json"))])
print(f"정렬 일치 cpp {mc/len(sch):.1%} · mlx {mm/len(sch):.1%}")
tok_t = {}   # (si,k) → mlx 첫 글자 시각
for i, o in enumerate(sown): tok_t.setdefault(o, (Tm[i], Tc[i], OKm[i], OKc[i]))

# 문장 시작(v090) = 무음 끝
def snap(t, lo=-0.6, hi=1.2):
    for a, b in SIL8:
        if a - 0.05 <= t <= b: return b
    c = [b for a, b in SIL8 if t + lo <= b <= t + hi]
    return min(c, key=lambda b: abs(b - t)) if c else t
SON = []; DIS = []
for si, (s, toks) in enumerate(SENTS):
    tm, tc, om, oc = tok_t[(si, 0)]
    t = tc if oc else tm
    if om and oc and abs(tm - tc) > 1.0: DIS.append((si, " ".join(toks)[:16], round(tc, 2), round(tm, 2))); t = max(tm, tc)
    SON.append(snap(t))
for k, v in OVR.get("sent_on", {}).items():   # 05강: 「장|문장 앞글자」 로 장 지정 가능(같은 문장 「정답은 삼 번입니다」 18·20장)
    ks, kt = (int(k.split("|")[0]), k.split("|")[1]) if "|" in k else (None, k)
    for si, (s, toks) in enumerate(SENTS):
        if " ".join(toks).startswith(kt) and (ks is None or ks == s): SON[si] = v
for a, b in zip(SON, SON[1:]): assert b > a, ("문장 시작 역행", a, b)

# ---------- 줄 나눔(resplit_v4 DP: ok_break · weak · 쉼 우대)
EXC_BREAK = set()
NOUN_MYEON = {'표면', '측면', '단면', '화면', '장면', '전면', '후면', '평면', '정면', '바닥면', '내면', '외면', '면'}
def ok_break(toks, k):
    if toks[k] in NOUN_MYEON: return False
    if k + 1 < len(toks) and toks[k + 1].startswith(("아니라", "아닌")): return False
    if toks[k].rstrip(",").endswith("아니라"): return True
    if toks[k].rstrip(",").endswith(("되는지", "하는지", "있는지", "없는지", "는지")): EXC_BREAK.add(" ".join(toks[:k + 1])); return True   # 05강 담당 결정: 간접의문 연결어미 「-는지」 뒤(검사기 OK_END 에 없음 → 예외.md)
    bad, _ = reason(" ".join(toks[:k + 1]), " ".join(toks[k + 1:]), None)
    return not bad
def weak(toks, k):
    w = toks[k].rstrip(",")
    if toks[k].endswith(","): return 0
    if re.search(r"(와|과)$", w): return 1
    if w.endswith(("에서", "로", "에는", "에서는", "것과", "것은", "것이", "것도")): return 1
    if re.search(r"(겨|춰|눠|쳐|져|켜|펴|워|해|돼|봐)$", w): return 1
    if w.endswith(("은", "는")): return 1
    return 0
def pause_at(si, k):   # 어절 k 앞에 쉼(−40dB ≥0.04)이 있나
    t = tok_t[(si, k)][0]
    return any(t - 0.35 <= b <= t + 0.15 and b - a >= 0.04 for a, b in SIL4)
def split_k(si, toks, k):
    n = len(toks); INF = float("inf"); mean = len(" ".join(toks)) / k
    dp = [[(INF, None)] * (n + 1) for _ in range(k + 1)]; dp[0][0] = (0, [])
    for m in range(1, k + 1):
        for i in range(1, n + 1):
            if i < n and not ok_break(toks, i - 1): continue
            for j in range(i):
                if dp[m - 1][j][0] == INF: continue
                line = " ".join(toks[j:i]); Ln = len(line)
                if W(line) > MAXW_HARD: continue
                c = dp[m - 1][j][0] + (Ln - MAXC) * 300 * (Ln > MAXC) + max(0, 8 - Ln) * 25 + 0.3 * (Ln - mean) ** 2 \
                    + ((40 * weak(toks, i - 1) - (25 if pause_at(si, i) else 0)) if i < n else 0)
                if c < dp[m][i][0]: dp[m][i] = (c, dp[m - 1][j][1] + [i])
    return dp[k][n]
FORCE = OVR.get("force", {})
LINES = []   # dict(slide, si, toks range, text, sent_first)
for si, (s, toks) in enumerate(SENTS):
    text = " ".join(toks)
    fk = [k for k in FORCE if text.startswith(k)]
    if fk:
        fl = FORCE[fk[0]]; assert " ".join(fl) == text, (fl, text); cuts = []; c = 0
        for x in fl[:-1]: c += len(x.split(" ")); cuts.append(c)
    elif len(text) <= MAXC: cuts = []
    else:
        k0 = -(-len(text) // MAXC); best = None
        for k in (k0, k0 + 1):
            c, cu = split_k(si, toks, k)
            if cu is None: continue
            c += 150 * (k - k0)
            if best is None or c < best[0]: best = (c, cu[:-1])
        if best is None: raise SystemExit(f"나눌 자리 없음: {text}")
        cuts = best[1]
    prev = 0
    for j, kk in enumerate(cuts + [len(toks)]):
        LINES.append(dict(slide=s, si=si, k0=prev, text=" ".join(toks[prev:kk]), sent_first=(j == 0))); prev = kk
assert " ".join(x["text"] for x in LINES) == " ".join(" ".join(t) for _, t in SENTS)

# ---------- 줄 시작(v090)
ONO = OVR.get("on", {})
for x in LINES:
    if x["sent_first"]: x["on"] = SON[x["si"]]; x["how"] = "문장시작(무음 끝)"; continue
    ref = tok_t[(x["si"], x["k0"])][0]
    on, how = real_onset(DB5, ref)
    x["on"] = on if on is not None else ref; x["how"] = f"줄나눔 실소리({how})" if on is not None else "줄나눔 받아쓰기(이어진 말)"; x["ref"] = round(ref, 3)
for x in LINES:
    for k, v in ONO.items():
        if x["text"].startswith(k): x["on"] = v; x["how"] = "손값(받아쓰기 확인)"
for a, b in zip(LINES, LINES[1:]): assert b["on"] > a["on"] + 0.3, ("줄 시작 역행/너무 가까움", a, b)

# 장 말 구간(v090)
def end_before(t):   # t(다음 말 시작) 바로 앞 쉼 시작 = 앞 말 끝
    c = [a for a, b in SIL8 if abs(b - t) < 0.002]
    if c: return c[0]
    c = [a for a, b in SIL8 if a < t - 0.05]; return max(c)
SL = sorted(set(x["slide"] for x in LINES)); RNG = {}
for s in SL:
    ls = [x for x in LINES if x["slide"] == s]; nxt = [x for x in LINES if x["slide"] == s + 1]
    b = end_before(nxt[0]["on"]) if nxt else max(a for a, b in SIL8 if a < DUR - 0.05)
    RNG[s] = (ls[0]["on"], b, ls)
for k, v in OVR.get("end", {}).items(): RNG[int(k)] = (RNG[int(k)][0], v, RNG[int(k)][2])

# ---------- 아나운서 warp 결과
def wj(name): return json.load(open(f"../아나운서B/5_{name}_flow{OVR.get('warp_tag', '')}.json"))
GWJ, BWJ = wj("인삿말"), wj("끝인사")
tl = {"slides": [], "subs": [], "audio": [], "anchors": [], "pauses": [], "skipped": []}
# 표지 + 인삿말 (fix23_v2b 방식: 클립 끝 = 표지→2 컷)
GT = json.load(open("greet_text.json"))["text"]
gsents = [x.strip() for x in re.split(r"(?<=[.?!])\s+", GT) if x.strip()]
GLINES = OVR.get("greet_lines") or ["안녕하세요", "마루시공전문가 민간자격 온라인 강의", "제5강에 오신 여러분을 환영합니다", "9강에서는 실제 시공 순서에 따라 작업 방법을 익히고,", "각 단계에서 확인해야 할 사항을 짚어봅니다"]
assert "".join(GLINES).replace(" ", "") == "".join(s.rstrip(".") for s in gsents).replace(" ", ""), "인삿말 줄 ≠ 문장"
G = load16("greet_tc_090.wav"); GDB = dbcurve(G); gdur = len(G) / 16000
GON = OVR.get("greet_on")   # 인삿말 줄 시작(인삿말 wav 초) — 받아쓰기 + 실소리 확인
if not GON:
    gw = json.load(open("greet_tc_words.json"))["words"]; gch, gt = [], []
    for a_, b_, w_ in gw:
        cs_ = norm(w_)
        for k_, c_ in enumerate(cs_): gch.append(c_); gt.append(a_ + (b_ - a_) * k_ / max(1, len(cs_)))
    lch, lown = [], []
    for li, t_ in enumerate(GLINES):
        for c_ in norm(t_): lch.append(c_); lown.append(li)
    sm_ = difflib.SequenceMatcher(None, lch, gch, autojunk=False); st_ = {}
    for a_, b_, n_ in sm_.get_matching_blocks():
        for k_ in range(n_): st_[a_ + k_] = gt[b_ + k_]
    GON = []
    for li in range(len(GLINES)):
        ks = [k_ for k_ in range(len(lch)) if lown[k_] == li and k_ in st_]; ref = st_[ks[0]]
        on_, how_ = real_onset(GDB, ref); GON.append(round(on_ if on_ is not None else ref, 3))
    GON[0] = GWJ["target_speech"][0]
print("인삿말 줄 시작", GON)
toa = GWJ["target_at_out"]; LOUD = json.load(open("loud05.json"))
ggain = round(10 ** ((LOUD["voice"] - LOUD["greet"]) / 20), 3)
tl["audio"].append(dict(slide=1, out=round(max(0.0, toa), 4), src_from=round(max(0.0, -toa), 4), src_to=round(gdur, 4), src="work/greet_tc_090.wav", gain=ggain))
tl["anchors"].append({"name": "인삿말", "in": 0.0, "clip": f"../아나운서B/5_인삿말_flow{OVR.get('warp_tag', '')}.mp4", "clip_t0": 0.0, "fade_in": 0.5})
cut = q(GWJ["out_dur"])
for j, (t, txt) in enumerate(zip(GON, GLINES)):
    tl["subs"].append(dict(slide=1, start=q(toa + t - LEAD), voice_on=round(toa + t, 3), text=txt, part="인삿말", sent_start=txt.startswith(("안녕", "5강")) and j > 0))
tl["slides"].append(dict(slide=1, start=0.0, end=cut, voice_start=round(toa + GWJ["target_speech"][0], 3), voice_end=round(toa + GWJ["target_speech"][1], 3),
                         note="표지 + 인삿말 아나운서(flow) · 소리 강의인삿말/0.9배/인삿말_05강_090.wav"))
# 본문 2 ~ L-1
for s in SL:
    if s == L: continue
    a, b, ls = RNG[s]
    starts = [x for x in ls[1:] if x["sent_first"]]; ins = []
    for x in starts:
        on = x["on"]; c = [(u, v) for u, v in SIL4 if on - 0.35 <= v <= on + 0.12 and u > a]
        if not c: tl["skipped"].append(dict(slide=s, why="앞 쉼 못 찾음", text=x["text"])); continue
        u, v = max(c, key=lambda z: z[1] - z[0]); g = v - u; add = max(0.0, SENT_MIN - g); p = (u + v) / 2
        ins.append((p, add)); tl["pauses"].append(dict(slide=s, text=x["text"][:20], before=round(g, 3), after=round(g + add, 3)))
    ins.sort(); start = cut; off = start + LEAD - a
    def mp(t): return t + off + sum(d for p, d in ins if p <= t)
    s0 = 0.0 if s == 2 else max(a - 0.05, RNG[s - 1][1] + 0.05); s1 = min(b + 0.05, DUR)
    prev = s0
    for p, d in ins + [(s1, 0.0)]:
        tl["audio"].append(dict(slide=s, out=round(mp(prev), 4), src_from=round(prev, 4), src_to=round(p, 4))); prev = p
    for j, x in enumerate(ls):
        von = mp(x["on"])
        tl["subs"].append(dict(slide=s, start=start if j == 0 else q(von - LEAD), voice_on=round(von, 3), text=x["text"], how=x["how"], sent_start=x["sent_first"] and j > 0, v090_on=round(x["on"], 3)))
    qz, sf = s in QUIZ, s in SELF
    end = q(mp(b) + (QUIZ_WAIT if qz else SELF_WAIT if sf else TURN))
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(mp(a), 3), voice_end=round(mp(b), 3), gap_after_voice=round(end - mp(b), 3),
                             gap_before_voice=LEAD, wait="문제" if qz else "스스로" if sf else "텀", quiz_wait=qz, self_check_wait=sf, src_offset=round(off, 4),
                             v090=[round(a, 3), round(b, 3)], inserts=[[round(p, 4), round(d, 4)] for p, d in ins]))
    cut = end
# 마지막 장 = 끝인사 클립 + bye_tc_090.wav(v090 797.66~)
SND = json.load(open("sound05.json")); BA = SND["bye_v090"][0]
a, b, ls = RNG[L]; ts, te = a - BA, b - BA          # bye wav 기준 말 구간
assert abs(ts - BWJ["target_speech"][0]) < 0.03 and abs(te - BWJ["target_speech"][1]) < 0.05, (ts, te, BWJ["target_speech"])
ts, te = BWJ["target_speech"]; cs = BWJ["clip_speech"][0]
start = cut; off = start + LEAD - ts
s0 = round(np.floor((BA + max(0.0, ts - 0.05)) / 0.02 + 1e-6) * 0.02 - BA, 3)   # v090 기준 20ms 칸(announcer_audio_check)
bdur = len(load16("bye_tc_090.wav")) / 16000
tl["audio"].append(dict(slide=L, out=round(off + s0, 4), src_from=round(s0, 4), src_to=round(bdur, 4), src="work/bye_tc_090.wav", gain=1.0))
for j, x in enumerate(ls):
    von = off + (x["on"] - BA)
    tl["subs"].append(dict(slide=L, start=start if j == 0 else q(von - LEAD), voice_on=round(von, 3), text=x["text"], part="끝인사", how=x["how"], sent_start=x["sent_first"] and j > 0, v090_on=round(x["on"], 3)))
end = q(off + te + HOLD_END)
c0 = round(off + ts - cs, 4)
tl["anchors"].append({"name": "끝인사", "in": start, "clip": f"../아나운서B/5_끝인사_flow{OVR.get('warp_tag', '')}.mp4", "clip_t0": c0, "out": q(c0 + BWJ["out_dur"]), "fade_in": 0.5})
tl["slides"].append(dict(slide=L, start=start, end=end, voice_start=round(off + ts, 3), voice_end=round(off + te, 3), gap_after_voice=round(end - (off + te), 3),
                         gap_before_voice=LEAD, quiz_wait=False, src_offset=round(off, 4), note=f"끝인사 클립(flow) · 소리 = v090 마무리 {BA}~{SND['bye_v090'][1]}"))
cut = end
for an, (x0, y0) in zip(tl["anchors"], ((934, 40), (952, 36))):   # 규칙 20: place05/fit05 실측 → 인삿말 x450(제목·사진 사이 · 빈칸 412 < 몸 420 · 팀장 확인) · 끝인사 = 겹침 0 그대로
    an["x"] = OVR.get("anc_x", {}).get(an["name"], x0); an["y"] = y0
    an["place"] = "지적 #9·규칙 20: " + ("빈 공간으로 옮김(place05 실측)" if an["x"] != x0 else "안 가림 → 그대로")
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut
for a_, c_ in zip(tl["subs"], tl["subs"][1:]): assert c_["start"] > a_["start"] + 0.5, ("짧은 줄", a_, c_)
T = cut   # 🩸v3 실수: bye_freeze 를 절대 시각으로 적어 두면 앞 텀이 바뀔 때 말하는 도중 정지 → 클립 기준(freeze_clip)으로
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3),
                "bye_freeze": round(c0 + OVR["freeze_clip"], 4), "bye_freeze_note": OVR.get("freeze_note", "임시(실측 전)")}
tl["total"] = round(T + 9.70, 3)
song = "Focused Flow"; bg_db = round(LOUD["voice"] - 20 - LOUD["bgm"], 2)
tl["bgm"] = dict(file=f"BGM/{song}.mp3", gain_db=bg_db, song_lufs=LOUD["bgm"], voice_lufs=LOUD["voice"], loops=int(np.ceil(tl["total"] / (LOUD["bgm_dur"] - 3.0))), crossfade=3.0, fade_out=5.836,
                 rule="지금_규칙 10·23: 5강 = Focused Flow · 곡 LUFS + gain = 음성(v090) LUFS − 20 · 이어 붙임(3초 크로스페이드)")
tl["params"] = dict(LEAD=LEAD, SENT_MIN=SENT_MIN, TURN=TURN, QUIZ_WAIT=QUIZ_WAIT, SELF_WAIT=SELF_WAIT, HOLD_END=HOLD_END, QUIZ=sorted(QUIZ), SELF=sorted(SELF), MAXC=MAXC,
                    voice="녹음_본문_04-20강/마루시공_-_05강.mp3 atempo=0.9", greet=f"강의인삿말/0.9배/인삿말_05강_090.wav gain {ggain}", announcer="남자(홀수 모음) · 표지 인삿말 + 마지막 장 끝인사 · flow(warp_s) · 페이드인 0.5",
                    bgm=f"{song} {bg_db}dB", 방식="오더44: 11~20강 최종 납품 방식(20강 v4c) 그대로 처음부터")
json.dump(tl, open(f"../타임라인_{VER}.json", "w"), ensure_ascii=False, indent=1)
print("자막", len(tl["subs"]), "최장", max(len(x["text"]) for x in tl["subs"]), "총", tl["total"], f"({int(tl['total']//60)}:{tl['total']%60:04.1f})", "QUIZ", sorted(QUIZ), "SELF", sorted(SELF))
print("문장 시작 어긋남(cpp/mlx>1s)", DIS); print("건너뜀", tl["skipped"])
P = [p["before"] for p in tl["pauses"]]; print("문장끝 쉼", len(P), "원래 최소", min(P), "넣음", round(sum(d for s in tl["slides"] for _, d in s.get("inserts", [])), 2))
print("이어진 말(판정불가 후보)", [(x["text"][:14], x["ref"]) for x in LINES if "이어진" in x["how"]])
