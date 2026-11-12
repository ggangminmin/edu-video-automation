# 10강(오더43): 모든 자막 줄 시작 = 실소리 − 0.09 (18강 onset_v4 · newline_onset_check v2 와 같은 실소리 정의) + 받아쓰기 확인
#  실소리 = 깨끗한 음성(타임라인 audio 대로 · BGM 없음) 5ms RMS · 기준점(voice_on) ±0.3 안 −50dB 밑 ≥30ms 쉼 중 끝이 기준점에 가장 가까운 것 → 뒤 −50dB 30ms 넘는 첫 시각
#           쉼 없으면 ±0.15 안 −45dB 밑 지역 최소(골짜기) · 그것도 없으면 「이어진 말」 = 그대로 두고 표시(받아쓰기 자르기로 손 확인)
#  장 첫 줄(= 장 컷) 은 옮기지 않고 선행만 잼 · 받아쓰기: [on−0.9, on−0.03] 끝에 첫 어절 없음 · [on−0.03, on+1.3] 첫 어절로 시작
#  손값 MAN = {줄 글자 앞부분: 실소리 초} (받아쓰기 자르기로 확인한 것만)
# 실행(work): ~/.venvs/tts/bin/python onset10.py <입력 타임라인> <출력 타임라인> <결과 json>  (받아쓰기 → heavy_run asr)
import sys, json, re, os, subprocess, numpy as np
src_tl, out_tl, out_js = sys.argv[1:4]
tl = json.load(open(src_tl)); SR, H = 16000, 80; FR = SR / H; TH, RUN, SHALLOW, GAP = -50.0, 6, -45.0, 6
MAN = {k: v for k, v in json.load(open("onset_man.json")).items() if not k.startswith("_")} if os.path.exists("onset_man.json") else {}
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
def onset(ref):
    i0, i1 = max(0, int((ref - 0.3) * FR)), min(len(db) - RUN, int((ref + 0.3) * FR)); seg = db[i0:i1]; runs = []; j = 0
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
    v0, v1 = max(3, int((ref - 0.15) * FR)), min(len(db) - 4, int((ref + 0.15) * FR))
    vs = [m for m in range(v0, v1) if db[m] <= SHALLOW and db[m] == db[m - 3:m + 4].min()]
    if not vs: return None, "이어진 말"
    m = min(vs, key=lambda m: abs(m / FR - ref)); return m / FR, "골짜기"
import mlx_whisper
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip() if len(y) > SR * 0.2 else ""
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
NUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5", "십": "1"}
SL = {s["slide"]: s for s in tl["slides"]}; S = tl["subs"]; rows = []
for i, s in enumerate(S):
    first = abs(s["start"] - SL[s["slide"]]["start"]) < 1e-6
    ref = s.get("voice_on") or s["start"] + 0.09
    man = next((v for k, v in MAN.items() if s["text"].startswith(k)), None)
    on, how = (man, "손값") if man is not None else onset(ref)
    r = dict(n=s["n"], slide=s["slide"], text=s["text"], first=first, old_start=round(s["start"], 3), ref=round(ref, 3), onset=None if on is None else round(on, 3), how=how)
    if on is not None and not first:
        ns = on - 0.09
        if i > 0 and ns <= S[i - 1]["start"] + 0.5: r["skip"] = "앞 줄과 너무 가까움"; ns = None
        if ns is not None:
            s["start"] = ns; s["voice_on"] = round(on, 3); S[i - 1]["end"] = ns; s["how_on"] = f"실소리({how}) −0.09"
    r["start"] = round(s["start"], 3); r["lead"] = None if on is None else round(on - s["start"], 3)
    if on is not None:
        w0 = kn(s["text"].split()[0]); h = w0[:2]; h2 = NUM.get(h[0], h[0]) + h[1:]
        aft, bef = kn(asr(on - 0.03, on + 1.3)), kn(asr(on - 0.9, on - 0.03))
        r.update(asr_after=aft[:10], asr_before=bef[-8:], asr_ok=(aft.startswith(h) or aft.startswith(h2)) and h not in bef[-4:])
    rows.append(r); print(r, flush=True)
for a, b in zip(S, S[1:]): assert a["end"] <= b["start"] + 1e-6 and b["start"] > a["start"] + 0.3, (a, b)
tl["params"]["v1_onset"] = "모든 줄 시작 = 실소리(깨끗한 음성 −50dB 30ms 상승 · newline_onset_check 와 같은 정의) − 0.09 · 장 첫 줄은 컷 그대로 · 받아쓰기 확인(onset10.py)"
json.dump(tl, open(out_tl, "w"), ensure_ascii=False, indent=1); json.dump(rows, open(out_js, "w"), ensure_ascii=False, indent=1)
bad = [r for r in rows if r.get("asr_ok") is False or r["onset"] is None or (r["lead"] is not None and not -1e-6 <= r["lead"] <= 0.177 + 1e-6)]
print("줄", len(rows), "· 받아쓰기✗/이어진말/선행 밖", len(bad))
for r in bad: print("  확인", r)
