# 15강 1단계 타임라인 초안 — 11강 v2 align.py 복사본을 15강용으로 고치고 v3 확정 규칙(인수인계)을 반영
#  · 메모 대본(제목줄·교재: 제외) → 자막 줄 분할 → 0.9배 음성 받아쓰기 강제정렬
#  · 텀은 장면 바뀌기 전에: 앞 말 끝 → (앞 장면·앞 자막 유지) → 다음 장면+새 자막 같은 프레임 → LEAD(0.09) 뒤 말 시작
#  · 구조: 표지+인삿말(아나운서) → 2번 오프닝 → 본문 → 25번 클로징 → 끝인사(아나운서) → 엔딩
#  2단계에선 11강 v3 확정 스크립트로 다시 만든다(이 파일은 초안).
import json, re, subprocess, difflib, bisect, os
import numpy as np
notes = json.load(open("../notes_clean.json"))
MAXC = 35
QUIZ = {15, 17, 19, 21, 23}          # 15강 문제 슬라이드(메모 「문제 N」) — 낭독 뒤 대기
TERM = 1.30          # 페이지 넘김 말-말 무음(11강 v2 POST 0.30 + PRE 1.00 합 그대로, 장면 바뀌기 전에 둠)
QUIZ_WAIT = 5.5      # 문제 낭독 끝 → 컷
LEAD = 0.09          # 자막·장면이 말보다 먼저
HOLD_END = 3.5       # 마지막 음성 끝 → 엔딩 전환(00강)
GREET_TEXT = ["안녕하세요. 마루시공전문가 민간자격 온라인 강의 제15강에 오신 여러분을 환영합니다.",
              "15강에서는 마루에 발생하는 하자의 종류를 알아보고, 현장 상태를 바탕으로 원인을 조사하는 방법을 살펴봅니다."]  # 강의인삿말/audio_14 (받아쓰기·파일명 대조)
AMETA = json.load(open("../아나운서/meta.json"))       # cut_greet.py 결과(인삿말·끝인사 0.9배 길이·말 시작)

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

tr = json.load(open("wfull.json"))["transcription"]
tch, tt = [], []
for w in tr:
    cs = norm_chars(w["text"]); a, b = w["offsets"]["from"]/1000, w["offsets"]["to"]/1000
    for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))

def silences(path, d):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n=-40dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return list(zip(st, en + [9999] * (len(st) - len(en))))
SIL = silences("v090.wav", 0.08)
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "v090.wav"]))

lines, SENT = [], []
for si, paras in enumerate(notes, 1):
    for parts in make_lines(paras):
        SENT.append(list(range(len(lines), len(lines) + len(parts))))
        for t in parts: lines.append((si, t))
json.dump([t for _, t in lines], open("lines.json", "w"), ensure_ascii=False)   # linetimes_make.py 입력
if not os.path.exists("linetimes.json"): raise SystemExit(f"lines.json {len(lines)}줄 저장 — linetimes_make.py 먼저")
sch, sline = [], []
for li, (_, t) in enumerate(lines):
    for c in norm_chars(t): sch.append(c); sline.append(li)
sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False)
stime = [None] * len(sch)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): stime[a + k] = tt[b + k]
idx = [i for i, v in enumerate(stime) if v is not None]
for i in range(len(stime)):
    if stime[i] is None:
        j = bisect.bisect(idx, i); lo = idx[j-1] if j > 0 else None; hi = idx[j] if j < len(idx) else None
        stime[i] = stime[hi] if lo is None else stime[lo] if hi is None else stime[lo] + (stime[hi] - stime[lo]) * (i - lo) / (hi - lo)
matched = sum(n for _, _, n in sm.get_matching_blocks())
print(f"정렬 일치 글자 {matched}/{len(sch)} = {matched/len(sch):.1%}")

def snap_onset(t, lo=-0.6, hi=0.35):
    for s0, e0 in SIL:
        if s0 - 0.05 <= t <= e0: return e0
    c = [e for s0, e in SIL if t + lo <= e <= t + hi]
    return min(c, key=lambda e: abs(e - t)) if c else t
def sil_before(t):
    c = [s0 for s0, e0 in SIL if abs(e0 - t) < 0.002]
    return c[0] if c else t
first_char = {}
for i, li in enumerate(sline): first_char.setdefault(li, i)
on = [None] * len(lines); SNAPPED = 0
for sent in SENT:
    on[sent[0]] = round(snap_onset(stime[first_char[sent[0]]], -0.6, 1.2), 3)
    if any(abs(e - on[sent[0]]) < 0.002 for _, e in SIL): SNAPPED += 1
DB = np.load("rmsdb.npy"); H = 0.005
S5 = silences("v090.wav", 0.05)
HOW = {}
def cont_onset(est, prev):
    c = [(s0, e0) for s0, e0 in S5 if est - 0.5 <= s0 <= est + 0.3 and est - 0.05 <= e0 <= est + 0.8 and s0 > prev + 0.3]
    if c: return min(c, key=lambda z: abs(z[1] - est))[1], "무음끝"
    a0 = int((est - 0.12) / H); b0 = int((est + 0.3) / H)
    i = int(np.argmin(DB[a0:b0])); j = a0 + i
    while j < b0 + 40 and DB[j] < DB[a0 + i] + 6: j += 1
    return j * H, "골짜기"
TM = json.load(open("linetimes.json"))["mlx"]
assert len(TM) == len(lines)
for sent in SENT:
    for i in sent[1:]:
        t, how = cont_onset(TM[i], on[i - 1]); HOW[i] = how
        on[i] = round(max(t, on[i - 1] + 0.5), 3)
OVR = {int(k): v for k, v in json.load(open("onset_override.json")).items()} if os.path.exists("onset_override.json") else {}
for i, v in OVR.items(): on[i] = v; HOW[i] = "받아쓰기보정"
print(f"문장 시작 {SNAPPED}/{len(SENT)} 이 무음 끝에 붙음 · 보정 {len(OVR)}")
on[0] = SIL[0][1] if SIL and SIL[0][0] == 0 else on[0]

slides = sorted(set(s for s, _ in lines))
src = {}
for s in slides:
    lis = [i for i, (ss, _) in enumerate(lines) if ss == s]
    a = on[lis[0]]
    b = sil_before(on[lis[-1] + 1]) if lis[-1] + 1 < len(lines) else max(s0 for s0, e0 in SIL if s0 < DUR - 0.01 and e0 >= DUR - 0.05)
    src[s] = (a, b, lis)

# --- 출력 시간축 (민석 확정 11/2 20:1x B안: 표지+인삿말 클립 → 2번(아나운서 없음) … 24 → 25번 = 끝인사 클립이 클로징 대신 → 엔딩)
tl = {"slides": [], "subs": [], "audio": [], "announcer": []}
G = AMETA["인삿말"]; B = AMETA["끝인사"]
g_dur = G["dur_out"]
tl["announcer"].append({"part": "인삿말", "file": "_작업/15강/아나운서/15_인삿말_090.mp4", "out": 0.0, "dur": g_dur, "speech": G["speech_out"]})
# 인삿말 자막: 두 문장, 무음 경계(문장 사이)로 나눔 — 2단계에서 받아쓰기 강제정렬로 교체
gs = G["speech_out"]
g_mid = round((110.246 - G["src_from"]) / 0.9, 3)   # 모음 음성 무음 109.594~110.246 끝 = 둘째 문장 시작(0.9배 환산)
def prop_lines(sents, t0, t1, mids, part, slide):
    # 문장 시작 = mids(무음 경계), 문장 안 줄 = 글자 수 비례(초안 — 2단계에서 받아쓰기 강제정렬)
    starts = [t0] + mids; ends = mids + [t1]
    for sent, a, b in zip(sents, starts, ends):
        parts = sum(make_lines([sent]), []); tot = sum(len(norm_chars(x)) for x in parts); acc = 0
        for x in parts:
            v = round(a + (b - a) * acc / tot, 3); acc += len(norm_chars(x))
            tl["subs"].append({"n": len(tl["subs"]) + 1, "slide": slide, "part": part, "start": round(v - LEAD, 3), "end": None, "voice_on": v, "text": x, "how": "초안비례"})
prop_lines(GREET_TEXT, gs[0], gs[1], [g_mid], "인삿말", 1)
greet_voice_end = gs[1]
prev_end_voice = greet_voice_end; prev_quiz = False
T_cut = None
cover_start = 0.0
for k, s in enumerate(slides[:-1]):                  # 25번 타입캐스트 클로징 구간은 쓰지 않음
    a, b, lis = src[s]
    gap = QUIZ_WAIT + LEAD if prev_quiz else TERM
    v_a = prev_end_voice + gap            # 이 슬라이드 첫 말 출력 시각
    if s == 2: v_a = max(v_a, g_dur + LEAD)   # 오프닝은 인삿말 클립이 끝난 뒤
    cut = round(v_a - LEAD, 3)            # 장면 바뀌는 시각(텀은 그 앞)
    if not tl["slides"]: tl["slides"].append({"slide": 1, "start": 0.0, "end": cut, "note": "표지 + 아나운서 인삿말"})
    else: tl["slides"][-1]["end"] = cut
    seg0 = 0.0 if s == 2 else max(a - 0.05, src[slides[k-1]][1] + 0.05)
    seg1 = min(b + 0.05, DUR)
    off = v_a - a
    tl["audio"].append({"slide": s, "out": round(seg0 + off, 3), "src_from": round(seg0, 3), "src_to": round(seg1, 3)})
    for j, li in enumerate(lis):
        st = cut if j == 0 else on[li] + off - LEAD
        tl["subs"].append({"n": len(tl["subs"]) + 1, "slide": s, "start": round(st, 3), "end": None,
                           "voice_on": round(on[li] + off, 3), "text": lines[li][1], "how": "문장시작" if any(se[0] == li for se in SENT) else HOW.get(li, "")})
    tl["slides"].append({"slide": s, "start": cut, "end": None, "voice_start": round(a + off, 3), "voice_end": round(b + off, 3),
                         "quiz_wait": s in QUIZ, "src_offset": round(off, 4)})
    prev_end_voice = b + off; prev_quiz = s in QUIZ
# 25번 클로징 = 끝인사 클립(0.9배)으로 교체 — 장면·첫 자막 같은 프레임, 0.09초 뒤 끝인사 말 시작
last = slides[-1]
cut = round(prev_end_voice + (QUIZ_WAIT + LEAD if prev_quiz else TERM) - LEAD, 3)
tl["slides"][-1]["end"] = cut
bye_v = cut + LEAD
bye_out = round(bye_v - B["speech_out"][0], 3)          # 클립 0초가 놓일 자리(실제 등장은 cut, 클립 안 in점부터 = 이미 움직이는 중)
clip_in = round(cut - bye_out, 3)
tl["announcer"].append({"part": "끝인사(=클로징)", "file": "_작업/15강/아나운서/15_끝인사_090.mp4", "show_from": cut, "clip_in": clip_in,
                        "dur": round(B["dur_out"] - clip_in, 3), "speech": [round(bye_v, 3), round(bye_out + B["speech_out"][1], 3)], "audio": "클립 소리(0.9배) 사용 · 타입캐스트 클로징 안 씀"})
tl["slides"].append({"slide": last, "start": cut, "end": None, "voice_start": round(bye_v, 3), "voice_end": round(bye_out + B["speech_out"][1], 3), "quiz_wait": False, "note": "끝인사 클립이 클로징 대신"})
BYE_TEXT = re.split(r"(?<=[.?])\s+", notes[last - 1][0])   # 끝인사 받아쓰기 = 25번 메모와 글자 같음
b_m = [round(bye_out + (x - B["src_from"]) / 0.9, 3) for x in (126.780, 129.894)]   # 모음 무음 끝(문장 시작)
n0 = len(tl["subs"])
prop_lines(BYE_TEXT, round(bye_v, 3), round(bye_out + B["speech_out"][1], 3), b_m, "끝인사", last)
tl["subs"][n0]["start"] = cut
T = round(bye_out + B["speech_out"][1] + HOLD_END, 3)
tl["slides"][-1]["end"] = T
for x, y in zip(tl["subs"], tl["subs"][1:]): x["end"] = y["start"]          # 빈 바 0
tl["subs"][-1]["end"] = round(bye_out + B["speech_out"][1] + 0.3, 3)
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(TERM=TERM, QUIZ_WAIT=QUIZ_WAIT, LEAD=LEAD, HOLD_END=HOLD_END, MAXC=MAXC, QUIZ=sorted(QUIZ),
                    voice="11-19강/마루시공_-_15강.mp3 atempo=0.9", announcer="남자(홀수강) · 표지 인삿말 + 25번 끝인사만, 2번 없음", bgm="방장 결정표대로(미정)")
json.dump(tl, open("../타임라인_초안.json", "w"), ensure_ascii=False, indent=1)
print("자막 줄", len(tl["subs"]), "최장", max(len(x["text"]) for x in tl["subs"]), "총길이", tl["total"])
for x in tl["slides"]: print({k: x.get(k) for k in ("slide", "start", "end", "voice_start", "voice_end", "quiz_wait")})
