# 나눔 자리마다: 단어 시각 근처 쉼(−50dB)·골짜기(≤−38) 후보 → 받아쓰기 앞 창 [t−0.9,t] · 뒤 창 [t,t+1.2]
import json, sys; sys.path.insert(0, "v3")
from voice import *; from plan import SPLIT
import mlx_whisper
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
out = {}
for i, a in SPLIT.items():
    x, y = S[i], S[i + 1]; full = x["text"] + " " + y["text"]; b = full[len(a) + 1:]
    fw = kn(b.split()[0])[:2]; ws = words_out(x["start"], y["end"])
    exp = x["start"] + (y["end"] - x["start"]) * len(a) / len(full)
    cand = [t for t, w in ws if kn(w).startswith(fw)]
    ref = min(cand, key=lambda t: abs(t - exp)) if cand else exp
    c = [p[1] for p in pauses(ref - 0.7, ref + 0.45)]
    i0, i1 = int((ref - 0.6) * FR), int((ref + 0.4) * FR)
    c += [round(m / FR, 3) for m in range(i0, i1) if db[m] <= -38 and db[m] == db[m - 4:m + 5].min()]
    c = sorted(set(c)); res = []
    print(i, a, "/", b, "ref", ref, "exp", round(exp, 3), "pauses", pauses(ref - 0.7, ref + 0.45), [(t, w) for t, w in ws if abs(t - ref) < 1.2], flush=True)
    for t in c:
        res.append((t, round(float(db[int(t * FR)]), 1), asr(t - 0.9, t - 0.01), asr(t, t + 1.2)))
        print("   ", res[-1], flush=True)
    out[i] = dict(ref=ref, exp=exp, res=res)
json.dump(out, open("v3/probe.json", "w"), ensure_ascii=False, indent=1)
