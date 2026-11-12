# 아나운서 영역 프레임 차 → 튐 숫자: 정지(차≈0, 같은 그림 반복) · 튐(앞뒤 평균의 2.5배 넘는 차)
import sys, subprocess, numpy as np
f, x, y, w, h, a, b = sys.argv[1], *map(int, sys.argv[2:6]), float(sys.argv[6]), float(sys.argv[7])
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", f, "-vf", f"crop={w}:{h}:{x}:{y},scale={w//4}:{h//4},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, h // 4, w // 4).astype(np.float32)
d = np.abs(np.diff(F, axis=0)).mean((1, 2))
med = np.median(d)
still = int((d < med * 0.15).sum())
nb = (np.convolve(d, [1, 0, 1], "same") / 2)
spike = int(((d > nb * 2.5) & (d > med)).sum())
cv = float(np.std(np.diff(d)) / (med + 1e-6))
print(f"{f.split('/')[-1]:24s} 프레임 {len(F)} · 정지 {still} · 튐 {spike} · 들쭉날쭉 {cv:.2f}")
