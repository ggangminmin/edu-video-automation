# 한 장 후보 잉크 폭(render05 sub_png 와 같은 글꼴·자간)
import sys
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
FJ = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 58); TR = -0.78
def _has(c):
    if c.isspace(): return True
    m = Image.new("L", (90, 90)); ImageDraw.Draw(m).text((10, 75), c, font=F, fill=255, anchor="ls"); return m.getbbox() is not None
def FF(c): return F if _has(c) else FJ
def ink(txt):
    im = Image.new("L", (2600, 200)); d = ImageDraw.Draw(im); x = 20
    for c in txt: d.text((x, 150), c, font=FF(c), fill=255, anchor="ls"); x += FF(c).getlength(c) + TR
    b = im.getbbox(); return b[2] - b[0]
if __name__ == "__main__":
    for t in sys.argv[1:]: print(ink(t), len(t), t)
