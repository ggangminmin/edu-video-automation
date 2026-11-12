# NN강 1단계 타임라인 초안 — 15강 align.py + align_v3.py(11강 v3 규칙) 합본, 강 번호 자동
#  · 메모 대본(제목줄·교재: 제외) → 자막 줄(35자) → 0.9배 음성 받아쓰기 강제정렬(whisper.cpp 문장 시작 + mlx 단어 문장 안 줄)
#  · 13강 보강: cpp·mlx 문장 시작이 1초 넘게 다르면 늦은 쪽(받아쓰기가 보기 낭독을 건너뛰면 항상 일찍 잡힘)
#  · v3 텀: 말 끝 → 1.21 → 장면+새 자막 같은 프레임 → 0.09 → 말 · 문제 5.5 · 🆕스스로 확인하기 3.0(규칙 17) · 마지막 3.5 → 엔딩
#  · 🆕규칙 18 구조: 표지(1) + 팀장 인삿말 클립(영상만) + 소리 = 강의인삿말/audio_{N-1} 0.9배(greet_tc_090.wav)
#                   → 2(아나운서 없음) → … → 마지막 장 = 팀장 끝인사 클립(영상만) + 소리 = 타입캐스트 본문 마무리(v090 그 장 구간)
#    클립 영상은 2단계에서 11강 work/warp_clip.py 로 타입캐스트 소리에 맞춰 늘이고 줄임(입 싱크 ≤0.1초).
# 실행 순서: align.py(lines.json) → linetimes_make.py → align.py → check_text.py → check_bound.py → fix_bound.py → align.py
import json, re, subprocess, difflib, bisect, os
import numpy as np
from lec import N
FPS = 30000 / 1001
def q(t): return round(round(t * FPS) / FPS, 4)
notes = json.load(open("../notes_clean.json")); raw = json.load(open("../notes_raw.json"))
HEAD = [r.strip().splitlines()[0] if r.strip() else "" for r in raw]
QUIZ = {i for i, h in enumerate(HEAD, 1) if re.search(r"-\d{3}\s+문제\s*\d+\s*$", h)}
SELF = {i for i, h in enumerate(HEAD, 1) if "스스로" in h}
LAST = len(notes)
MAXC = 35; LEAD = 0.09; POST, PRE = 0.30, 1.00; GAP = POST + PRE - LEAD
QUIZ_WAIT, SELF_WAIT, HOLD_END = 5.5, 3.0, 3.5
GT = json.load(open("greet_text.json")) if os.path.exists("greet_text.json") else None   # 인삿말 문장(타입캐스트 받아쓰기 + 파일 이름 표기 대조, 손으로 확인)
AMETA = json.load(open("../아나운서/meta.json"))

STRONG = ("고", "며", "면", "는데", "지만", "므로", "뒤", "때는", "해서", "어서", "아서", "려면", "려니")
CONNECT = ("고", "며", "면", "서", "는데", "지만", "뒤", "때는", "므로", "니다", "하고", "해", "에서", "으로", "로", "를", "을", "는", "은", "와", "과", "때", "도")
FORCE = {k: v for k, v in json.load(open("force_split.json")).items() if not k.startswith("_")} if os.path.exists("force_split.json") else {}   # 오더15 줄 나눔 고정
import sys as _sys; _sys.path.insert(0, "../../검수/검사기"); from line_break_check import reason as _lb_reason, QUIZ as _LBQ   # 🆕06강: 줄 나눔 = line_break_check 허용 자리만(오더25 방식)
def split_line(s):
    if s in FORCE: return FORCE[s]
    if len(s) <= MAXC: return [s]
    best = None
    for i, ch in enumerate(s):
        if ch != " ": continue
        L, R = s[:i].rstrip(), s[i+1:].lstrip()
        if len(L) < 6 or len(R) < 6: continue
        score = abs(len(L) - len(R))
        if L.endswith(","): score -= 30
        elif any(L.endswith(c) for c in STRONG): score -= 12
        elif any(L.endswith(c) for c in CONNECT): score -= 4
        if re.match(r"(아니라|아닙|수 |있|않|없|곱하|나누|하는|하면|해야|된|되|할 |볼 |봅|합니|입니)", R): score += 20
        if max(len(L), len(R)) > MAXC: score += 15
        if not _LBQ.match(R) and _lb_reason(L, R)[0]: score += 1000   # 🆕06강: 검사기 위반 자리는 마지막 수단
        if best is None or score < best[0]: best = (score, L, R)
    if best is None: return [s]
    return split_line(best[1]) + split_line(best[2])
def make_lines(paras):
    out = []
    for p in paras:
        for sent in re.split(r"(?<=[.?])\s+", p.strip()):
            sent = sent.strip()
            if not sent: continue
            if sent.endswith("."): sent = sent[:-1]
            out.append([x.strip() for x in split_line(sent)])
    return out
def norm_chars(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]
def load_cpp(p): return json.loads(open(p, "rb").read().decode("utf-8", "replace"))["transcription"]

lines, SENT = [], []
for si, paras in enumerate(notes, 1):
    for parts in make_lines(paras):
        SENT.append(list(range(len(lines), len(lines) + len(parts))))
        for t in parts: lines.append((si, t))
json.dump([t for _, t in lines], open("lines.json", "w"), ensure_ascii=False)
if not os.path.exists("linetimes.json"): raise SystemExit(f"lines.json {len(lines)}줄 저장 — linetimes_make.py 먼저")

def silences(path, d):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n=-40dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return list(zip(st, en + [9999] * (len(st) - len(en))))
SIL = silences("v090.wav", 0.08); S5 = silences("v090.wav", 0.05)
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "v090.wav"]))

sch, sline = [], []
for li, (_, t) in enumerate(lines):
    for c in norm_chars(t): sch.append(c); sline.append(li)
def align_chars(words):
    tch, tt = [], []
    for a, b, w in words:
        cs = norm_chars(w)
        for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))
    sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False); st = [None] * len(sch)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): st[a + k] = tt[b + k]
    return st, sum(n for _, _, n in sm.get_matching_blocks())
cpp = [(w["offsets"]["from"]/1000, w["offsets"]["to"]/1000, w["text"]) for w in load_cpp("wfull.json")]
stime, m1 = align_chars(cpp); CPP_OK = [v is not None for v in stime]
stime_m, m2 = align_chars([tuple(x) for x in json.load(open("mlxwords.json"))])
print(f"정렬 일치 글자 cpp {m1/len(sch):.1%} · mlx {m2/len(sch):.1%}")
idx = [i for i, v in enumerate(stime) if v is not None]
for i in range(len(stime)):
    if stime[i] is None:
        j = bisect.bisect(idx, i); lo = idx[j-1] if j > 0 else None; hi = idx[j] if j < len(idx) else None
        stime[i] = stime[hi] if lo is None else stime[lo] if hi is None else stime[lo] + (stime[hi] - stime[lo]) * (i - lo) / (hi - lo)
def snap_onset(t, lo=-0.6, hi=1.2):
    for s0, e0 in SIL:
        if s0 - 0.05 <= t <= e0: return e0
    c = [e for s0, e in SIL if t + lo <= e <= t + hi]
    return min(c, key=lambda e: abs(e - t)) if c else t
def sil_before(t):
    c = [s0 for s0, e0 in SIL if abs(e0 - t) < 0.002]
    return c[0] if c else t
first_char = {}
for i, li in enumerate(sline): first_char.setdefault(li, i)
on = [None] * len(lines); SNAPPED = 0; DISAGREE = []
for sent in SENT:
    fc = first_char[sent[0]]; t = stime[fc]; tm = stime_m[fc]
    if tm is None:
        k = fc
        while k < len(sch) and sline[k] == sent[0] and stime_m[k] is None: k += 1
        tm = stime_m[k] - 0.12 * (k - fc) if k < len(sch) and sline[k] == sent[0] else None
    if not CPP_OK[fc] and tm is not None: DISAGREE.append((sent[0], lines[sent[0]][1][:16], "cpp없음", round(t, 2), round(tm, 2))); t = tm
    elif tm is not None and abs(tm - t) > 1.0: DISAGREE.append((sent[0], lines[sent[0]][1][:16], round(t, 2), round(tm, 2))); t = max(t, tm)
    on[sent[0]] = round(snap_onset(t), 3)
    if any(abs(e - on[sent[0]]) < 0.002 for _, e in SIL): SNAPPED += 1
SFX = {int(k): v for k, v in json.load(open("sent_fix.json")).items()} if os.path.exists("sent_fix.json") else {}
for i, v in SFX.items(): on[i] = v                     # sent_check.py: 문장 시작 = 긴 무음 끝(받아쓰기 확인)
DB = np.load("rmsdb.npy"); H = 0.005
HOW = {}
def cont_onset(est, prev):
    c = [(s0, e0) for s0, e0 in S5 if est - 0.5 <= s0 <= est + 0.3 and est - 0.05 <= e0 <= est + 0.8 and s0 > prev + 0.3]
    if c: return min(c, key=lambda z: abs(z[1] - est))[1], "무음끝"
    a0 = int((est - 0.12) / H); b0 = int((est + 0.3) / H)
    i = int(np.argmin(DB[a0:b0])); j = a0 + i
    while j < b0 + 40 and DB[j] < DB[a0 + i] + 6: j += 1
    return j * H, "골짜기"
TM = json.load(open("linetimes.json"))["mlx"]; assert len(TM) == len(lines)
for sent in SENT:
    for i in sent[1:]:
        t, how = cont_onset(TM[i], on[i - 1]); HOW[i] = how
        on[i] = round(max(t, on[i - 1] + 0.5), 3)
OVR = {int(k): v for k, v in json.load(open("onset_override.json")).items()} if os.path.exists("onset_override.json") else {}
for i, v in OVR.items(): on[i] = v; HOW[i] = "받아쓰기보정"
print(f"문장 시작 {SNAPPED}/{len(SENT)} 무음 끝에 붙음 · cpp/mlx 어긋남 {len(DISAGREE)} · 줄 보정 {len(OVR)} · 문장 보정 {len(SFX)}")
for d in DISAGREE: print("  어긋남", d)
slides = sorted(set(s for s, _ in lines))
src = {}
for s in slides:
    lis = [i for i, (ss, _) in enumerate(lines) if ss == s]
    a = on[lis[0]]
    b = sil_before(on[lis[-1] + 1]) if lis[-1] + 1 < len(lines) else max(s0 for s0, e0 in SIL if s0 < DUR - 0.01 and e0 >= DUR - 0.05)
    src[s] = (a, b, lis)

# --- 인삿말(타입캐스트 0.9배) 줄 시각
G = AMETA["인삿말"]; B = AMETA["끝인사"]
gw = json.load(open("greet_tc_words.json"))
GS = silences("greet_tc_090.wav", 0.08)
g_on0 = GS[0][1] if GS and GS[0][0] < 0.01 else 0.0                              # 타입캐스트 말 시작
g_end = max(s0 for s0, e0 in GS if e0 >= gw["dur_090"] - 0.05) if GS else gw["dur_090"]   # 말 끝
glines = []
if GT:
    for parts in make_lines([GT["text"]]): glines += parts
    gch, gl = [], []
    for li, t in enumerate(glines):
        for c in norm_chars(t): gch.append(c); gl.append(li)
    tch, tt = [], []
    for a, b, w in gw["words"]:
        cs = norm_chars(w)
        for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))
    sm = difflib.SequenceMatcher(None, gch, tch, autojunk=False); st = {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): st[a + k] = tt[b + k]
    print(f"인삿말 글자 일치 {len(st)}/{len(gch)}")
    gon = []
    for li in range(len(glines)):
        ks = [k for k in range(len(gch)) if gl[k] == li and k in st]
        t = st[ks[0]] - 0.12 * (ks[0] - gl.index(li)) if ks else None
        for s0, e0 in GS:
            if t is not None and s0 - 0.05 <= t <= e0 + 0.15: t = e0; break
        gon.append(round(t, 3) if t is not None else None)
    gon[0] = round(g_on0, 3)
else:
    gon = []
g_off = G["speech_out"][0] - g_on0            # 타입캐스트 말 시작 = 클립 말 시작(warp 전 기준)
cover_cut = q(g_end + g_off + (G["dur_out"] - G["speech_out"][1]))   # 말 끝 → 클립 끝 꼬리(0.79초)만큼 두고 2번으로

tl = {"slides": [], "subs": [], "audio": [], "anchors": []}
tl["audio"].append(dict(slide=1, out=round(g_off, 4), src_from=0.0, src_to=round(gw["dur_090"], 3), src=f"{N:02d}강/work/greet_tc_090.wav", note="규칙 18: 강의인삿말 타입캐스트 0.9배"))
tl["anchors"].append({"name": "인삿말", "in": 0.0, "clip": f"_작업/{N:02d}강/아나운서/{N:02d}_인삿말_090.mp4", "clip_t0": 0.0, "clip_dur": G["dur_out"],
                      "clip_speech": G["speech_out"], "tc_speech": [round(g_on0 + g_off, 3), round(g_end + g_off, 3)],
                      "warp_ratio": round((g_end - g_on0) / (G["speech_out"][1] - G["speech_out"][0]), 3), "audio": "클립 소리 끔 → 2단계 warp_clip.py"})
for li, t in enumerate(glines):
    v = (gon[li] if gon[li] is not None else g_on0) + g_off
    tl["subs"].append(dict(slide=1, start=q(max(0, v - LEAD)), voice_on=round(v, 3), text=t, part="인삿말"))
tl["slides"].append(dict(slide=1, start=0.0, end=cover_cut, note="표지 + 인삿말 아나운서(영상) + 타입캐스트 인삿말(소리)"))
cut = cover_cut
for s in slides:
    a, b, lis = src[s]
    start = cut; off = start + LEAD - a
    s0 = 0.0 if s == 2 else max(a - 0.05, src[s - 1][1] + 0.05) if s - 1 in src else a - 0.05
    s1 = min(b + 0.05, DUR)
    tl["audio"].append(dict(slide=s, out=round(s0 + off, 4), src_from=round(s0, 4), src_to=round(s1, 4)))
    for j, li in enumerate(lis):
        st_ = start if j == 0 else q(on[li] + off - LEAD)
        d = dict(slide=s, start=st_, voice_on=round(on[li] + off, 3), text=lines[li][1],
                 how="문장시작" if any(se[0] == li for se in SENT) else HOW.get(li, ""))
        tl["subs"].append(d)
    wait = QUIZ_WAIT if s in QUIZ else SELF_WAIT if s in SELF else HOLD_END if s == LAST else GAP
    end = q(b + off + wait)
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(a + off, 3), voice_end=round(b + off, 3),
                             gap_after_voice=round(end - (b + off), 3), wait="문제" if s in QUIZ else "스스로" if s in SELF else "마지막" if s == LAST else "텀",
                             src_offset=round(off, 4)))
    if s == LAST:
        t0 = round(a + off - B["speech_out"][0], 4)          # 클립 말 시작 = 타입캐스트 마무리 말 시작
        tl["anchors"].append({"name": "끝인사", "in": start, "clip": f"_작업/{N:02d}강/아나운서/{N:02d}_끝인사_090.mp4", "clip_t0": t0,
                              "clip_dur": B["dur_out"], "clip_speech": B["speech_out"], "tc_speech": [round(a + off, 3), round(b + off, 3)],
                              "warp_ratio": round((b - a) / (B["speech_out"][1] - B["speech_out"][0]), 3), "audio": "클립 소리 끔 · 소리 = v090 마지막 장(타입캐스트 마무리) → 2단계 warp_clip.py"})
    cut = end
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1
    x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut
T = cut
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(LEAD=LEAD, GAP_voice_to_cut=GAP, QUIZ_WAIT=QUIZ_WAIT, SELF_WAIT=SELF_WAIT, HOLD_END=HOLD_END, QUIZ=sorted(QUIZ), SELF=sorted(SELF), MAXC=MAXC,
                    voice=f"녹음_본문_04-20강/마루시공_-_{N:02d}강.mp3 atempo=0.9", announcer=("남자" if N % 2 else "여자") + " · 표지 인삿말 + 마지막 장 끝인사만, 2번 없음",
                    bgm={6:"Warm Rhodes Lounge",8:"Clear Focus",16:"Clear Focus",17:"Focused Flow",18:"Warm Rhodes Lounge",19:"Approxima",20:"Clear Focus"}.get(N, "?") + " (BGM/ · 「(1)」 아닌 파일 · −20dB 곡마다 실측 · 지금_규칙 10)", 구조="민석 확정 B안 + 규칙 18(소리 = 타입캐스트)")
json.dump(tl, open("../타임라인_초안.json", "w"), ensure_ascii=False, indent=1)
print("QUIZ", sorted(QUIZ), "SELF", sorted(SELF), "LAST", LAST)
print("자막", len(tl["subs"]), "(인삿말", len(glines), ") 최장", max(len(x["text"]) for x in tl["subs"]), "총길이", tl["total"], f"({int(tl['total']//60)}:{tl['total']%60:04.1f})")
print("warp 비율 인삿말", tl["anchors"][0]["warp_ratio"], "끝인사", tl["anchors"][-1]["warp_ratio"])
