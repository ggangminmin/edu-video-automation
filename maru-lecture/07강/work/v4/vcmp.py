# 영상: v3(t) vs v4(t 또는 t+Δ) RGB 평균차 표본 · 바뀐 카드 프레임 시트 · mix 앞부분 같음
import subprocess, numpy as np, json
from PIL import Image, ImageDraw
D = -0.033367
def fr(p, t): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.4f}","-i",p,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout, np.uint8).reshape(1080,1920,3)
V3, V4 = "../../07강_v3.mp4", "../../07강_v4.mp4"; R = {}
ts = [5,60,150,250,300,360,376.5] + [390,420,460,500,600,700,800,880,900,910,920]
for t in ts:
    t4 = t if t < 377 else t + D
    R[str(t)] = round(float(np.abs(fr(V3,t+0.017).astype(int)-fr(V4,t4+0.017).astype(int)).mean()), 4)
# mix 앞부분
def pcm(p, a, b): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",str(a),"-to",str(b),"-i",p,"-f","s16le","-ac","2","-"],capture_output=True).stdout, np.int16).astype(int)
m3, m4 = pcm("../mix_v3.wav",0,377.39), pcm("../mix_v4.wav",0,377.39); n=min(len(m3),len(m4)); R["mix 0~377.39 최대차 LSB"] = int(np.abs(m3[:n]-m4[:n]).max())
json.dump(R, open("../../검사_v4/화면비교.json","w"), ensure_ascii=False, indent=1); print(R)
# 바뀐 카드 시트: n90 시작 · n91 · n108 · n109 시작 −1/0/+1 프레임
F = 1001/30000; tiles = []
for nm, t in (("n90 6:17.39", 377.391), ("n108 7:25.11", 445.111), ("n109 7:27.87", 447.865)):
    for k in (-1, 0, 1):
        im = Image.fromarray(fr(V4, t + k*F + 0.005)).crop((0, 780, 1920, 1080)).resize((960,150)); d = ImageDraw.Draw(im); d.text((8,4), f"{nm} {k:+d}f", fill=(255,0,0)); tiles.append(im)
S = Image.new("RGB", (960, 150*len(tiles))); [S.paste(im, (0, 150*i)) for i, im in enumerate(tiles)]; S.save("../../검사_v4/바뀐카드.jpg", quality=85)
