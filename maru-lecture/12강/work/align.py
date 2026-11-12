# 11강 v1 — 메모 대본 → 자막 줄 분할 → 받아쓰기 강제정렬 → 슬라이드/자막 타임라인(출력 시간축)
import json, re, subprocess, difflib, bisect
W = "."
notes = json.load(open("../notes_clean.json"))          # 슬라이드별 대본 줄(제목줄·교재: 이하 제외)
MAXC = 35                                               # 00강 실측 한 줄 최대 35자(공백 포함)
QUIZ = {17, 19, 21, 23, 25}                             # 문제 슬라이드(낭독 뒤 대기)
COVER = 3.0          # 표지 길이(판단)
POST = 0.30          # 앞 음성 끝 → 컷 (00강 0.07~0.29)
PRE = 1.00           # 컷 → 다음 음성 (오더 d: 1.0초 이상)
QUIZ_WAIT = 5.5      # 문제 낭독 끝 → 컷 (오더 e: 5~6초)
LEAD = 0.09          # 자막이 음성보다 먼저 (00강 중앙 0.09)
HOLD_END = 3.5       # 마지막 음성 끝 → 엔딩 전환 (00강 3.5)

STRONG = ("고", "며", "면", "는데", "지만", "므로", "뒤", "때는", "해서", "어서", "아서", "려면", "려니")
CONNECT = ("고", "며", "면", "서", "는데", "지만", "뒤", "때는", "므로", "니다", "하고", "해", "에서", "으로", "로", "를", "을", "는", "은", "와", "과", "때", "도")

FORCE = {"기준을 하나로 공유하고 진행 중 확인하는 일이 정밀 패턴 시공의 출발점입니다":   # v2: 「확인하는 / 일이」는 말이 붙어 경계가 안 잡혀 「공유하고」 뒤에서 나눔
         ["기준을 하나로 공유하고", "진행 중 확인하는 일이 정밀 패턴 시공의 출발점입니다"]}
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
        if best is None or score < best[0]: best = (score, L, R)
    L, R = best[1], best[2]
    return split_line(L) + split_line(R)

def make_lines(paras):
    out = []
    for p in paras:
        for sent in re.split(r"(?<=[.?])\s+", p.strip()):
            sent = sent.strip()
            if not sent: continue
            if sent.endswith("."): sent = sent[:-1]          # 마침표 지움(00강), 물음표 남김
            parts = [x.strip() for x in split_line(sent)]
            out.append(parts)
    return out

def norm_chars(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]

# --- 받아쓰기(0.9배 음성 whisper.cpp 단어 단위) → 글자별 시간
tr = json.load(open("wfull.json"))["transcription"]
tch, tt = [], []
for w in tr:
    cs = norm_chars(w["text"]); a, b = w["offsets"]["from"]/1000, w["offsets"]["to"]/1000
    for k, c in enumerate(cs):
        tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))

# --- 무음 구간(-40dB, 0.08s 이상)
def silences(path, d):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n=-40dB:d={d}", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return list(zip(st, en + [9999] * (len(st) - len(en))))
SIL = silences("v090.wav", 0.08)
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "v090.wav"]))

# --- 대본 글자열
lines = []   # (slide, text)
SENT = []    # 문장별 줄 번호 목록
for si, paras in enumerate(notes, 1):
    for parts in make_lines(paras):
        SENT.append(list(range(len(lines), len(lines) + len(parts))))
        for t in parts: lines.append((si, t))
sch, sline = [], []
for li, (_, t) in enumerate(lines):
    for c in norm_chars(t): sch.append(c); sline.append(li)
sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False)
stime = [None] * len(sch)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): stime[a + k] = tt[b + k]
# 보간
idx = [i for i, v in enumerate(stime) if v is not None]
for i in range(len(stime)):
    if stime[i] is None:
        j = bisect.bisect(idx, i)
        lo = idx[j-1] if j > 0 else None; hi = idx[j] if j < len(idx) else None
        if lo is None: stime[i] = stime[hi]
        elif hi is None: stime[i] = stime[lo]
        else: stime[i] = stime[lo] + (stime[hi] - stime[lo]) * (i - lo) / (hi - lo)
matched = sum(n for _, _, n in sm.get_matching_blocks())
print(f"정렬 일치 글자 {matched}/{len(sch)} = {matched/len(sch):.1%}")

def snap_onset(t, lo=-0.6, hi=0.35):
    # 1) whisper 시각이 무음 안에 있으면 그 무음 끝 = 소리 시작  2) 아니면 가까운 무음 끝
    for s0, e0 in SIL:
        if s0 - 0.05 <= t <= e0: return e0
    c = [e for s0, e in SIL if t + lo <= e <= t + hi]
    return min(c, key=lambda e: abs(e - t)) if c else t
def sil_before(t):
    # 소리 시작 t 바로 앞 무음의 시작 = 앞 소리 끝
    c = [s0 for s0, e0 in SIL if abs(e0 - t) < 0.002]
    return c[0] if c else t

first_char = {}
for i, li in enumerate(sline): first_char.setdefault(li, i)
nch = [len(norm_chars(t)) for _, t in lines]
on = [None] * len(lines); SNAPPED = 0
for si, sent in enumerate(SENT):
    t = stime[first_char[sent[0]]]
    on[sent[0]] = round(snap_onset(t, -0.6, 1.2), 3)
    if any(abs(e - on[sent[0]]) < 0.002 for _, e in SIL): SNAPPED += 1
# v2: 문장 안에서 쪼갠 줄 = mlx-whisper 단어 시각(linetimes.json) → 앞 무음 끝 또는 음량 골짜기 뒤 다시 오르는 지점
import numpy as np
TM = json.load(open("linetimes.json"))["mlx"]           # evalsync.py 가 만든 줄별 첫 글자 시각(mlx-whisper word_timestamps)
DB = np.load("rmsdb.npy"); H = 0.005                    # 16k 음성 RMS(dB), 5ms 간격
S5 = silences("v090.wav", 0.05)
HOW = {}
def cont_onset(est, prev):
    c = [(s0, e0) for s0, e0 in S5 if est - 0.5 <= s0 <= est + 0.3 and est - 0.05 <= e0 <= est + 0.8 and s0 > prev + 0.3]
    if c: return min(c, key=lambda z: abs(z[1] - est))[1], "무음끝"
    a0 = int((est - 0.12) / H); b0 = int((est + 0.3) / H)
    i = int(np.argmin(DB[a0:b0])); j = a0 + i
    while j < b0 + 40 and DB[j] < DB[a0 + i] + 6: j += 1
    return j * H, "골짜기"
assert len(TM) == len(lines)
for si, sent in enumerate(SENT):
    for i in sent[1:]:
        t, how = cont_onset(TM[i], on[i - 1]); HOW[i] = how
        on[i] = round(max(t, on[i - 1] + 0.5), 3)
import os
OVR = {int(k): v for k, v in json.load(open("onset_override.json")).items()} if os.path.exists("onset_override.json") else {}
for i, v in OVR.items(): on[i] = v; HOW[i] = "받아쓰기보정"     # fix_bound.py: 앞뒤 받아쓰기로 고른 골짜기
print(f"문장 시작 {SNAPPED}/{len(SENT)} 이 무음 끝에 붙음")
on[0] = SIL[0][1] if SIL and SIL[0][0] == 0 else on[0]

slides = sorted(set(s for s, _ in lines))
src = {}  # slide -> 원본(0.9배) 소리 시작·끝
for k, s in enumerate(slides):
    lis = [i for i, (ss, _) in enumerate(lines) if ss == s]
    a = on[lis[0]]
    nxt = on[lis[-1] + 1] if lis[-1] + 1 < len(lines) else DUR
    b = sil_before(nxt) if lis[-1] + 1 < len(lines) else max(s0 for s0, e0 in SIL if s0 < DUR - 0.01 and e0 >= DUR - 0.05)
    src[s] = (a, b, lis)

# --- 출력 시간축 조립
T = 0.0; tl = {"slides": [], "subs": [], "audio": []}
tl["slides"].append({"slide": 1, "start": 0.0, "end": COVER, "note": "표지(메모 없음) — 음성 없음"})
T = COVER
for k, s in enumerate(slides):
    a, b, lis = src[s]
    if s == 2:
        seg0 = 0.0; pre = 0.0                    # 오프닝 = 원본 0초부터 그대로(하이젠 싱크 유지)
    else:
        seg0 = max(a - 0.05, src[slides[k-1]][1] + 0.05); pre = PRE - (a - seg0)
    seg1 = min(b + 0.05, DUR)
    post = (QUIZ_WAIT if s in QUIZ else (HOLD_END if s == slides[-1] else POST)) - (seg1 - b)
    start = T
    vstart = T + pre                              # 이 슬라이드 원본 seg0 이 놓이는 출력 시각
    tl["audio"].append({"slide": s, "out": round(vstart, 3), "src_from": round(seg0, 3), "src_to": round(seg1, 3)})
    end = vstart + (seg1 - seg0) + post
    off = vstart - seg0
    for j, li in enumerate(lis):
        st = on[li] + off - LEAD
        en = (on[lis[j+1]] + off - LEAD) if j + 1 < len(lis) else end
        if j == 0: st = max(st, start)
        tl["subs"].append({"n": len(tl["subs"]) + 1, "slide": s, "start": round(st, 3), "end": round(en, 3),
                           "voice_on": round(on[li] + off, 3), "text": lines[li][1]})
    tl["slides"].append({"slide": s, "start": round(start, 3), "end": round(end, 3),
                         "voice_start": round(a + off, 3), "voice_end": round(b + off, 3),
                         "gap_after_voice": round(end - (b + off), 3),
                         "gap_before_voice": round(a + off - start, 3), "quiz_wait": s in QUIZ, "src_offset": round(off, 4)})
    T = end
for x, y in zip(tl["subs"], tl["subs"][1:]): x["end"] = y["start"]      # v2: 빈 바 0 (00강처럼 앞 자막 유지)
for k2, x in enumerate(tl["subs"]): x["how"] = "문장시작" if any(sent[0] == k2 for sent in SENT) else HOW.get(k2, "")
tl["ending"] = {"zoom_blur": [round(T, 3), round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 0.67 + 8.13, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 0.67 + 0.5, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(COVER=COVER, POST=POST, PRE=PRE, QUIZ_WAIT=QUIZ_WAIT, LEAD=LEAD, HOLD_END=HOLD_END, MAXC=MAXC,
                    voice="11-19강/마루시공_-_11강.mp3 atempo=0.9", bgm="BGM/Approxima.mp3 -20dB")
json.dump(tl, open("../타임라인.json", "w"), ensure_ascii=False, indent=1)
print("자막 줄", len(tl["subs"]), "최장", max(len(x["text"]) for x in tl["subs"]), "총길이", tl["total"])
for x in tl["slides"]: print(x)
