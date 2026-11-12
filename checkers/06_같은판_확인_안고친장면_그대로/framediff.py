#!/usr/bin/env python3
"""두 마스터 전 프레임 화소 대조(yuv420p 전 평면). 사용: framediff.py A.mp4 B.mp4 out.json
프레임마다 최대 절대차·평균 절대차·다른 화소 수(휘도). c7-qa 10/6"""
import sys, subprocess, json, numpy as np
A, B, OUT = sys.argv[1:4]
def probe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip().split(',')
    n, d = o[2].split('/'); return int(o[0]), int(o[1]), float(n) / float(d)
# 11/12: 1920x1080 · 29.97fps 고정이던 것을 영상에서 읽는다. 두 판의 크기가 다르면 비교 자체가 안 되므로 멈춘다.
(W, H, FPS), (WB, HB, FPSB) = probe(A), probe(B)
if (W, H) != (WB, HB): sys.exit(f'ERROR 두 영상 크기가 다르다: {W}x{H} vs {WB}x{HB}')
if abs(FPS - FPSB) > 0.01: print(f'⚠️ 프레임 속도가 다르다: {FPS:.3f} vs {FPSB:.3f} — 시각은 A 기준')
N = W * H * 3 // 2
def rd(p):
    return subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-'],
                            stdout=subprocess.PIPE, bufsize=N * 4)
pa, pb = rd(A), rd(B)
rows = []; i = 0; na = nb = 0
while True:
    a = pa.stdout.read(N); b = pb.stdout.read(N)
    if len(a) < N or len(b) < N:
        na = i + (len(a) == N); nb = i + (len(b) == N)
        # 남은 프레임 수 세기
        while len(a) == N:
            a = pa.stdout.read(N); na += len(a) == N
        while len(b) == N:
            b = pb.stdout.read(N); nb += len(b) == N
        break
    if a != b:
        x = np.frombuffer(a, np.uint8).astype(np.int16); y = np.frombuffer(b, np.uint8).astype(np.int16)
        d = np.abs(x - y); yl = d[:W * H].reshape(H, W)
        ys, xs = np.nonzero(yl)
        bbox = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
        rows.append({'f': i, 't': round(i / FPS, 3), 'max': int(d.max()), 'mad': round(float(d.mean()), 4),
                     'nY': int(len(xs)), 'bbox': bbox})
    i += 1
if na == 0 or nb == 0: sys.exit(f'ERROR 프레임을 못 읽음(A {na} · B {nb}) — 검사 안 함')
json.dump({'A': A, 'B': B, 'size': [W, H], 'fps': round(FPS, 4), 'frames_A': na, 'frames_B': nb, 'diff_frames': len(rows), 'rows': rows}, open(OUT, 'w'), ensure_ascii=False)
print('frames', na, nb, 'diff', len(rows))
# 연속 구간 요약
runs = []
for r in rows:
    if runs and r['f'] == runs[-1][1] + 1: runs[-1][1] = r['f']; runs[-1][2] = max(runs[-1][2], r['max'])
    else: runs.append([r['f'], r['f'], r['max']])
for s, e, m in runs: print(f'  f{s}~f{e} ({s/FPS:.2f}~{(e+1)/FPS:.2f}s, {e-s+1}f) max {m}')
