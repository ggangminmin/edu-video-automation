# verify_on.py 에서 걸린 줄만: 말 시작 후보(음량 골짜기 뒤 상승·무음 끝, on-1.2 ~ on+0.3)를 이른 순으로
# 짧은 구간 받아쓰기 → 「그 줄 첫 말로 시작 + 앞 1초 끝엔 없음」 첫 후보 채택 → onset_override.json (align13_v1 이 읽음)
import json, re, difflib, numpy as np, subprocess, mlx_whisper, sys
V = json.load(open("verify_on.json")); bad = [r for r in V if not r["ok"]]
NG = 5                                                     # 초안 타임라인 앞 인삿말 줄 수 → 대본 줄 번호 = n-1-NG
DB = np.load("rmsdb.npy"); H = 0.005
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    r = mlx_whisper.transcribe(x[int(max(0,a)*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
NUM = {"일":"1","이":"2","삼":"3","사":"4","십":"10"}
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
def heads(t): h = n(t)[:3]; return {h, "".join(NUM.get(c, c) for c in h)}
def starts(af, t): return max(difflib.SequenceMatcher(None, af[:len(h)], h).ratio() for h in heads(t)) >= 0.6
def ends_with(bf, t): return any(difflib.SequenceMatcher(None, bf[-len(h)-k:][:len(h)], h).ratio() >= 0.75 for h in heads(t) for k in range(3))
over = {}
for r in bad:
    i = r["n"] - 1 - NG; on = r["on"]; text = r["text"]
    full = None
    a0, b0 = int((on - 1.2) / H), int((on + 0.3) / H); seg = DB[a0:b0]
    mins = [a0 + k for k in range(2, len(seg) - 2) if seg[k] == seg[k-2:k+3].min() and seg[k] < seg[max(0,k-20):k+20].max() - 6]
    cands = set()
    for j in mins:
        k = j
        while k < j + 40 and DB[k] < DB[j] + 6: k += 1
        cands.add(round(k * H, 3))
    pick, log = None, []
    for t in sorted(cands):
        af, bf = tr(t, t + 1.3), tr(max(0, t - 1.0), t)
        ok = starts(af, text) and not ends_with(bf, text); log.append((t, ok, af[:8], bf[-8:]))
        if ok: pick = t; break
    print(r["n"], text, "원래", on, "→", pick, log, flush=True)
    if pick is not None and abs(pick - on) > 0.02: over[i] = pick
json.dump(over, open("onset_override.json", "w"), indent=1)
print("보정", over)
