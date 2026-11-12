# 클릭 찾기: >4kHz 고역 순간값이 둘레 50ms 고역 RMS 의 10배(20dB) 넘는 점 · 사용: clicks.py <wav|mp4> [a b]
import numpy as np, subprocess, sys
from scipy.signal import butter, sosfiltfilt
SR = 48000; p = sys.argv[1]
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, len(x)/SR)
x = x[int(a*SR):int(b*SR)]; h = sosfiltfilt(butter(4, 4000, "hp", fs=SR, output="sos"), x)
w = 2400; e = np.sqrt(np.convolve(h**2, np.ones(w)/w, "same")) + 1e-6
idx = np.where((np.abs(h) > 10*e) & (np.abs(h) > 10**(-50/20)))[0]
ev = []
for i in idx:
    if not ev or i - ev[-1][0] > 480: ev.append([i, abs(h[i])])
print(p.split("/")[-1], f"{a}~{b}", "클릭", len(ev), [ (round(a+i/SR,3), round(20*np.log10(v),1)) for i, v in ev[:20]])
