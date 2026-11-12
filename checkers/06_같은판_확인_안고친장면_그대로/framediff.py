#!/usr/bin/env python3
"""두 마스터 전 프레임 화소 대조(yuv420p 전 평면). 사용: framediff.py A.mp4 B.mp4 out.json
프레임마다 최대 절대차·평균 절대차·다른 화소 수(휘도). c7-qa 10/6"""
import sys, subprocess, json, numpy as np
A, B, OUT = sys.argv[1:4]
W, H = 1920, 1080
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
        rows.append({'f': i, 't': round(i * 1001 / 30000, 3), 'max': int(d.max()), 'mad': round(float(d.mean()), 4),
                     'nY': int(len(xs)), 'bbox': bbox})
    i += 1
json.dump({'A': A, 'B': B, 'frames_A': na, 'frames_B': nb, 'diff_frames': len(rows), 'rows': rows}, open(OUT, 'w'), ensure_ascii=False)
print('frames', na, nb, 'diff', len(rows))
# 연속 구간 요약
runs = []
for r in rows:
    if runs and r['f'] == runs[-1][1] + 1: runs[-1][1] = r['f']; runs[-1][2] = max(runs[-1][2], r['max'])
    else: runs.append([r['f'], r['f'], r['max']])
for s, e, m in runs: print(f'  f{s}~f{e} ({s*1001/30000:.2f}~{(e+1)*1001/30000:.2f}s, {e-s+1}f) max {m}')
