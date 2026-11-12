# 전편 흑/백 튐 검사: 모든 프레임 32x18 회색 평균 → 앞뒤와 크게 다른 1~2프레임 튐(밝기 차 ≥40, 앞·뒤 프레임끼리는 비슷) · 전부 검정(≤3)/흰(≥250) 프레임이 엔딩 검정 밖에 있나
# 실행(_작업): heavy_run.sh render python3 오더24/flash_check.py NN강/NN강_v3c.mp4 NN강/타임라인_v3c.json  (전편 디코딩이라 칸 안)
import sys, json, subprocess, numpy as np
mp4, tlp = sys.argv[1], sys.argv[2]; tl = json.load(open(tlp)); FPS = 30000 / 1001
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "scale=32:18,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 18 * 32).astype(np.float32); m = f.mean(1)
b0, b1 = tl["ending"]["black"]
spikes = []
for k in (1, 2):
    for i in range(1, len(m) - k):
        a, c = m[i - 1], m[i + k]
        mid = m[i:i + k]
        if abs(a - c) < 15 and np.all(np.abs(mid - (a + c) / 2) >= 40): spikes.append((i, round(i / FPS, 3), k, round(float(a), 1), [round(float(x), 1) for x in mid]))
blk = [i for i in range(len(m)) if (m[i] <= 3 or m[i] >= 250) and not (b0 - 0.05 <= i / FPS <= b1 + 0.1)]
ok = not spikes and not blk
res = dict(mp4=mp4, frames=len(m), spikes=spikes[:50], black_white_outside_ending=[(i, round(i / FPS, 3), round(float(m[i]), 1)) for i in blk[:50]], verdict="통과" if ok else "걸림")
out = mp4.rsplit("/", 1)[0] + "/검사_v3c/흑백튐.json"; json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
print(f"흑백튐 {res['verdict']} · 프레임 {len(m)} · 튐 {len(spikes)} · 엔딩 밖 검정/흰 {len(blk)} → {out}")
sys.exit(0 if ok else 1)
