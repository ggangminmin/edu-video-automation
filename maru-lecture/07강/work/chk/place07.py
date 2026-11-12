# 오더16/규칙20: 표지 인삿말·마지막 장 끝인사 아나운서 ↔ 슬라이드 사진·글자 겹침 측정 → 겹치면 빈 공간 가운데로 x 이동(크기·y 그대로)
#  사진·글자 = 강 슬라이드 전체 픽셀 상위 90%(배경) 과 RGB 최대차 > 28 (열림 3px · 넓힘 6px) · 자막바(y≥900) 아래는 제외(바가 위에 덮임)
#  아나운서 = warp 클립 프레임(0.25초마다) 그린 아닌 화소 합집합 → 렌더와 같은 배율로 줄여 overlay 위치에 놓음
import sys, json, glob, subprocess, numpy as np
from PIL import Image, ImageFilter
N = 7; D = "07강"; tl = json.load(open(f"{D}/타임라인_v1b초안.json"))   # 07강 사본(오더24 place16.py)
L = tl["slides"][-1]["slide"]
P = {"인삿말": dict(slide=1, x=934, y=40, w=788, h=1402), "끝인사": dict(slide=L, x=952, y=36, w=799, h=1421)}
sl = sorted(glob.glob(f"{D}/slides/s-*.png"))
bg = np.percentile(np.stack([np.asarray(Image.open(p).convert("RGB").resize((480, 270)), np.int16) for p in sl]), 90, axis=0)   # 종이·나무 배경(글자·사진은 더 어두움 · 중앙값은 다른 장 제목 글자가 남아 가짜 영역 생김)
bgF = np.asarray(Image.fromarray(bg.astype(np.uint8)).resize((1920, 1080), Image.BILINEAR), np.int16)
def content(n):
    im = np.asarray(Image.open(f"{D}/slides/s-{n:02d}.png").convert("RGB"), np.int16)
    m = (np.abs(im - bgF).max(2) > 28).astype(np.uint8) * 255
    m = Image.fromarray(m).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MaxFilter(13))
    m = np.asarray(m) > 0; m[900:] = False; return m
def alpha(clip, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps=4,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.int16)
    g = (f[..., 1] > f[..., 0] + 40) & (f[..., 1] > f[..., 2] + 40)
    return ~g                                            # 프레임별 인물 영역
out = {}
for k, p in P.items():
    a = [x for x in tl["anchors"] if x["name"] == k][0]
    A = alpha(f"{D}/아나운서/07_{k}_090.mp4", p["w"], p["h"]); U = A.any(0)   # warp 전 클립(같은 프레임들)
    C = content(p["slide"])
    def overlap(x):
        cv = np.zeros((1080, 1920), bool); y0 = p["y"]
        xs, xe = max(0, x), min(1920, x + p["w"]); hh = min(1080 - y0, p["h"])
        cv[y0:y0 + hh, xs:xe] = U[:hh, xs - x:xe - x]; return int((cv & C).sum()), cv
    ov0, _ = overlap(p["x"])
    cols = np.where(U[:1080 - p["y"]].any(0))[0]; bx0, bx1 = int(cols.min()), int(cols.max())   # 몸 좌우(캔버스 기준, 손 포함)
    res = dict(slide=p["slide"], x_now=p["x"], overlap_now=ov0, body_canvas=[bx0, bx1], body_w=bx1 - bx0 + 1)
    if ov0 > 0:
        rows = C[p["y"]:900].any(0)                       # 몸 높이 구간에서 사진·글자 있는 열
        free = ~rows; runs = []; s = None
        for i, v in enumerate(list(free) + [False]):
            if v and s is None: s = i
            if not v and s is not None: runs.append((s, i - 1)); s = None
        runs = [r for r in runs if r[1] < 1500]           # 오른쪽 나무 무늬 띠 밖(빈 공간 = 제목과 사진 사이)
        r = max(runs, key=lambda r: r[1] - r[0]); cx = (r[0] + r[1]) / 2
        x_new = int(round(cx - (bx0 + bx1) / 2)); ov1, _ = overlap(x_new)
        res.update(free_run=list(r), free_w=r[1] - r[0] + 1, x_new=x_new, overlap_new=ov1,
                   margin=[int(x_new + bx0 - r[0]), int(r[1] - (x_new + bx1))], fits=bool(r[1] - r[0] + 1 >= bx1 - bx0 + 1 + 40))
    out[k] = res
json.dump(out, open(f"{D}/work/chk/배치07.json", "w"), ensure_ascii=False, indent=1); print(N, json.dumps(out, ensure_ascii=False))
