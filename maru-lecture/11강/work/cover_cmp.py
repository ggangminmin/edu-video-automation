# #9 앞판(v3)·새판(v4) 표지 같은 시각 나란히 + 이번 판 겹침 수치
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]; T = [1.0, 7.0, 13.4]
F = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 22)
sheet = Image.new("RGB", (2 * 800 + 30, len(T) * (450 + 40) + 10), (245, 245, 247)); d = ImageDraw.Draw(sheet)
for i, t in enumerate(T):
    for j, v in enumerate(["v3", "v4"]):
        p = f"/tmp/_c_{v}_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", f"../11강_{v}.mp4", "-frames:v", "1", "-vf", "scale=800:450", p], check=True)
        x, y = 10 + j * 810, 10 + i * 490
        sheet.paste(Image.open(p), (x, y + 32)); d.text((x, y), f"{'앞판 v3' if j == 0 else '새판 v4'} · {int(t//60)}:{t%60:04.1f}", font=F, fill=(29, 29, 31))
sheet.save(out, quality=88); print(out)
