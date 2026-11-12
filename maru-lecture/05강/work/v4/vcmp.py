# 화면 비교: v3 t ↔ v4 t(78.9 앞) / t+Δ(뒤) · RGB 평균차 · 바뀐 카드 프레임(프레임 번호로)
import subprocess, numpy as np, json
from PIL import Image
D = 0.367033; FPS = 30000/1001
def fr(p, t):
    b = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.4f}","-i",p,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(1080,1920,3).astype(float)
R = {}
for t in (5, 20, 40, 60, 78.5, 80.5, 84, 90, 150, 300, 450, 600, 750, 880, 900, 910, 920, 927.5):
    t4 = t if t < 78.9 else t + D
    R[f"{t}↔{t4:.3f}"] = round(float(np.abs(fr("../../05강_v3.mp4", t) - fr("../../05강_v4.mp4", t4)).mean()), 3)
print(json.dumps(R, ensure_ascii=False, indent=1)); json.dump(R, open("../../검사_v4/화면비교.json","w"), ensure_ascii=False, indent=1)
# 바뀐 카드: 프레임 2364(n21) 2365(n22) 2478(n22) 2479(n23) 2615(3장 n23) 2616(4장 n24) · -ss (n−0.3)/FPS = n번째 프레임
ims = []
for n in (2364, 2365, 2478, 2479, 2615, 2616):
    t = (n - 0.3) / FPS; ims.append(Image.fromarray(fr("../../05강_v4.mp4", t).astype(np.uint8)).resize((640, 360)))
sheet = Image.new("RGB", (1280, 1080))
for i, im in enumerate(ims): sheet.paste(im, ((i % 2) * 640, (i // 2) * 360))
sheet.save("../../검사_v4/바뀐카드.jpg", quality=85)
