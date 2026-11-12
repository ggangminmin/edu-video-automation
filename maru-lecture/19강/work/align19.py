# 19강 1단계 타임라인 초안 — 11강 align.py(줄 분할·강제정렬) + align_v3.py(장면·자막 동기, 팀장 구조) 복사·수정
#  자막 = 메모 그대로(띄어쓰기·쉼표·숫자 손대지 않음, 마침표만 00강 방식으로 뺌) · 한 줄 최대 35자에서만 나눔
#  텀은 장면 바뀌기 전: 말 끝 → 1.21초 → 컷(장면+새 자막 같은 프레임) → 0.09초 → 말 · 문제 대기 5.5 · 끝 3.5
import json, re, subprocess, difflib, bisect, os, sys
import numpy as np
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
notes = json.load(open("../notes_clean.json"))
MAXC = 35; LEAD = 0.09; POST, PRE, QUIZ_WAIT, HOLD_END = 0.30, 1.00, 5.5, 3.5
GAP = POST + PRE - LEAD
QUIZ = {16, 18, 20, 22, 24}
SELF = {14}                 # 「스스로 확인하기」 — 대기 5.5초 여부 민석 결정 대기(SELF_WAIT=1 이면 5.5)
if os.environ.get("SELF_WAIT") == "1": QUIZ |= SELF
LAST = 26
CL = json.load(open("clips.json"))      # 인삿말·끝인사 클립(cut_clips.py 결과)

STRONG = ("고", "며", "면", "는데", "지만", "므로", "뒤", "때는", "해서", "어서", "아서", "려면", "려니")
CONNECT = ("고", "며", "면", "서", "는데", "지만", "뒤", "때는", "므로", "니다", "하고", "해", "에서", "으로", "로", "를", "을", "는", "은", "와", "과", "때", "도")
def split_line(s):
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
NUMK = {"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "6": "육", "7": "칠", "8": "팔", "9": "구", "0": "영"}
def norm_chars(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]

W = json.load(open("mlxwords.json"))["words"]
tch, tt = [], []
for a, b, w in W:
    cs = norm_chars(w)
    for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))
def silences(path, d):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n=-40dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]
    return list(zip(st, en + [9999] * (len(st) - len(en))))
SIL = silences("v090.wav", 0.08); S5 = silences("v090.wav", 0.05)
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "v090.wav"]))
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", "v090_16k.wav", "-f", "s16le", "-ac", "1", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
H = 0.005; hop = 80; fr = x[:len(x) // hop * hop].reshape(-1, hop); DB = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-6)

lines, SENT = [], []
for si, paras in enumerate(notes, 1):
    if si == 1: continue
    for parts in make_lines(paras):
        SENT.append(list(range(len(lines), len(lines) + len(parts))))
        for t in parts: lines.append((si, t))
sch, sline = [], []
for li, (_, t) in enumerate(lines):
    for c in norm_chars(t): sch.append(c); sline.append(li)
# 숫자는 받아쓰기에서 한글로 읽히므로(메모도 「일 번」 식) 그대로 비교
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
# 안 맞은 구간(대본 ≠ 음성 후보) 기록
diff = []
for op, a0, a1, b0, b1 in sm.get_opcodes():
    if op != "equal" and max(a1 - a0, b1 - b0) >= 2:
        diff.append(dict(op=op, line=lines[sline[min(a0, len(sline) - 1)]][1], script="".join(sch[a0:a1]), heard="".join(tch[b0:b1]), t=round(tt[min(b0, len(tt) - 1)], 2)))
json.dump(diff, open("align_diff.json", "w"), ensure_ascii=False, indent=1)

def snap_onset(t, lo=-0.6, hi=1.2):
    for s0, e0 in SIL:
        if s0 - 0.05 <= t <= e0: return e0
    c = [e for s0, e in SIL if t + lo <= e <= t + hi]
    return min(c, key=lambda e: abs(e - t)) if c else t
def sil_before(t):
    c = [s0 for s0, e0 in SIL if abs(e0 - t) < 0.002]
    return c[0] if c else t
def cont_onset(est, prev):
    c = [(s0, e0) for s0, e0 in S5 if est - 0.5 <= s0 <= est + 0.3 and est - 0.05 <= e0 <= est + 0.8 and s0 > prev + 0.3]
    if c: return min(c, key=lambda z: abs(z[1] - est))[1], "무음끝"
    a0 = int((est - 0.12) / H); b0 = int((est + 0.3) / H)
    i = int(np.argmin(DB[a0:b0])); j = a0 + i
    while j < b0 + 40 and DB[j] < DB[a0 + i] + 6: j += 1
    return j * H, "골짜기"
first_char = {}
for i, li in enumerate(sline): first_char.setdefault(li, i)
on = [None] * len(lines); HOW = {}
for sent in SENT:
    on[sent[0]] = round(snap_onset(stime[first_char[sent[0]]]), 3); HOW[sent[0]] = "문장시작"
    for i in sent[1:]:
        t, how = cont_onset(stime[first_char[i]], on[i - 1]); HOW[i] = how
        on[i] = round(max(t, on[i - 1] + 0.5), 3)
on[0] = SIL[0][1] if SIL and SIL[0][0] == 0 else on[0]
slides = sorted(set(s for s, _ in lines))
src = {}
for s in slides:
    lis = [i for i, (ss, _) in enumerate(lines) if ss == s]
    nxt = lis[-1] + 1
    b = sil_before(on[nxt]) if nxt < len(lines) else max(s0 for s0, e0 in SIL if s0 < DUR - 0.01 and e0 >= DUR - 0.05)
    src[s] = (on[lis[0]], b, lis)

G, B = CL["인삿말"], CL["끝인사"]
tl = {"slides": [], "subs": [], "audio": [], "anchors": []}
tl["audio"].append(dict(slide=1, out=0.0, src_from=0.0, src_to=G["dur"], src=G["wav"], gain=G.get("gain", 1.0)))
tl["anchors"].append({"name": "인삿말", "in": 0.0, "clip": G["clip"], "clip_t0": 0.0})
for t, txt in zip(G["on"], G["lines"]):
    tl["subs"].append(dict(slide=1, start=q(t - LEAD), voice_on=round(t, 3), text=txt, part="인삿말"))
cut = q(G["dur"])
tl["slides"].append(dict(slide=1, start=0.0, end=cut, note="표지 + 팀장 인삿말"))
for k, s in enumerate(slides):
    a, b, lis = src[s]
    ls = [dict(text=lines[i][1], on=on[i], how=HOW.get(i, "")) for i in lis]
    if s == LAST:                                       # 마지막 장 = 팀장 끝인사 클립(클로징 나레이션 대신)
        ls = [dict(text=t, on=o, how="끝인사") for t, o in zip(B["lines"], B["on"])]
        a, b = B["on"][0], B["voice_end"]
    start = cut; off = start + LEAD - a
    if s == LAST:
        tl["audio"].append(dict(slide=s, out=round(off, 4), src_from=0.0, src_to=B["dur"], src=B["wav"], gain=B.get("gain", 1.0)))
    else:
        prev_b = src[slides[k - 1]][1] if k else 0.0
        s0 = 0.0 if s == 2 else max(a - 0.05, prev_b + 0.05); s1 = min(b + 0.05, DUR)
        tl["audio"].append(dict(slide=s, out=round(s0 + off, 4), src_from=round(s0, 4), src_to=round(s1, 4)))
    for j, l in enumerate(ls):
        st = start if j == 0 else q(l["on"] + off - LEAD)
        tl["subs"].append(dict(slide=s, start=st, voice_on=round(l["on"] + off, 3), text=l["text"], how=l["how"]))
    wait = QUIZ_WAIT if s in QUIZ else (HOLD_END if s == LAST else GAP)
    end = q(b + off + wait)
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(a + off, 3), voice_end=round(b + off, 3),
                             gap_after_voice=round(end - (b + off), 3), gap_before_voice=round(a + off - start, 3), quiz_wait=s in QUIZ, src_offset=round(off, 4)))
    if s == LAST:
        tl["anchors"].append({"name": "끝인사", "in": start, "clip": B["clip"], "clip_t0": round(off, 4), "out": q(off + B["dur"])})
    cut = end
for i, x_ in enumerate(tl["subs"]):
    x_["n"] = i + 1
    x_["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut
T = cut
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(LEAD=LEAD, GAP_voice_to_cut=GAP, QUIZ_WAIT=QUIZ_WAIT, QUIZ=sorted(QUIZ), HOLD_END=HOLD_END, MAXC=MAXC,
                    voice="11-19강/마루시공_-_19강.mp3 atempo=0.9 → work/v090.wav", bgm="BGM/Approxima.mp3 -20dB",
                    구조="표지+팀장 인삿말(0.9배) → 2 아나운서 없음 → 본문 → 26 = 팀장 끝인사(0.9배) → 엔딩", 상태="1단계 초안(렌더 안 함)")
json.dump(tl, open("../타임라인_초안.json", "w"), ensure_ascii=False, indent=1)
print("자막", len(tl["subs"]), "최장", max(len(s["text"]) for s in tl["subs"]), "총길이", tl["total"])
for s_ in tl["slides"]: print(s_["slide"], round(s_["start"], 2), round(s_["end"], 2), s_.get("gap_before_voice"), s_.get("gap_after_voice"))
