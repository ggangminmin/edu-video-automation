# #81 「가 / 실」 경계 가리기 + #144 「지」 조각: 짧은 조각·앞 창 촘촘히
exec(open("v3/base.py").read())
import mlx_whisper
def asr(x, y):
    return mlx_whisper.transcribe(V[max(0, int(x * SR)):int(y * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
for x, y in [(340.575, 341.245), (340.575, 341.03), (341.05, 341.245), (341.25, 341.415), (341.05, 341.415), (612.305, 612.555), (611.9, 612.555), (612.675, 613.24)]:
    print(f"조각 [{x},{y}] 「{asr(x, y)}」", flush=True)
for t in [341.10, 341.15, 341.20, 341.245, 341.30, 341.35]:
    print(f"앞 [{t-1.2:.2f},{t}] 「{asr(t - 1.2, t)}」 | 뒤 0.6 「{asr(t, t + 0.6)}」", flush=True)
