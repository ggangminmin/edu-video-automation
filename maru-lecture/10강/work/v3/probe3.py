exec(open("v3/make_v3.py").read().split("new = []")[0])
print(' '.join(f'{int(db[m])}' for m in range(int(131.4*FR),int(132.1*FR))))
import mlx_whisper
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True)
for t in [131.6, 131.7]:
    print(t, "|", asr(t - 1.0, t)["text"], "|", asr(t, t + 1.2)["text"], flush=True)
r = asr(130.6, 133.4)
for s in r["segments"]:
    for w in s["words"]: print(round(130.6 + w["start"], 3), round(130.6 + w["end"], 3), w["word"])
