# 오더 11 — 사진 정렬 보정본 만들기 + 검사 (원본 slides/ 는 읽기만, 결과는 NN강/slides_fix/)
# 실행: lockf -k _작업/.heavy.lock python3 _작업/검수/photo_align_fix.py   (_작업 에서)
import json, numpy as np
from PIL import Image

def ld(L, n): return np.asarray(Image.open(f'{L}강/slides/s-{n:02d}.png').convert('RGB'))
def save(L, n, arr):
    import os; os.makedirs(f'{L}강/slides_fix', exist_ok=True)
    Image.fromarray(arr).save(f'{L}강/slides_fix/s-{n:02d}.png')

def shift_of(ref, img, box, rng=16):
    """box 안에서 img 를 ref 에 맞추는 (dx,dy) — 0 이면 맞음"""
    x0, y0, x1, y1 = box
    R = ref[y0:y1, x0:x1].astype(float).mean(2)
    best = None
    for dy in range(-rng, rng + 1):
        for dx in range(-rng, rng + 1):
            I = img[y0 + dy:y1 + dy, x0 + dx:x1 + dx].astype(float).mean(2)
            e = np.abs(R - I).mean()
            if best is None or e < best[0]: best = (e, dx, dy)
    return best[1], best[2], round(best[0], 2)

report = []
# (가) 같은 카드가 첫 장과 다른 자리 → 첫 장 픽셀을 그 영역에 그대로 (배경은 두 장이 픽셀까지 같음을 확인)
PAIRS = [('11', 1, 3), ('12', 1, 9), ('13', 1, 4), ('15', 1, 3), ('17', 1, 6), ('20', 1, 11)]
for L, a, b in PAIRS:
    A, B = ld(L, a), ld(L, b)
    d = np.abs(A.astype(int) - B.astype(int)).max(2); d[:, :1000] = 0
    ys, xs = np.where(d > 2)
    x0, x1, y0, y1 = max(xs.min() - 3, 1000), min(xs.max() + 4, 1920), max(ys.min() - 3, 0), min(ys.max() + 4, 1080)
    F = B.copy(); F[y0:y1, x0:x1] = A[y0:y1, x0:x1]
    # 검사
    out = np.ones(F.shape[:2], bool); out[y0:y1, x0:x1] = False
    outside = int((np.abs(F.astype(int) - B.astype(int)).max(2)[out] > 0).sum())
    inner = (x0 + 20, y0 + 20, x1 - 20, y1 - 20)
    before = shift_of(A, B, inner); after = shift_of(A, F, inner)
    save(L, b, F)
    report.append(dict(강=L, 장=b, 기준=a, 영역=[int(x0), int(y0), int(x1), int(y1)], 크기=list(F.shape[1::-1]),
                       영역밖차이=outside, 앞판_dxdy=before[:2], 새판_dxdy=after[:2], 새판_잔차=after[2]))

# (나) 11강 7번 — 3칸 중 가운데만 넓음(259·268·259) → 세 칸 262 로 다시 나눔. 제목 띠·바깥은 그대로.
A = ld('11', 7); F = A.copy(); Y0, Y1 = 343, 812
cells = [(1036, 1295), (1300, 1568), (1573, 1832)]   # [시작, 끝+1)
gaps = [(1295, 1300), (1568, 1573)]
W, G = 262, 5
nx = [1036, 1036 + W + G, 1036 + 2 * (W + G)]          # 1036 · 1303 · 1570 → 끝 1831
for (c0, c1), n0 in zip(cells, nx):
    im = Image.fromarray(A[Y0:Y1, c0:c1]).resize((W, Y1 - Y0), Image.LANCZOS)
    F[Y0:Y1, n0:n0 + W] = np.asarray(im)
for (g0, g1), n0 in zip(gaps, [nx[0] + W, nx[1] + W]):
    F[Y0:Y1, n0:n0 + G] = A[Y0:Y1, g0:g1]
out = np.ones(F.shape[:2], bool); out[Y0:Y1, 1036:1832] = False
outside = int((np.abs(F.astype(int) - A.astype(int)).max(2)[out] > 0).sum())
def widths(M):
    r = []
    for y in (400, 500, 600, 700):
        row = M[y, 1030:1832].astype(int).mean(1); white = row > 240
        segs, s = [], None
        for i, w in enumerate(white):
            if not w and s is None: s = i
            if w and s is not None:
                if i - s > 100: segs.append(i - s)
                s = None
        if s is not None and len(white) - s > 100: segs.append(len(white) - s)
        r.append(segs)
    return r
save('11', 7, F)
report.append(dict(강='11', 장=7, 영역=[1036, Y0, 1832, Y1], 크기=list(F.shape[1::-1]), 영역밖차이=outside,
                   앞판_칸폭=widths(A)[1], 새판_칸폭=widths(F)[1]))

json.dump(report, open('검수/photo_align_fix.json', 'w'), ensure_ascii=False, indent=1)
for r in report: print(r)
