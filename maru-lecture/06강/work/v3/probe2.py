# 새 나눔 4곳 후보마다 앞 창 [t-1.0,t](앞말 끝까지) · 뒤 창 [t,t+1.2] 받아쓰기 (깨끗한 음성)
exec(open("v3/base.py").read())
import mlx_whisper
def asr(x, y):
    return mlx_whisper.transcribe(V[max(0, int(x * SR)):int(y * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
C = {93: [389.62, 389.67, 389.70, 389.715, 389.73, 389.78],
     144: [611.95, 611.98, 612.015, 612.06, 612.15, 612.28, 612.34],
     81: [340.98, 341.02, 341.05, 341.07, 341.12, 341.25],
     119: [507.30, 507.36, 507.45, 507.55, 507.64, 507.66, 507.70]}
for k, ts in C.items():
    for t in ts: print(k, t, "| 앞", asr(t - 1.0, t), "| 뒤", asr(t, t + 1.2), flush=True)
