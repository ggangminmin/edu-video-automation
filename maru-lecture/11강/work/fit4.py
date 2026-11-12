import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
cnt = np.load("greet_alpha_count.npy"); vis = (cnt >= 1)[:1040]; vis[:, 700:] = False      # 오른쪽 테두리 잔상 열 제외(렌더에서 crop)
s = np.asarray(Image.open("../slides/s-01.png").convert("RGB")).astype(int)
C = np.abs(s - [248, 245, 240]).max(2) > 18; C[905:] = False
Dt = distance_transform_edt(~C)
res = []
for x in range(400, 520):
    m = np.zeros((1080, 1920), bool); m[40:1080, x:x + 788] = vis
    res.append((x, float(Dt[m].min())))
best = max(res, key=lambda r: r[1]); print("가장 넓게 띄운 x", best); print([r for r in res if r[0] % 5 == 0])
