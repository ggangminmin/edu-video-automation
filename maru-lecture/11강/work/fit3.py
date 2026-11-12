import numpy as np
from PIL import Image
cnt = np.load("greet_alpha_count.npy"); Y0 = 40; vis = (cnt >= 3)[:1040]
s = np.asarray(Image.open("../slides/s-01.png").convert("RGB")).astype(int)
C = np.abs(s - [248, 245, 240]).max(2) > 18; C[905:] = False
for x in (400, 443, 470, 500):
    m = np.zeros((1080, 1920), bool); m[Y0:1080, x:x + 788] = vis; o = m & C
    ys, xs = np.where(o); print(x, "겹침", o.sum(), "y", (ys.min(), ys.max()) if len(ys) else None, "x", (xs.min(), xs.max()) if len(xs) else None)
# 빈 공간 행별: 각 y 에서 851 기준 왼쪽 마지막 내용 x · 오른쪽 첫 내용 x
for y in range(60, 905, 60):
    r = np.where(C[y])[0]; l = r[r < 851]; rr = r[r > 851]
    print(y, l.max() if len(l) else None, rr.min() if len(rr) else None)
