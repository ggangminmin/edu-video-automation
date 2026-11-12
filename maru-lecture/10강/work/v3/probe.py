# 나눔 10곳: 둘째 장 첫 어절 실소리 후보마다 받아쓰기 [t-0.9,t] / [t,t+1.2]
import json, re, numpy as np, sys
sys.argv = ["x"]; exec(open("v3/make_v3.py").read().split("new = []")[0])
import mlx_whisper
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
rep = json.load(open("v3/rep.json")); out = {}
for r in rep:
    if r[0] != "나눔": continue
    i, info = r[1], r[5]; ref = info["ref"]
    c = [p[1] for p in pauses(ref - 0.7, ref + 0.45)]
    i0, i1 = int((ref - 0.6) * FR), int((ref + 0.4) * FR)
    c += [round(m / FR, 3) for m in range(i0, i1) if db[m] <= -38 and db[m] == db[m - 4:m + 5].min()]
    c = sorted(set(c)); res = []
    for t in c:
        res.append((t, round(float(db[int(t * FR)]), 1), asr(t - 0.9, t - 0.01), asr(t + 0.0, t + 1.2)))
        print(i, r[4][:30], res[-1], flush=True)
    out[i] = res
json.dump(out, open("v3/probe.json", "w"), ensure_ascii=False, indent=1)
