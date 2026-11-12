# v6b ↔ v7 바뀐 구간 밖 소리 비교: 오디오 조각마다 시간 이동(ms 반올림 734/735ms 등)을 찾아 빼고 상관 · 사용: seg_corr.py <v6b wav/npy> <v7 wav/npy>
import json, sys, numpy as np, subprocess
SR = 48000; D = "09강"
def load(p):
    if p.endswith(".npy"): return np.load(p)
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
a, b = load(sys.argv[1]), load(sys.argv[2])
ta = json.load(open(f"{D}/타임라인_v6b.json")); tb = json.load(open(f"{D}/타임라인_v7.json"))
A = ta["audio"]; B = [x for x in tb["audio"] if not (x["slide"] == 2 and 27.0 < x["out"] < 31.0)]
A = [x for x in A if not (x["slide"] == 2 and abs(x["out"] - 27.0089) < 1e-6)]
assert len(A) == len(B)
worst = 1; rows = []
for x, y in zip(A, B):
    i, j = int(x["out"] * SR), int(y["out"] * SR); n = int((x["src_to"] - x["src_from"]) * SR) - 200
    u = a[i + 100:i + 100 + n]; best = (-2, 0)
    for lag in range(-60, 61):
        v = b[j + 100 + lag:j + 100 + lag + n]
        if len(v) < n: continue
        c = float(np.dot(u, v) / np.sqrt(np.dot(u, u) * np.dot(v, v) + 1e-20)); best = max(best, (c, lag))
    rows.append((x["out"], y["out"], round(best[0], 6), best[1])); worst = min(worst, best[0])
# 이동 안 하는 맨 앞(0~27.40) · 2장 둘째 조각 앞부분
pre = int(27.40 * SR); c0 = float(np.dot(a[:pre], b[:pre]) / np.sqrt(np.dot(a[:pre], a[:pre]) * np.dot(b[:pre], b[:pre])))
print("앞 0~27.40 상관", round(c0, 6), "· 조각", len(rows), "최소 상관", round(worst, 6), "· lag 분포(샘플)", sorted(set(r[3] for r in rows)))
for r in rows:
    if r[2] < 0.999: print("  낮음", r)
# 2장 셋째 조각 꼬리(v6b src 16.165~18.5875)
x = next(z for z in ta["audio"] if abs(z["out"] - 27.0089) < 1e-6); y = next(z for z in tb["audio"] if z["slide"] == 2 and abs(z["src_from"] - 16.165) < 1e-6)
i = int((x["out"] + 16.165 - 11.47) * SR); j = int(y["out"] * SR); n = int((18.5875 - 16.165) * SR) - 200
u = a[i + 100:i + 100 + n]; bc = max((float(np.dot(u, b[j + 100 + l:j + 100 + l + n]) / np.sqrt(np.dot(u, u) * np.dot(b[j + 100 + l:j + 100 + l + n], b[j + 100 + l:j + 100 + l + n]))), l) for l in range(-60, 61))
print("2장 「넘어가는…보죠」 꼬리 상관", round(bc[0], 6), "lag", bc[1])
sys.exit(0 if worst >= 0.999 and c0 >= 0.999 and bc[0] >= 0.999 else 1)
