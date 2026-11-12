# 215 「곳에 / 알맞은」: 「에」→「알」 모음 경계 — 앞 창 받아쓰기 + 저역 무게중심(에 F2 높음 → 아 F2 낮음)
import sys, numpy as np; sys.path.insert(0, "v3"); from voice import *
import mlx_whisper
def asr(a, b): return mlx_whisper.transcribe(V[int(a*SR):int(b*SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
for t in np.arange(861.87, 862.12, 0.01):
    y = V[int(t*SR):int((t+0.02)*SR)]; f = np.abs(np.fft.rfft(y*np.hanning(len(y))))**2; fr = np.fft.rfftfreq(len(y), 1/SR); m = (fr > 200) & (fr < 3000)
    print(f"{t:.3f} 중심 {int((f[m]*fr[m]).sum()/f[m].sum())}Hz  1k~2.5k비 {f[(fr>1000)&(fr<2500)].sum()/f[m].sum():.2f}")
for t in (861.97, 862.00, 862.03, 862.06):
    print(t, asr(t - 1.0, t), "|", asr(t, t + 1.2), flush=True)
