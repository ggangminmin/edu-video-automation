# 오더15: fix_bound 미해결(→ None) 경계 다시 — 받아쓰기 동음 오인(범위는→범인은)을 자모 비교로 허용, 후보 창 넓힘(−1.2~+0.6초)
#  조건: [t, t+1.3] 받아쓰기 앞머리 ≈ 그 줄 첫 3글자(자모 ≥0.6) · [t−1, t] 끝 6글자 안에 그 줄 첫 2글자 없음(자모 ≥0.8)
#        + [t−1, t] 끝이 앞 줄 끝말 ≈(자모 ≥0.5) — 앞 줄이 다 끝난 뒤
#  결과 = onset_override.json 에 더함(줄번호: 시각). 고른 근거는 fix_bound2.log
import json, re, difflib, numpy as np, subprocess, mlx_whisper
tl = json.load(open("../타임라인_초안.json")); off = {s["slide"]: s.get("src_offset", 0) for s in tl["slides"]}
BODY = [x for x in tl["subs"] if "part" not in x]
DB = np.load("rmsdb.npy"); H = 0.005
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
NUMK = {"0":"영","1":"일","2":"이","3":"삼","4":"사","5":"오","6":"육","7":"칠","8":"팔","9":"구"}
CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"; JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"; JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"
def jamo(s):
    out = []
    for c in s:
        c = NUMK.get(c, c); o = ord(c[0]) - 0xAC00
        for ch in c:
            o = ord(ch) - 0xAC00
            if 0 <= o < 11172: out += [CHO[o // 588], JUNG[(o % 588) // 28]] + ([JONG[o % 28]] if o % 28 else [])
            else: out.append(ch)
    return out
def jr(a, b): return difflib.SequenceMatcher(None, jamo(a), jamo(b)).ratio()
def starts(after, head): return max(jr(after[:len(head) + k], head) for k in (-1, 0, 1)) >= 0.6
def has_head(before, head): return any(jr(before[-len(head) - k:][:len(head)], head) >= 0.8 for k in range(0, 5))
def ends_prev(before, tail): return max(jr(before[-len(tail) - k:], tail) for k in (0, 1, 2)) >= 0.5
log = open("fix_bound.log").read()
import sys
targets = [int(a) for a in sys.argv[1:]] or [int(l.split()[0]) for l in log.splitlines() if "→ None" in l]   # 인자 = 다시 볼 자막 번호(줄 나눔 바꾼 뒤)
over = json.load(open("onset_override.json")) if __import__("os").path.exists("onset_override.json") else {}
LOGF = "fix_bound3.log" if sys.argv[1:] else "fix_bound2.log"
out = open(LOGF, "w")
for N in targets:
    s = tl["subs"][N - 1]; prev = tl["subs"][N - 2]; LI = BODY.index(s)
    on = s["voice_on"] - off[s["slide"]]; pon = prev["voice_on"] - off[prev["slide"]]
    head = n(s["text"])[:3]; tail = n(prev["text"])[-3:]
    a0 = int(max(pon + 0.4, on - 1.2) / H); b0 = int((on + 0.6) / H); seg = DB[a0:b0]
    mins = [a0 + i for i in range(2, len(seg) - 2) if seg[i] == seg[i-2:i+3].min() and seg[i] < seg[max(0,i-20):i+20].max() - 4]
    cands = []
    for j in mins:
        k = j
        while k < j + 40 and DB[k] < DB[j] + 6: k += 1
        cands.append(round(k * H, 3))
    pick = None; rows = []
    for t in sorted(set(cands)):
        af, bf = tr(t, t + 1.3), tr(max(0, t - 1.0), t)
        ok = starts(af, head) and not has_head(bf, head[:2]) and ends_prev(bf, tail)
        rows.append((t, ok, af[:9], bf[-9:]))
        if ok: pick = t; break
    msg = f"{N} {s['text'][:16]} | 앞줄끝 {tail} | 원래 {round(on,3)} → {pick} {rows}"
    print(msg, flush=True); out.write(msg + "\n")
    if pick is not None: over[str(LI)] = pick
out.close(); json.dump(over, open("onset_override.json", "w"), indent=1)
print("미해결", len(targets), "→ 이번에 고름", sum(1 for l in open(LOGF) if "→ None" not in l))
