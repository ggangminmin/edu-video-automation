# 바뀐 카드 밖 newline_onset 걸림·판정불가 4줄(19·168·177·215) 세 근거: 앞 창 [t−1,t] · 뒤 창 [t,t+1.2]
import sys, json; sys.path.insert(0, "v3"); from voice import *
import mlx_whisper
def asr(a, b): return mlx_whisper.transcribe(V[int(a*SR):int(b*SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
P = {19: [64.135, 64.20, 64.25, 64.30], 168: [676.84, 676.89, 676.93, 677.02], 177: [707.965, 708.00, 708.04, 708.10], 215: [861.72, 861.80, 861.87, 861.90, 861.95]}
out = {}
for i, ts in P.items():
    for t in ts:
        r = (i, t, round(float(db[int(t*FR)]), 1), asr(t - 1.0, t), asr(t, t + 1.2)); out.setdefault(i, []).append(r[1:]); print(r, flush=True)
json.dump(out, open("v3/probe3.json", "w"), ensure_ascii=False, indent=1)
