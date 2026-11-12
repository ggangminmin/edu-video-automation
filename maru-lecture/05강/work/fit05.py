# 05강 표지 인삿말 자리: place05 의 실제 2D 겹침(전 프레임 합집합 ∩ 사진·글자)을 x 마다 재서 겹침 0 · 최소 여백 최대 x
import sys; sys.argv = ["place05.py", "v1"]
src = open("05강/work/place05.py").read().split("out = {}")[0]; exec(src)
import numpy as np
from scipy import ndimage
p = P["인삿말"]; a = [x for x in tl["anchors"] if x["name"] == "인삿말"][0]
A = alpha(a["clip"].replace("../", f"{D}/"), p["w"], p["h"]); U = A.any(0); C = content(1)
dist = ndimage.distance_transform_edt(~C)
res = []
for x in range(300, 640):
    cv = np.zeros((1080, 1920), bool); y0 = p["y"]; xs, xe = max(0, x), min(1920, x + p["w"]); hh = min(1080 - y0, p["h"])
    cv[y0:y0 + hh, xs:xe] = U[:hh, xs - x:xe - x]
    ov = int((cv & C).sum()); m = float(dist[cv].min()) if ov == 0 else 0.0
    res.append((x, ov, round(m, 1)))
z = [r for r in res if r[1] == 0]
print("겹침0 x 범위", (z[0][0], z[-1][0]) if z else None, "최대 여백", max(z, key=lambda r: r[2]) if z else min(res, key=lambda r: r[1]))
x = 450; cv = np.zeros((1080, 1920), bool); cv[p["y"]:p["y"] + min(1080 - p["y"], p["h"]), x:x + p["w"]] = U[:min(1080 - p["y"], p["h"]), :min(p["w"], 1920 - x)]
ys, xs_ = np.where(cv & C); print("x450 겹침 화소", len(xs_), "x", xs_.min(), xs_.max(), "y", ys.min(), ys.max())
from PIL import Image
im = np.asarray(Image.open(f"{D}/slides/s-01.png").convert("RGB")).copy(); im[cv] = (im[cv] * 0.5 + np.array([0, 200, 0]) * 0.5).astype(np.uint8); im[cv & C] = (255, 0, 0)
Image.fromarray(im).resize((960, 540)).save("05강/work/fit05_x450.jpg")
# 프레임별 겹침(합집합 아닌 실제 프레임)
cnt = [int(((np.pad(f[:min(1080 - p["y"], p["h"])], ((0, 0), (0, 0)))) & C[p["y"]:p["y"] + min(1080 - p["y"], p["h"]), x:x + p["w"]]).sum()) for f in A]
print("프레임별 겹침(0.25초마다)", cnt)
im = np.asarray(Image.open(f"{D}/slides/s-01.png").convert("RGB"), np.int16)
C0 = (np.abs(im - bgF).max(2) > 28); C0[900:] = False
for x in (440, 445, 450, 455, 460):
    cv = np.zeros((1080, 1920), bool); cv[p["y"]:p["y"] + min(1080 - p["y"], p["h"]), x:x + p["w"]] = U[:min(1080 - p["y"], p["h"]), :min(p["w"], 1920 - x)]
    d0 = ndimage.distance_transform_edt(~C0); print("x", x, "넓힘 없는 겹침", int((cv & C0).sum()), "최소 거리px", round(float(d0[cv].min()), 1))
x = 450; hh = min(1080 - p["y"], p["h"])
cnt0 = [int((f[:hh, :min(p["w"], 1920 - x)] & C0[p["y"]:p["y"] + hh, x:x + p["w"]]).sum()) for f in A]
print("x450 프레임별 실제 겹침(넓힘 없음, 0.25초마다)", cnt0, "걸린 프레임", sum(c > 0 for c in cnt0), "/", len(cnt0))
