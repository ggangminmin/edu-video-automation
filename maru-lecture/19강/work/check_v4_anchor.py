# 오더34: v4 끝인사 정지(정지 뒤 얼굴 움직임 0 · 정지 앞 = 앞판 같음) · 등장 알파(0 · 0.25 · 0.5초) 실측 + 그림
# 실행(cwd=_작업): python3 19강/work/check_v4_anchor.py NN 앞판
import json, sys, subprocess as sp, numpy as np
from PIL import Image, ImageDraw
n, prev = sys.argv[1], sys.argv[2]
tl = json.load(open(f"{n}강/타임라인_v4b.json")); A = {a["name"]: a for a in tl["anchors"]}
FPS = 30000 / 1001; q = lambda t: round(t * FPS) / FPS
def frame(mp4, t, crop=None):
    vf = [f"select=eq(n\\,{int(round(t * FPS))})"] + ([f"crop={crop}"] if crop else [])
    r = sp.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", ",".join(vf), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    w, h = (1920, 1080) if not crop else map(int, crop.split(":")[:2]); return np.frombuffer(r, np.uint8).reshape(h, w, 3).astype(int)
new = f"{n}강/{n}강_v4b.mp4"; old = f"{n}강/{n}강_{prev}.mp4"
e = A["끝인사"]; fr = tl["ending"]["bye_freeze"]; x = e["x"]
face = f"300:260:{x + 200}:{e['y'] + 60}"           # 끝인사 얼굴(700 폭 캔버스 · 1421 높이 기준 얼굴 위쪽)
out = {}
pts = [fr - 0.35, fr - 0.2, fr - 0.05, fr + 0.1, fr + 0.3, e["out"] - 0.6, e["out"] - 0.52]
F = [frame(new, t, face) for t in pts]
out["정지 뒤 얼굴 프레임차"] = [round(float(np.abs(F[i] - F[3]).mean()), 2) for i in (4, 5, 6)]
out["정지 앞 v4-앞판 얼굴차"] = [round(float(np.abs(frame(new, t, face) - frame(old, t, face)).mean()), 2) for t in pts[:2]]
# 등장 알파: 아나운서 몸 영역 평균을 슬라이드만(v4 첫 프레임 직전 장 없음 → 앞판에서 아나운서 없는 같은 장 프레임 대신 v4 컷+0 프레임을 0 으로) 기준
def alpha(t0, an):
    body = f"200:500:{an['x'] + 250}:{an['y'] + 300}"
    s = [frame(new, q(t0) + k / FPS, body) for k in (0, 8, 15, 30)]
    full = s[3]; base = s[0]; d = np.abs(full - base).mean() + 1e-6
    return [round(float(np.abs(v - base).mean() / d), 2) for v in s]
cl_in = next(s for s in tl["slides"] if s["slide"] == max(x["slide"] for x in tl["slides"]))["start"]
out["등장 알파 오프닝(0·0.27·0.5·1.0초 · 0프레임 기준)"] = alpha(0.0, A["인삿말"])
out["등장 알파 클로징(cut 기준 같은 식)"] = alpha(cl_in, e)
print(json.dumps(out, ensure_ascii=False))
sheet = Image.new("RGB", (300 * len(pts), 290), "white"); d = ImageDraw.Draw(sheet)
for i, (t, f) in enumerate(zip(pts, F)):
    sheet.paste(Image.fromarray(f.astype(np.uint8)), (300 * i, 30)); d.text((300 * i + 4, 6), f"{t:.3f}" + (" 정지" if t > fr else ""), fill="red" if t > fr else "black")
sheet.save(f"{n}강/검사_v4b/끝인사_정지.jpg")
