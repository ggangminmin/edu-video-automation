# 5ms RMS(깨끗한 v4) 새 줄 앞 쉼 → 실소리
import numpy as np
c = np.load("clean_v4.npy").astype(np.float64)
for nm, a, b in (("n90", 377.40, 377.52), ("n109", 447.80, 447.98)):
    s = c[int(a*48000):int(b*48000)]; f = s[:len(s)//240*240].reshape(-1,240); d = 20*np.log10(np.sqrt((f**2).mean(1))+1e-12)
    print(nm, " ".join(f"{a+i*0.005:.3f}:{v:.1f}" for i, v in enumerate(d)))
