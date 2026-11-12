# #9 표지 인삿말 아나운서 x 정하기: 키잉 알파(렌더와 같은 체인·788x1402) 전 프레임 합집합 ↔ s-01 글자·사진 영역
import subprocess, numpy as np, sys
from PIL import Image
W, H = 788, 1402; Y0 = 40
KEY = ("chromakey=0x01FA04:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[c][m];"
       "[m]alphaextract,erosion,erosion,gblur=sigma=1.2[a];[c][a]alphamerge,scale=788:1402,format=rgba,alphaextract")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "greet_warp.mp4", "-filter_complex", "[0:v]" + KEY, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
U = np.zeros((H, W), bool); n = 0
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    U |= np.frombuffer(b, np.uint8).reshape(H, W) > 24; n += 1
vis = U[:1080 - Y0]                                   # 화면에 보이는 줄만
cols = np.where(vis.any(0))[0]; print("프레임", n, "알파 합집합 캔버스 x", cols.min(), cols.max())
s = np.asarray(Image.open("../slides/s-01.png").convert("RGB")).astype(int)
bg = np.median(s[600:700, 700:1000].reshape(-1, 3), 0); print("배경색", bg)
C = (np.abs(s - bg).max(2) > 18)                      # 글자·사진 등 배경 아닌 곳
C[905:] = False                                       # 자막바 자리(어차피 자막바가 덮음)
best = None
for x in range(300, 700):
    m = np.zeros((1080, 1920), bool); m[Y0:1080, x:x + W] = vis
    k = int((m & C).sum())
    if best is None or k < best[1] or (k == best[1] and abs(x + (cols.min() + cols.max()) / 2 - 851) < abs(best[0] + (cols.min() + cols.max()) / 2 - 851)): best = (x, k)
x = int(sys.argv[1]) if len(sys.argv) > 1 else best[0]
m = np.zeros((1080, 1920), bool); m[Y0:1080, x:x + W] = vis
print("최소 겹침 x", best, "| 선택 x", x, "겹침 픽셀", int((m & C).sum()), "몸 화면 x", x + cols.min(), "~", x + cols.max())
cc = np.where(C[150:850].any(0))[0]
left = cc[cc < 851].max(); right = cc[cc > 851].min(); print("빈 열(150~850)", left + 1, "~", right - 1, "| 여백 왼", x + cols.min() - left - 1, "오른", right - 1 - (x + cols.max()))
