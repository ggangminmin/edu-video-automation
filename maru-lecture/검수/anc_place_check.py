#!/usr/bin/env python3
"""오더 18 — 아나운서 배치 점검 자료 만들기 (판정은 cx 가 함)
사용(_작업 에서): 검수/heavy_run.sh render python3 검수/anc_place_check.py NN
- 표지 인삿말 · 마지막 장 끝인사 각각: 클립 전 프레임을 렌더와 같은 키잉·크기로 알파 → 합집합으로
  ① 슬라이드 글자·사진(배경과 18 넘게 다른 픽셀, 자막바 y≥905 제외)과 겹침 픽셀 · 최소 거리
  ② 빈 열(y150~850) 안 가운데 어긋남 ③ 크기 ④ 발·다리가 자막바 위에서 끊기는지 ⑤ 초록 윤곽·오른쪽 끝 잔상
  ⑥ 등장 첫 15프레임 정지 ⑦ 로고(x1553 y71 274×58) 겹침
- 정지 컷 4장(처음·손 최대·중간·끝): 12~15 = 실제 mp4 프레임 + 합성, 16~20 = 합성만.
- 12~15: 등장 프레임 앞뒤 ±2 를 mp4 에서 뽑아 「앞 장 위에 먼저 나옴」 확인.
결과: _작업/검수/anc/NN_{greet,bye}.jpg · NN.json
"""
import sys, os, json, subprocess, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, binary_erosion, binary_dilation

L = int(sys.argv[1]); W = os.getcwd()   # _작업
OUT = os.path.join(W, '검수', 'anc'); os.makedirs(OUT, exist_ok=True)
tlp = f'{L}강/타임라인_v2.json' if L <= 15 else f'{L}강/타임라인_초안.json'
tl = json.load(open(tlp)); A = {a['name']: a for a in tl['anchors']}
last = max(s['slide'] for s in tl['slides'])
MP4 = f'{L}강/{L}강_v2.mp4' if L <= 15 else None
if MP4 and subprocess.run(['ffprobe', '-v', 'error', MP4], capture_output=True).returncode != 0:
    print(f'{MP4} 아직 못 엶(렌더 중) → 합성만'); MP4 = None
FPS = 30000 / 1001
SIZE = {'인삿말': (788, 1402), '끝인사': (799, 1421)}
KEY = ("chromakey=0x01FA04:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[c][m];"
       "[m]alphaextract,erosion,erosion,gblur=sigma=1.2[a];[c][a]alphamerge")
LOGO = (1553, 71, 1553 + 274, 71 + 58)
BARTOP = 905

def clip_path(c):
    for base in (f'{L}강/work', W, os.path.dirname(W)):
        p = os.path.normpath(os.path.join(base, c))
        if os.path.exists(p): return p
    raise FileNotFoundError(c)

def frame_at(t):
    r = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-ss', f'{t:.4f}', '-i', MP4, '-frames:v', '1',
                        '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.uint8).reshape(1080, 1920, 3)

res = {'강': L, '타임라인': tlp}
for name, sl in (('인삿말', 1), ('끝인사', last)):
    a = A[name]; cw, ch = SIZE[name]; x0, y0 = a.get('x', 934 if name == '인삿말' else 952), a.get('y', 40 if name == '인삿말' else 36)
    cp = clip_path(a['clip'])
    cmd = ['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', cp, '-filter_complex',
           f'[0:v]fps=30000/1001,{KEY},scale={cw}:{ch},format=rgba[o]', '-map', '[o]', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = cw * ch * 4; cnt = np.zeros((ch, cw), np.uint16); frames = 0; widest = (-1, None, 0)
    keep = {}; first15 = []; edgecol = 0; prev = None; keyfail = []
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        f = np.frombuffer(b, np.uint8).reshape(ch, cw, 4); al = f[..., 3] > 128
        cnt += al
        cols = np.where(al[:, :cw - 3].any(0))[0]
        wdt = int(cols.max() - cols.min()) if len(cols) else 0
        if wdt > widest[0]: widest = (wdt, f.copy(), frames)
        if al[:, cw - 2:].any(): edgecol += 1
        if al.mean() > 0.6: keyfail.append(frames)
        if frames == 0: keep['처음'] = (f.copy(), 0)
        if frames < 15:
            if prev is not None: first15.append(float(np.abs(f[..., :3].astype(int) - prev[..., :3].astype(int))[al].mean() if al.any() else 0))
            prev = f.copy()
        lastf = f; frames += 1
    p.wait()
    keep['끝'] = (lastf.copy(), frames - 1); keep['손 최대'] = (widest[1], widest[2])
    # 중간 프레임 = 한 번 더 짧게
    mid = frames // 2
    r = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', cp, '-filter_complex',
                        f'[0:v]fps=30000/1001,{KEY},scale={cw}:{ch},format=rgba,select=eq(n\\,{mid})[o]', '-map', '[o]',
                        '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'], capture_output=True, check=True).stdout
    keep['중간'] = (np.frombuffer(r, np.uint8).reshape(ch, cw, 4).copy(), mid)

    S = np.asarray(Image.open(f'{L}강/slides/s-{sl:02d}.png').convert('RGB')).astype(int)
    bg = np.median(S[150:850, 600:1000].reshape(-1, 3), 0)
    C = np.abs(S - bg).max(2) > 18; C[BARTOP:] = False
    U = np.zeros((1080, 1920), bool)
    vis = cnt >= 1
    ys, xs = np.where(vis)
    yy, xx = ys + y0, xs + x0; ok = (yy < 1080) & (xx < 1920); U[yy[ok], xx[ok]] = True
    Dt = distance_transform_edt(~C)
    U7 = np.zeros((1080, 1920), bool); v7 = vis.copy(); v7[:, 700:] = False
    ys7, xs7 = np.where(v7); yy7, xx7 = ys7 + y0, xs7 + x0; ok7 = (yy7 < 1080) & (xx7 < 1920); U7[yy7[ok7], xx7[ok7]] = True
    bx7 = np.where(U7[:BARTOP].any(0))[0]
    crop7 = dict(겹침픽셀=int((U7 & C).sum()), 최소거리=float(Dt[U7].min()), 몸x=(int(bx7.min()), int(bx7.max())), 로고겹침=int(U7[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]].sum()))
    over = int((U & C).sum()); mind = float(Dt[U].min()) if U.any() else None
    bx = np.where(U[:BARTOP].any(0))[0]; body = (int(bx.min()), int(bx.max())) if len(bx) else None
    # 빈 열: y150~850 에 글자·사진 없는 열의 연속 구간 중 몸 가운데를 품은 것
    emptycol = ~C[150:850].any(0); bc = (body[0] + body[1]) // 2
    l = bc
    while l > 0 and emptycol[l - 1]: l -= 1
    r_ = bc
    while r_ < 1919 and emptycol[r_ + 1]: r_ += 1
    gap = (l, r_) if emptycol[bc] else None
    off = (bc - (l + r_) // 2) if gap else None
    logo = int(U[LOGO[1]:LOGO[3], LOGO[0]:LOGO[2]].sum())
    bottom = int(np.where(U.any(1))[0].max())
    # 초록 윤곽: 스틸 4장, 알파 경계 바깥 2px 띠에서 G ≥ max(R,B)+3 인 픽셀 수(합성 결과 기준)
    def comp(f):
        im = Image.fromarray(S.astype(np.uint8)).convert('RGBA'); im.alpha_composite(Image.fromarray(f), (x0, y0)); return np.asarray(im.convert('RGB'))
    green = {}
    stills = []
    for k in ('처음', '손 최대', '중간', '끝'):
        f, idx = keep[k]; c = comp(f)
        al = np.zeros((1080, 1920), bool); fa = f[..., 3] > 20
        hh, ww = min(ch, 1080 - y0), min(cw, 1920 - x0); al[y0:y0 + hh, x0:x0 + ww] = fa[:hh, :ww]
        ring = binary_dilation(al, iterations=1) & ~binary_erosion(al, iterations=1); ring[BARTOP:] = False
        ci = c.astype(int); g = ring & (ci[..., 1] >= np.maximum(ci[..., 0], ci[..., 2]) + 3) & (ci[..., 1] > 60)
        green[k] = int(g.sum())
        t = (a.get('clip_t0', 0) + idx / FPS)
        real = frame_at(t + 0.5 / FPS) if MP4 else None
        stills.append((k, idx, t, c, real))
    # 정지(첫 15프레임 사이 평균 차가 0.3 미만이 3번 넘게 연속)
    still_run = max((len(s) for s in ''.join('0' if d < 0.3 else '1' for d in first15).split('1')), default=0)
    item = dict(장=sl, x=x0, y=y0, 크기=[cw, ch], 프레임=frames, 겹침픽셀=over, 최소거리=mind, 몸x=body, 빈공간=gap,
                가운데어긋남=off, 로고겹침=logo, 몸아래끝y=bottom, 자막바뒤로이어짐=bottom >= BARTOP + 20,
                오른쪽끝잔상프레임=edgecol, crop700기준=crop7, 키잉실패프레임=keyfail[:20], 키잉실패수=len(keyfail), 초록윤곽=green, 첫15정지연속=still_run, 손최대프레임=widest[2])
    # 12~15: 등장 ±2 프레임(실제 mp4)
    edge = []
    if MP4:
        tin = a['in'] if name == '끝인사' else 0.0
        fi = round(tin * FPS)
        prevslide = np.asarray(Image.open(f'{L}강/slides/s-{max(1, sl - 1):02d}.png').convert('RGB')).astype(int)
        for d in range(-2, 3):
            if fi + d < 0: continue
            fr = frame_at((fi + d + 0.5) / FPS).astype(int)
            reg = (slice(y0, min(1080, y0 + ch)), slice(x0, min(1920, x0 + cw)))
            dprev = float(np.abs(fr - prevslide)[150:850, 300:1500].mean()); dcur = float(np.abs(fr - S)[150:850, 300:1500].mean())
            sub = fr[reg]; gr = int(((sub[..., 1] > sub[..., 0] + 40)).sum())
            # 아나운서 있음 = 슬라이드 그림과 그 자리 차이가 큼
            dn = float(np.abs(fr - (S if dcur < dprev else prevslide))[reg][:BARTOP - y0].mean())
            edge.append(dict(프레임=fi + d, 초=round((fi + d) / FPS, 4), 장=sl if dcur < dprev else sl - 1, 아나운서자리차=round(dn, 1)))
            Image.fromarray(fr.astype(np.uint8)).resize((640, 360)).save(os.path.join(OUT, f'{L}_{name}_edge{d:+d}.jpg'), quality=80)
        item['등장±2'] = edge
    res[name] = item
    # 시트: 4 스틸(합성 | 실제)
    tw, th = 640, 360; rows = len(stills); cols = 2 if MP4 else 1
    sheet = Image.new('RGB', (tw * cols + 10 * (cols - 1), (th + 30) * rows), 'white'); dr = ImageDraw.Draw(sheet)
    for i, (k, idx, t, c, real) in enumerate(stills):
        im = Image.fromarray(c); d2 = ImageDraw.Draw(im)
        d2.rectangle([body[0], 150, body[1], BARTOP], outline=(255, 0, 0), width=3)
        if gap: d2.rectangle([gap[0], 150, gap[1], 850], outline=(0, 160, 255), width=3)
        sheet.paste(im.resize((tw, th)), (0, i * (th + 30) + 30))
        if real is not None: sheet.paste(Image.fromarray(real).resize((tw, th)), (tw + 10, i * (th + 30) + 30))
        dr.text((6, i * (th + 30) + 8), f'{L}강 {name} · {k} · 클립 {idx}f · 영상 {t:.2f}s  (왼쪽=합성·빨강=몸 범위·파랑=빈 공간' + (' | 오른쪽=실제 mp4)' if MP4 else ')'), fill=(0, 0, 0))
    sheet.save(os.path.join(OUT, f'{L}_{"greet" if name == "인삿말" else "bye"}.jpg'), quality=85)
json.dump(res, open(os.path.join(OUT, f'{L}.json'), 'w'), ensure_ascii=False, indent=1, default=str)
for k in ('인삿말', '끝인사'):
    r = res[k]; print(L, k, {kk: r[kk] for kk in ('x', '겹침픽셀', '최소거리', '몸x', '빈공간', '가운데어긋남', '로고겹침', '자막바뒤로이어짐', '오른쪽끝잔상프레임', 'crop700기준', '키잉실패수', '키잉실패프레임', '첫15정지연속')}, r.get('등장±2', ''))
