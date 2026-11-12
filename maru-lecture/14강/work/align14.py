# 14강 1단계 초안 (11강 align.py 복사·수정) — 메모 대본 → 자막 줄 분할 → 받아쓰기 강제정렬 → 슬라이드/자막 타임라인(출력 시간축)
import json, re, subprocess, difflib, bisect
W = "."
notes = json.load(open("../notes_clean.json"))          # 슬라이드별 대본 줄(제목줄·교재: 이하 제외)
MAXC = 35                                               # 00강 실측 한 줄 최대 35자(공백 포함)
QUIZ = {15, 17, 19, 21, 23}                             # 문제 슬라이드(낭독 뒤 대기)
COVER = 3.0          # 표지 길이(판단)
POST = 0.30          # 앞 음성 끝 → 컷 (00강 0.07~0.29)
PRE = 1.00           # 컷 → 다음 음성 (오더 d: 1.0초 이상)
QUIZ_WAIT = 5.5      # 문제 낭독 끝 → 컷 (오더 e: 5~6초)
LEAD = 0.09          # 자막이 음성보다 먼저 (00강 중앙 0.09)
HOLD_END = 3.5       # 마지막 음성 끝 → 엔딩 전환 (00강 3.5)

STRONG = ("고", "며", "면", "는데", "지만", "므로", "뒤", "때는", "해서", "어서", "아서", "려면", "려니")
CONNECT = ("고", "며", "면", "서", "는데", "지만", "뒤", "때는", "므로", "니다", "하고", "해", "에서", "으로", "로", "를", "을", "는", "은", "와", "과", "때", "도")

FORCE = {  # 14강: 단어(바닥 보정비·시공 방법) 가운데서 끊기지 않게 공백 있는 자리에서 나눔
    "견적은 자재비·시공비·부자재비·철거비·바닥 보정비·운반비 등으로 구성됩니다": ["견적은 자재비·시공비·부자재비·철거비·바닥 보정비·운반비", "등으로 구성됩니다"],
    "견적서에는 공사 개요·수량·자재 명세·시공 방법·하자보증·결제 조건을 넣습니다": ["견적서에는 공사 개요·수량·자재 명세·시공 방법·하자보증·결제", "조건을 넣습니다"]}
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

import numpy as np
def _char_first(words):
    tch=[];tt=[]
    for a,b,w in words:
        cs=norm_chars(w)
        for k,c in enumerate(cs): tch.append(c); tt.append(a+(b-a)*k/max(1,len(cs)))
    sm2=difflib.SequenceMatcher(None,sch,tch,autojunk=False); st=[None]*len(sch)
    for a,b,n in sm2.get_matching_blocks():
        for k in range(n): st[a+k]=tt[b+k]
    ix=[i for i,v in enumerate(st) if v is not None]
    for i in range(len(st)):
        if st[i] is None:
            j=bisect.bisect(ix,i); lo=ix[j-1] if j>0 else ix[0]; hi=ix[j] if j<len(ix) else ix[-1]
            st[i]=st[lo] if hi==lo else st[lo]+(st[hi]-st[lo])*(i-lo)/(hi-lo)
    return [st[first_char[i]] for i in range(len(lines))]
MLX_LINE=_char_first([tuple(x) for x in json.load(open("mlxwords.json"))])
_raw=subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
_x=np.frombuffer(_raw,np.int16).astype(float)/32768; _n=len(_x)//80
RMSDB=20*np.log10(np.sqrt((_x[:_n*80].reshape(_n,80)**2).mean(1))+1e-6)
# 14강: 문장 시작 = 긴 무음(≥0.6초) 끝을 순서대로 1:1 대응 (긴 무음 149개 = 문장 150개 − 1 실측 일치)
#        받아쓰기 시각이 ±1초 흔들려 문장 첫머리가 앞 문장 안 짧은 쉼에 붙던 문제(예: 18번 「정답은 삼 번입니다」 1.57초 이르게) 해결
LONG = [(a0, b0) for a0, b0 in SIL if b0 - a0 >= 0.6 and a0 > 0.01 and b0 < DUR - 0.01]
assert len(LONG) == len(SENT) - 1, (len(LONG), len(SENT))
WHIS = [on[sent[0]] for sent in SENT]
for k, sent in enumerate(SENT):
    if k > 0: on[sent[0]] = round(LONG[k - 1][1], 3)
DEV = [round(on[sent[0]] - min(WHIS[k], MLX_LINE[sent[0]], key=lambda w: abs(w - on[sent[0]])), 2) for k, sent in enumerate(SENT)]
print("문장 시작: 긴 무음 대응 ↔ 받아쓰기 최대 차", max(map(abs, DEV)))
SENT_END = {k: (LONG[k][0] if k < len(LONG) else DUR) for k in range(len(SENT))}
# v2: 문장 안에서 쪼갠 줄 = mlx-whisper 단어 시각(linetimes.json) → 앞 무음 끝 또는 음량 골짜기 뒤 다시 오르는 지점
TM = MLX_LINE           # evalsync.py 가 만든 줄별 첫 글자 시각(mlx-whisper word_timestamps)
DB = RMSDB; H = 0.005                    # 16k 음성 RMS(dB), 5ms 간격
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
        on[i] = round(min(max(t, on[i - 1] + 0.5), SENT_END[si] - 0.5), 3)
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

# --- 출력 시간축 조립 (14강 초안 · v3 규칙)
# 경계: 앞 말 끝 → (텀, 앞 장면·앞 자막 유지) → 컷 = 새 장면 + 새 자막 같은 프레임 → LEAD(0.09) 뒤 말 시작
GAP = POST + PRE                     # 보통 넘김 무음 합계 1.30초 (11강 v2 값 그대로, 위치만 컷 앞으로)
FPS = 30000 / 1001
def fr(t): return round(round(t * FPS) / FPS, 3)          # 프레임 격자에 맞춤
GREET = dict(clip="../아나운서/14_인삿말_090.mp4", dur=18.352,
             lines=[(0.921, "안녕하세요, 마루시공전문가 민간자격 온라인 강의"), (5.401, "제14강에 오신 여러분을 환영합니다"),
                    (8.771, "14강에서는 마루시공 견적을 작성하는 방법과"), (12.803, "고객에게 작업 내용을 설명하고 응대하는 방법을 배웁니다")])
BYE_SIL_END = [1.000, 5.098, 6.796, 8.553, 9.341, 9.992, 11.041, 13.413, 17.001]
BYE_W = json.load(open("greet/14_끝인사_090_w.json"))["transcription"]
BYE = dict(clip="../아나운서/14_끝인사_090.mp4", dur=21.021, sent_on=[1.000, 6.796, 13.413])
tl = {"slides": [], "subs": [], "audio": [], "anchor": []}
def add_sub(slide, st, on, text):
    tl["subs"].append({"n": len(tl["subs"]) + 1, "slide": slide, "start": fr(st), "end": None, "voice_on": round(on, 3), "text": text})
# 1) 표지 + 인삿말 (슬라이드 1 유지, 아나운서 클립 0초 = 영상 0초)
T = 0.0
for g_on, g_t in GREET["lines"]: add_sub(1, max(0.0, g_on - LEAD), g_on, g_t)
tl["anchor"].append({"part": "인삿말", "clip": GREET["clip"], "out": 0.0, "dur": GREET["dur"], "audio": "클립 소리(0.9배)"})
T = GREET["dur"]
tl["slides"].append({"slide": 1, "start": 0.0, "end": fr(T), "note": "표지 + 인삿말(짝수 하이젠 0.9배)"})
# 2) 본문 2~24번 (방장 11/2 20:1x 확정: 2번 아나운서 없음 · 25번 클로징은 끝인사 클립이 대신, 타입캐스트 클로징 구간 안 씀)
LAST = slides[-1]
for k, s in enumerate(slides[:-1]):
    a, b, lis = src[s]
    seg0 = max(0.0, a - 0.05) if k == 0 else max(a - 0.05, src[slides[k-1]][1] + 0.05)
    start = T; off = start + LEAD - a                       # 컷 뒤 LEAD 에 말 시작
    seg1 = min(b + 0.05, DUR)
    vstart = seg0 + off
    tl["audio"].append({"slide": s, "out": round(vstart, 3), "src_from": round(seg0, 3), "src_to": round(seg1, 3)})
    vend = b + off
    end = vend + (QUIZ_WAIT if s in QUIZ else GAP - LEAD)      # 문제 = 낭독 끝→컷 5.5초 / 보통 = 다음 컷 뒤 LEAD 에 말 → 무음 합계 GAP
    end = fr(end)
    for j, li in enumerate(lis):
        st = start if j == 0 else on[li] + off - LEAD           # 첫 줄 = 컷 프레임
        add_sub(s, st, on[li] + off, lines[li][1])
    tl["slides"].append({"slide": s, "start": fr(start), "end": end, "voice_start": round(a + off, 3), "voice_end": round(vend, 3),
                         "gap_after_voice": round(end - vend, 3), "lead_after_cut": round(a + off - start, 3),
                         "quiz_wait": s in QUIZ, "src_offset": round(off, 4)})
    T = end
# 3) 25번 클로징 = 끝인사 클립(소리·영상 0.9배) — 컷 = 클립 첫 말 −LEAD, 클립은 그 지점부터(앞 idle 은 컷 앞이라 잘라냄, 움직이는 중)
bye_lines = []
for p in notes[LAST - 1]:
    for parts in make_lines([p]): bye_lines.append(parts)
assert len(bye_lines) == len(BYE["sent_on"]), (len(bye_lines), "끝인사 문장 수 ≠ 25번 메모 문장 수")
CLIP_FROM = BYE["sent_on"][0] - LEAD
START25 = T; G0 = T - CLIP_FROM                              # G0 = 클립 0초가 놓일 출력 시각(가상)
for so, parts in zip(BYE["sent_on"], bye_lines):
    t0 = so
    for j, ptxt in enumerate(parts):
        if j > 0:   # 문장 안 쪼갠 줄: 끝인사 받아쓰기 단어 시각(greet/14_끝인사_090_w.json), 무음 끝이 0.25초 안이면 그쪽
            w0 = ptxt.split()[0][:2]
            wt = next(x["offsets"]["from"] / 1000 for x in BYE_W if x["text"].strip().startswith(w0) and x["offsets"]["from"] / 1000 > so)
            near = [e for e in BYE_SIL_END if abs(e - wt) <= 0.25]
            t0 = near[0] if near else wt
        add_sub(LAST, START25 if (so == BYE["sent_on"][0] and j == 0) else G0 + t0 - LEAD, G0 + t0, ptxt)
tl["anchor"].append({"part": "클로징=끝인사", "clip": BYE["clip"], "out": round(START25, 3), "clip_from": round(CLIP_FROM, 3),
                     "dur": round(BYE["dur"] - CLIP_FROM, 3), "audio": "클립 소리(0.9배) · 타입캐스트 클로징 안 씀"})
T = fr(G0 + BYE["dur"])                                      # 클립 끝(손 모은 자세) = 엔딩 전환 시작. 마지막 말 끝 뒤 1.38초(00강 3.5초)
tl["slides"].append({"slide": LAST, "start": fr(START25), "end": T, "voice_start": round(G0 + BYE["sent_on"][0], 3),
                     "voice_end": round(G0 + 19.642, 3), "lead_after_cut": LEAD, "note": "끝인사 클립이 클로징 대신"})
for x, y in zip(tl["subs"], tl["subs"][1:]): x["end"] = y["start"]      # 빈 바 0
tl["subs"][-1]["end"] = T
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(GAP=GAP, QUIZ_WAIT=QUIZ_WAIT, LEAD=LEAD, MAXC=MAXC, QUIZ=sorted(QUIZ), draft="1단계 초안 — 2단계는 11강 v3 확정 스크립트로 다시 만든다",
                    voice="11-19강/마루시공_-_14강.mp3 atempo=0.9", bgm="BGM/Approxima.mp3 -20dB(방장 결정표 확인 필요)",
                    announcer="여(짝수) · 1번 인삿말 클립 · 2번 없음 · 25번 끝인사 클립 (새 생성 없음, 방장 11/2 20:1x 확정)")
json.dump(tl, open("../타임라인_초안.json", "w"), ensure_ascii=False, indent=1)
# 검산: 장면 경계마다 새 자막 시작 = 컷 프레임, 옛 자막이 새 장면에 남는지
bad = 0
for sl in tl["slides"][1:]:
    first = next(x for x in tl["subs"] if x["slide"] == sl["slide"])
    if abs(first["start"] - sl["start"]) > 0.001: bad += 1; print("경계 불일치", sl["slide"], first["start"], sl["start"])
early = [x for x in tl["subs"] if x["voice_on"] - x["start"] > 0.16 or x["voice_on"] - x["start"] < -0.001]
print("자막 줄", len(tl["subs"]), "최장", max(len(x["text"]) for x in tl["subs"]), "총길이", tl["total"], "경계불일치", bad,
      "선행>0.16 또는 늦음", len(early))
for x in early: print("  ", x["n"], x["slide"], round(x["voice_on"] - x["start"], 3), x["text"])
for x in tl["slides"]: print({k: x[k] for k in x if k in ("slide","start","end","gap_after_voice","lead_after_cut","quiz_wait")})
