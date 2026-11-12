exec(open("v3/make_v3.py").read().split("new = []")[0])
import mlx_whisper
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
for t in [719.12, 719.17, 719.22, 719.27, 719.32, 503.30, 503.43]:
    print(t, "|", asr(t - 1.0, t), "|", asr(t, t + 1.2), flush=True)
