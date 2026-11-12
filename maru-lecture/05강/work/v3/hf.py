# 10ms 마다 3kHz 이상 에너지 비율(마찰음 ㅅ·ㅈ = 높음 · 비음 ㄴ·ㅁ·모음 = 낮음)
import sys, numpy as np; sys.path.insert(0, "v3"); from voice import *
a, b = map(float, sys.argv[1].split(":"))
for t in np.arange(a, b, 0.01):
    y = V[int(t*SR):int((t+0.01)*SR)]; f = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2; fr = np.fft.rfftfreq(len(y), 1/SR)
    e = f.sum() + 1e-12; print(f"{t:.3f} dB{10*np.log10(e/len(y)+1e-12):6.1f} 고역{f[fr>3000].sum()/e:5.2f}")
