# 13강 초안(v3 규칙) — 11강 align.py 복사본. 메모 대본 → 자막 줄 분할 → 받아쓰기 강제정렬 → 슬라이드/자막 타임라인(출력 시간축)
import json, re, subprocess, difflib, bisect
W = "."
notes = json.load(open("../notes_clean.json"))          # 슬라이드별 대본 줄(제목줄·교재: 이하 제외)
MAXC = 35                                               # 00강 실측 한 줄 최대 35자(공백 포함)
QUIZ = {18, 20, 22, 24, 26}                             # 문제 슬라이드(낭독 뒤 대기)
COVER = 3.0          # 표지 길이(판단)
POST = 0.30          # 앞 음성 끝 → 컷 (00강 0.07~0.29)
PRE = 1.00           # 컷 → 다음 음성 (오더 d: 1.0초 이상)
QUIZ_WAIT = 5.5      # 문제 낭독 끝 → 컷 (오더 e: 5~6초)
LEAD = 0.09          # 자막이 음성보다 먼저 (00강 중앙 0.09)
HOLD_END = 3.5       # 마지막 음성 끝 → 엔딩 전환 (00강 3.5)

STRONG = ("고", "며", "면", "는데", "지만", "므로", "뒤", "때는", "해서", "어서", "아서", "려면", "려니")
CONNECT = ("고", "며", "면", "서", "는데", "지만", "뒤", "때는", "므로", "니다", "하고", "해", "에서", "으로", "로", "를", "을", "는", "은", "와", "과", "때", "도")

FORCE = {}
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
CPP_OK = [v is not None for v in stime]
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
# 13강: 받아쓰기가 확인문제 보기 낭독을 통째로 건너뛰는 곳(18번 cpp · 26번 mlx)이 있어 문장 시작이 앞당겨짐
#   → mlx 단어로도 같은 정렬을 하고 두 값이 1초 넘게 다르면 늦은 쪽(건너뛰면 항상 일찍 잡힘)
_ch, _tt = [], []
for _a, _b, _w in json.load(open("mlxwords.json")):
    _cs = norm_chars(_w)
    for k, c in enumerate(_cs): _ch.append(c); _tt.append(_a + (_b - _a) * k / max(1, len(_cs)))
_sm = difflib.SequenceMatcher(None, sch, _ch, autojunk=False); stime_m = [None] * len(sch)
for a, b, n in _sm.get_matching_blocks():
    for k in range(n): stime_m[a + k] = _tt[b + k]
DISAGREE = []
for si, sent in enumerate(SENT):
    t = stime[first_char[sent[0]]]
    fc = first_char[sent[0]]; tm = stime_m[fc]
    if tm is None:                                   # 「일 번」↔「1번」처럼 첫 글자가 숫자 표기로 어긋나면 그 줄의 첫 일치 글자
        k = fc
        while k < len(sch) and sline[k] == sent[0] and stime_m[k] is None: k += 1
        tm = stime_m[k] - 0.12 * (k - fc) if k < len(sch) and sline[k] == sent[0] else None
    if not CPP_OK[first_char[sent[0]]] and tm is not None:          # cpp 가 이 글자를 못 받아씀(보간값) → mlx
        DISAGREE.append((sent[0], lines[sent[0]][1][:16], "cpp없음", round(t, 2), round(tm, 2))); t = tm
    elif tm is not None and abs(tm - t) > 1.0:
        DISAGREE.append((sent[0], lines[sent[0]][1][:16], round(t, 2), round(tm, 2))); t = max(t, tm)
    on[sent[0]] = round(snap_onset(t, -0.6, 1.2), 3)
    if any(abs(e - on[sent[0]]) < 0.002 for _, e in SIL): SNAPPED += 1
# v2: 문장 안에서 쪼갠 줄 = mlx-whisper 단어 시각(linetimes.json) → 앞 무음 끝 또는 음량 골짜기 뒤 다시 오르는 지점
import numpy as np
def char_times(words):     # 11강 linetimes_make.py 와 같은 방식(줄별 첫 글자 시각)
    tch=[];tt=[]
    for a_,b_,w_ in words:
        cs=norm_chars(w_)
        for k,c in enumerate(cs): tch.append(c); tt.append(a_+(b_-a_)*k/max(1,len(cs)))
    sm_=difflib.SequenceMatcher(None,sch,tch,autojunk=False); st=[None]*len(sch)
    for a_,b_,n_ in sm_.get_matching_blocks():
        for k in range(n_): st[a_+k]=tt[b_+k]
    ix=[i for i,v in enumerate(st) if v is not None]
    for i in range(len(st)):
        if st[i] is None:
            j=bisect.bisect(ix,i); lo=ix[j-1] if j>0 else ix[0]; hi=ix[j] if j<len(ix) else ix[-1]
            st[i]=st[lo] if hi==lo else st[lo]+(st[hi]-st[lo])*(i-lo)/(hi-lo)
    first={}
    for i,l in enumerate(sline): first.setdefault(l,st[i])
    return [first[i] for i in range(len(lines))]
TM = char_times([tuple(x) for x in json.load(open("mlxwords.json"))])
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
print(f"문장 시작 {SNAPPED}/{len(SENT)} 이 무음 끝에 붙음"); print("cpp↔mlx 1초 넘게 다른 문장 시작(늦은 쪽 채택):", DISAGREE)
on[0] = SIL[0][1] if SIL and SIL[0][0] == 0 else on[0]

slides = sorted(set(s for s, _ in lines))
src = {}  # slide -> 원본(0.9배) 소리 시작·끝
for k, s in enumerate(slides):
    lis = [i for i, (ss, _) in enumerate(lines) if ss == s]
    a = on[lis[0]]
    nxt = on[lis[-1] + 1] if lis[-1] + 1 < len(lines) else DUR
    b = sil_before(nxt) if lis[-1] + 1 < len(lines) else max(s0 for s0, e0 in SIL if s0 < DUR - 0.01 and e0 >= DUR - 0.05)
    src[s] = (a, b, lis)

# --- 출력 시간축 조립 (v3 확정 규칙: 텀은 장면 바뀌기 전 · 장면과 새 자막 같은 프레임 · 그 뒤 LEAD 초에 말)
GAP = POST + PRE                 # 앞 말 끝 → 다음 말 시작 무음(11강 v2 값 0.30+1.00 그대로, 위치만 컷 앞으로)
AN = "../아나운서"
def clip_lines(wav, wjson, sents):
    # 인삿말·끝인사 클립: 문장 → 줄 분할 → 줄 첫 글자 시각(whisper-cpp 단어) → 무음 끝 스냅
    w = json.load(open(wjson))["transcription"]; ch, tt_ = [], []
    for x in w:
        cs = norm_chars(x["text"]); a_, b_ = x["offsets"]["from"]/1000, x["offsets"]["to"]/1000
        for k, c in enumerate(cs): ch.append(c); tt_.append(a_ + (b_ - a_) * k / max(1, len(cs)))
    sil = silences(wav, 0.08); out = []
    L = []
    for snt in sents:
        for j, part in enumerate(split_line(snt)): L.append((part.strip(), j == 0))
    S = "".join("".join(norm_chars(p)) for p, _ in L)
    sm_ = difflib.SequenceMatcher(None, S, "".join(ch), autojunk=False); st = {}
    for a_, b_, n_ in sm_.get_matching_blocks():
        for k in range(n_): st[a_ + k] = tt_[b_ + k]
    pos = 0
    for p, first in L:
        t = st.get(pos, None); pos += len(norm_chars(p))
        inside = [e for s0, e in sil if s0 - 0.05 <= t <= e]          # 받아쓰기 시각이 무음 안 → 그 무음 끝
        c = inside or [e for s0, e in sil if t - 0.6 <= e <= t + 0.35]
        v = min(c, key=lambda e: abs(e - t)) if c else t
        if out and v <= out[-1][1] + 0.5:                              # 받아쓰기가 두 줄을 한 시각으로 묶음 → 다음 무음 끝
            v = min((e for s0, e in sil if e > out[-1][1] + 0.5), default=v)
        out.append((p, round(v, 3)))
    vend = max(s0 for s0, e0 in sil if s0 < DUR_(wav) - 0.01)
    return out, vend
def DUR_(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
# 인삿말 자막 = 강의인삿말/audio_12(제13강) 원음 받아쓰기 문장(원문 대본 파일 없음 → 받아쓰기·띄어쓰기는 메모 대본 표기 기준으로 손질)
GREET = ["안녕하세요", "마루시공전문가 민간자격 온라인 강의 제13강에 오신 여러분을 환영합니다",
         "13강에서는 주거 공간과 상업 공간 등 사용 환경에 따라 달라지는 시공 조건과 적용 방법을 알아봅니다"]
# 끝인사 자막 = 끝인사 모음 받아쓰기(= 28번 메모 대본과 같은 문장 → 대본 표기로)
BYE = ["제품을 고르기 전에 그 바닥을 어떻게 사용할지 들어 보세요", "현장 조건을 구체적으로 알아야 선택 이유도 설명할 수 있습니다",
       "14강에서는 확인한 범위와 조건을 견적, 변경 합의, 고객 인계에 담아 보겠습니다"]
g_lines, g_end = clip_lines(f"{AN}/13_인삿말_090.wav", f"{AN}/13_인삿말_090_w.json", GREET)
b_lines, b_end = clip_lines(f"{AN}/13_끝인사_090.wav", f"{AN}/13_끝인사_090_w.json", BYE)

tl = {"slides": [], "subs": [], "audio": [], "announcer": []}
def add_sub(slide, st, txt, von, how=""):
    tl["subs"].append({"n": len(tl["subs"]) + 1, "slide": slide, "start": round(st, 3), "end": None,
                       "voice_on": round(von, 3), "text": txt, "how": how})
# 1) 표지 + 인삿말(클립 0초 = 출력 0초, 클립 안 말 앞 idle 은 클립에 들어 있음)
G0 = 0.0
tl["announcer"].append({"part": "인삿말", "clip": "아나운서/13_인삿말_090.mp4", "out": G0, "on_slide": 1,
                        "voice": [round(G0 + g_lines[0][1], 3), round(G0 + g_end, 3)]})
tl["audio"].append({"slide": 1, "out": G0, "src": "아나운서/13_인삿말_090.wav", "src_from": 0.0, "src_to": round(g_end + 0.05, 3)})
for p, t in g_lines: add_sub(1, G0 + t - LEAD, p, G0 + t, "인삿말")
prev_end_voice = G0 + g_end; cur_start = 0.0; cur_slide = 1
LAST = slides[-1]
for k, s in enumerate(slides):
    if s == LAST: break                        # 11/2 민석 확정 B안: 마지막 장 = 끝인사 클립 소리(타입캐스트 클로징 안 씀)
    a, b, lis = src[s]
    seg0 = 0.0 if s == 2 else max(a - 0.05, src[slides[k-1]][1] + 0.05)
    seg1 = min(b + 0.05, DUR)
    wait = QUIZ_WAIT + LEAD if cur_slide in QUIZ else GAP
    vstart_a = prev_end_voice + wait           # 이 슬라이드 첫 말(a) 출력 시각
    off = vstart_a - a
    cut = vstart_a - LEAD                      # 장면 컷 = 새 자막 시작
    tl["slides"].append({"slide": cur_slide, "start": round(cur_start, 3), "end": round(cut, 3)})
    cur_start, cur_slide = cut, s
    tl["audio"].append({"slide": s, "out": round(seg0 + off, 3), "src_from": round(seg0, 3), "src_to": round(seg1, 3)})
    for j, li in enumerate(lis):
        st = cut if j == 0 else on[li] + off - LEAD
        add_sub(s, st, lines[li][1], on[li] + off, HOW.get(li, "문장시작" if any(se[0] == li for se in SENT) else ""))
    tl["slides"][-1].update()
    meta = {"voice_start": round(a + off, 3), "voice_end": round(b + off, 3), "quiz_wait": s in QUIZ, "src_offset": round(off, 4)}
    tl.setdefault("_meta", {})[s] = meta
    prev_end_voice = b + off
# 2) 오프닝 아나운서 없음(11/2 민석 확정: 2번 = 슬라이드 + 나레이션만)
# 3) 마지막 장 = 끝인사 클립(영상·소리 0.9배). 장면 컷 = 끝인사 첫 말 −LEAD, 자막 = 28번 메모 대본 줄(끝인사 말과 같은 문장)
wait = QUIZ_WAIT + LEAD if cur_slide in QUIZ else GAP
B_von = prev_end_voice + wait; B_out = B_von - b_lines[0][1]; cut = B_von - LEAD
tl["slides"].append({"slide": cur_slide, "start": round(cur_start, 3), "end": round(cut, 3)})
cur_start, cur_slide = cut, LAST
tl["announcer"].append({"part": "끝인사(클로징 대신)", "clip": "아나운서/13_끝인사_090.mp4", "on_slide": LAST,
                        "out": round(B_out, 3), "show_from": round(cut, 3), "clip_in": round(cut - B_out, 3),
                        "voice": [round(B_von, 3), round(B_out + b_end, 3)]})
tl["audio"].append({"slide": LAST, "out": round(B_out, 3), "src": "아나운서/13_끝인사_090.wav", "src_from": 0.0, "src_to": round(b_end + 0.05, 3)})
assert [norm_chars(p) for p, _ in b_lines] == [norm_chars(lines[li][1]) for li in src[LAST][2]], "끝인사 줄 ≠ 28번 대본 줄"
for (p, t), li in zip(b_lines, src[LAST][2]):
    add_sub(LAST, max(cut, B_out + t - LEAD), lines[li][1], B_out + t, "끝인사")
tl["_meta"][LAST] = {"voice_start": round(B_von, 3), "voice_end": round(B_out + b_end, 3), "quiz_wait": False, "src_offset": None}
T = B_out + b_end + HOLD_END
tl["slides"].append({"slide": cur_slide, "start": round(cur_start, 3), "end": round(T, 3)})
for x, y in zip(tl["subs"], tl["subs"][1:]): x["end"] = y["start"]          # 빈 바 0
tl["subs"][-1]["end"] = round(B_out + b_end + 0.3, 3)
for x in tl["slides"]: x.update(tl["_meta"].get(x["slide"], {}))
del tl["_meta"]
tl["ending"] = {"zoom_blur": [round(T, 3), round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 0.67 + 8.13, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 0.67 + 0.5, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(GAP=GAP, QUIZ_WAIT=QUIZ_WAIT, LEAD=LEAD, HOLD_END=HOLD_END, MAXC=MAXC, QUIZ=sorted(QUIZ),
                    voice="11-19강/마루시공_-_13강.mp3 atempo=0.9 → work/v090.wav", bgm="BGM/Approxima.mp3 -20dB (곡 배정은 방장 결정표)",
                    note="초안(1단계). 2단계에서 11강 v3 확정 스크립트로 다시 만든다")
json.dump(tl, open("../타임라인_초안.json", "w"), ensure_ascii=False, indent=1)
print("자막 줄", len(tl["subs"]), "최장", max(len(x["text"]) for x in tl["subs"]), "총길이", tl["total"])
for x in tl["slides"]: print(x)
for x in tl["announcer"]: print(x)
