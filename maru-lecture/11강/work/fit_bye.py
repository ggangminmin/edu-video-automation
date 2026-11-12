import subprocess, numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
W, H = 799, 1421; Y0 = 36
KEY = ("chromakey=0x01FA04:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[c][m];"
       "[m]alphaextract,erosion,erosion,gblur=sigma=1.2[a];[c][a]alphamerge,scale=799:1421,format=rgba,alphaextract")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "bye_warp.mp4", "-filter_complex", "[0:v]" + KEY, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
cnt = np.zeros((H, W), np.int32)
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    cnt += np.frombuffer(b, np.uint8).reshape(H, W) > 24
np.save("bye_alpha_count.npy", cnt)
vis = (cnt >= 1)[:1080 - Y0]; c = np.where(vis[:, :700].any(0))[0]; print("몸 캔버스 x", c.min(), c.max(), "가장자리 열 프레임수", cnt[:1044, 700:].max())
vis[:, 700:] = False
s = np.asarray(Image.open("../slides/s-27.png").convert("RGB")).astype(int)
bg = np.median(s[600:700, 100:400].reshape(-1, 3), 0)
C = np.abs(s - bg).max(2) > 18; C[905:] = False; Dt = distance_transform_edt(~C)
def clr(x):
    m = np.zeros((1080, 1920), bool); m[Y0:1080, x:x + W] = vis[:, :min(W, 1920 - x)]; return float(Dt[m].min())
print("지금 x=952 최소거리", clr(952))
cc = np.where(C[100:850].any(0))[0]; print("내용 열 범위", cc.min(), cc.max())
