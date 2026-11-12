import sys, json; sys.path.insert(0, "v3"); from voice import *
import mlx_whisper
def asr(a, b):
    return mlx_whisper.transcribe(V[int(a*SR):int(b*SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
P = {99: [406.10, 406.27, 406.30, 406.35], 223: [888.45, 888.62, 888.74, 888.80], 229: [907.10, 907.17, 907.215, 907.26], 11: [41.55, 41.62], 81: [335.86, 335.95], 91: [375.145, 375.235], 193: [770.45, 770.51, 770.585]}
out = {}
for i, ts in P.items():
    for t in ts:
        r = (i, t, round(float(db[int(t*FR)]), 1), asr(t - 1.0, t), asr(t, t + 1.2)); out.setdefault(i, []).append(r[1:]); print(r, flush=True)
json.dump(out, open("v3/probe2.json", "w"), ensure_ascii=False, indent=1)
