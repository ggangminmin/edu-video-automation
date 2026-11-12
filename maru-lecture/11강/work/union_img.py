import subprocess, numpy as np
from PIL import Image
W, H = 788, 1402
KEY = ("chromakey=0x01FA04:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[c][m];"
       "[m]alphaextract,erosion,erosion,gblur=sigma=1.2[a];[c][a]alphamerge,scale=788:1402,format=rgba,alphaextract")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "greet_warp.mp4", "-filter_complex", "[0:v]" + KEY, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
cnt = np.zeros((H, W), np.int32); bb = []
while True:
    b = p.stdout.read(W * H)
    if len(b) < W * H: break
    a = np.frombuffer(b, np.uint8).reshape(H, W) > 24; cnt += a
    c = np.where(a[:1040].any(0))[0]; bb.append((c.min(), c.max()))
bb = np.array(bb); print("프레임별 x min 분포", np.percentile(bb[:, 0], [0, 5, 50, 95, 100]), "max", np.percentile(bb[:, 1], [0, 5, 50, 95, 100]))
im = (np.clip(cnt / cnt.max(), 0, 1) ** 0.3 * 255).astype(np.uint8)
Image.fromarray(im[:1040]).save("/private/tmp/claude-501/-Users-mac-production-Library-Mobile-Documents-com-apple-CloudDocs-minming-personl-prj--------261022------------/de3c13a9-97f8-4928-ae13-631cde05fa15/scratchpad/union.png")
np.save("greet_alpha_count.npy", cnt)
