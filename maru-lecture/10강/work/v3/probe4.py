# v4b #30 「시공할」 실소리: 5ms RMS + 후보마다 앞 창(앞말 끝까지)·뒤 창 받아쓰기
exec(open("v3/make_v3.py").read().split("new = []")[0])
a, b = 129.8, 130.7; i0 = int(a * FR)
print("RMS", ' '.join(f'{(i0+k)/FR:.3f}:{int(v)}' for k, v in enumerate(db[i0:int(b*FR)])))
print("−50 밑", pauses(a, b))
import mlx_whisper
def asr(x, y):
    yv = V[max(0, int(x * SR)):int(y * SR)]
    return mlx_whisper.transcribe(yv, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
for t in [130.10, 130.15, 130.20, 130.25, 130.30, 130.35, 130.40]:
    print(t, "|", asr(t - 1.0, t), "|", asr(t, t + 1.2), flush=True)
