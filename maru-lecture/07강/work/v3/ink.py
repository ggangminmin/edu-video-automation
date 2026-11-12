from PIL import Image, ImageDraw, ImageFont
import numpy as np, sys
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58); TR=-0.78
def ink(txt):
    im = Image.new("L", (2400, 200), 0); d = ImageDraw.Draw(im); x = 100
    for c in txt: d.text((x, 150), c, font=F, fill=255, anchor="ls"); x += F.getlength(c) + TR
    xs = np.where(np.array(im).max(0) > 0)[0]; return int(xs.max() - xs.min() + 1)
if __name__ == "__main__":
    for t in sys.argv[1:]: print(len(t), ink(t), t)
