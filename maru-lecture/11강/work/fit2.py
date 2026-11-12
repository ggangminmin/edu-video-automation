import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
cnt = np.load("greet_alpha_count.npy"); Y0 = 40
print("x>650 에 알파 있는 프레임 수(최대)", cnt[:1040, 650:].max())
vis = (cnt >= 3)[:1080 - Y0]                       # 3프레임 이상 나온 곳만(단발 잔상 제외)
s = np.asarray(Image.open("../slides/s-01.png").convert("RGB")).astype(int)
C = np.abs(s - [248, 245, 240]).max(2) > 18; C[905:] = False
for marg in (0, 10, 20, 30):
    D = binary_dilation(C, iterations=marg) if marg else C
    ok = []
    for x in range(250, 750):
        m = np.zeros((1080, 1920), bool); m[Y0:1080, x:x + 788] = vis
        if not (m & D).any(): ok.append(x)
    print(f"여백 {marg}px 로 겹침 0 인 x:", (ok[0], ok[-1]) if ok else "없음")
