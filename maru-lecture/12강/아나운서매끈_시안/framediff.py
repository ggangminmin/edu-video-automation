# 아나운서 영역 프레임 차(연속 프레임 평균 절대차) → 튐 = 앞뒤 ±7프레임 중앙값의 2배 넘고 +0.8 넘는 값 · 멈칫 = 차 < 중앙값의 0.25
# 사용: framediff.py <mp4> <out.npy> [crop=w:h:x:y] [ss] [t]
import sys, subprocess, numpy as np, json
mp4, out = sys.argv[1:3]; crop = sys.argv[3] if len(sys.argv) > 3 else "500:900:290:60"
ss = sys.argv[4] if len(sys.argv) > 4 else None; t = sys.argv[5] if len(sys.argv) > 5 else None
w, h = [int(v) // 2 for v in crop.split(":")[:2]]
cmd = ["ffmpeg", "-v", "error"] + (["-ss", ss] if ss else []) + ["-i", mp4] + (["-t", t] if t else []) + ["-vf", f"crop={crop},scale={w}:{h},format=gray", "-f", "rawvideo", "-"]
raw = subprocess.run(cmd, capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
d = np.abs(np.diff(f, axis=0)).mean((1, 2))
med = np.array([np.median(d[max(0, i-7):i+8]) for i in range(len(d))])
spike = np.where((d > 2 * med) & (d - med > 0.8))[0]
stall = np.where((d < 0.25 * med) & (med > 0.5))[0]
np.save(out, d)
print(json.dumps(dict(frames=len(f), diff_med=round(float(np.median(d)), 3), spike_n=len(spike), spike_at=[round(i/29.97, 2) for i in spike],
                      stall_n=len(stall), jerk_std=round(float(np.std(np.diff(d))), 3)), ensure_ascii=False))
