# 12강 v2 인삿말 「그리고」 자리(출력 11.9~12.9초) 입 확대 컷: 프레임마다 얼굴 확대 + 그 프레임 소리 크기(타입캐스트) → 컨택트시트
# 클립 「그리고」 입 = 출력 12.23~12.48 (warp 지도) · 타입캐스트엔 「그리고」 없음, 「완료」 12.29~
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont
V = "12강/12강_v2.mp4"; OUT = "12강/검사_v2/그리고_확대.jpg"
X, Y, S = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])     # 얼굴 크롭 좌상단·한 변
t0, t1, fps = 11.9, 12.9, 30000 / 1001
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", V, "-t", str(t1 - t0), "-vf", f"crop={S}:{S}:{X}:{Y},scale=240:240",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = [Image.frombytes("RGB", (240, 240), raw[i:i + 240 * 240 * 3]) for i in range(0, len(raw) - 240 * 240 * 3 + 1, 240 * 240 * 3)]
au = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-i", V, "-t", str(t1 - t0), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                  capture_output=True).stdout, np.int16) / 32768
F = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 18)
cols = 6; rows = (len(fr) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 244, rows * 284), "white"); d = ImageDraw.Draw(sheet)
for k, im in enumerate(fr):
    t = t0 + k / fps; x, y = (k % cols) * 244, (k // cols) * 284
    sheet.paste(im, (x + 2, y + 2))
    s = au[int((t - t0) * 16000):int((t - t0 + 1 / fps) * 16000)]
    db = 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-7) if len(s) else -99
    mark = " 그리고(클립)" if 12.23 <= t < 12.48 else (" 완료" if 12.29 <= t < 12.83 else "")
    d.text((x + 6, y + 246), f"{t:.3f}s {db:5.0f}dB{mark}", fill="black", font=F)
sheet.save(OUT, quality=88); print(OUT, len(fr), "프레임")
