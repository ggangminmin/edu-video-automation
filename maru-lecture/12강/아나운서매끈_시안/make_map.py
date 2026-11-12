# 시안 지도 만들기(v4 warp2 지도 = DTW+앵커 결과를 출발점)
#  가 = Whittaker 평활(2차 차분 벌점 λ) + 국소 lag 보정 반복 → 속도 0.75~1.35 · 프레임당 속도 변화 ≤0.03
#  다 = 쉼 구간에서만 속도를 바꾸는 「구절별 일정 속도」(구절 안은 일정, 바뀜은 쉼 안 0.3초 ease)
import sys, json, numpy as np
from scipy.sparse import diags, csc_matrix
from scipy.sparse.linalg import spsolve
from sync_eval import evaluate
src, mode, out = sys.argv[1:4]
d = json.load(open(src)); m = np.array(d["map"]); tau, cl = m[:, 0].copy(), m[:, 1].copy()
n = len(tau); dt = tau[1] - tau[0]
def whit(y, w, lam):
    D = diags([1, -2, 1], [0, 1, 2], shape=(n - 2, n)); W = diags(w)
    return spsolve(csc_matrix(W + lam * D.T @ D), w * y)
def clamp(z, lo, hi, dmax):
    s = np.diff(z) / dt
    for _ in range(200):     # 속도 범위 + 변화율 한도(앞뒤로 번갈아)
        s = np.clip(s, lo, hi)
        for i in range(1, len(s)): s[i] = np.clip(s[i], s[i-1] - dmax, s[i-1] + dmax)
        for i in range(len(s) - 2, -1, -1): s[i] = np.clip(s[i], s[i+1] - dmax, s[i+1] + dmax)
    z2 = np.concatenate([[z[0]], z[0] + np.cumsum(s) * dt]); return z2 * (cl[-1] - cl[0]) / (z2[-1] - z2[0]) + (cl[0] - z2[0] * (cl[-1] - cl[0]) / (z2[-1] - z2[0]))
LAM = float(sys.argv[4]) if len(sys.argv) > 4 else 3e5
if mode == "ga":
    w = np.ones(n); w[0] = w[-1] = 1e6
    z = whit(cl, w, LAM)
    DMAX = 0.03 * (100 / 29.97)          # 프레임당 0.03 → 10ms 칸당
    z = clamp(z, 0.75, 1.35, DMAX)
elif mode == "tube":
    import librosa
    yt = librosa.load("../work/bye_tc_090.wav", sr=16000)[0]; ts = d["target_speech"][0]
    fr = librosa.util.frame(np.pad(yt, (0, 160)), frame_length=160, hop_length=160); db = 20 * np.log10(np.sqrt((fr**2).mean(0)) + 1e-7)
    voiced = db[int(ts * 100): int(ts * 100) + n] > -40
    vv = np.convolve(voiced.astype(float), np.ones(11), "same") > 0          # 소리 ±50ms
    TOL = float(sys.argv[5]) if len(sys.argv) > 5 else 0.06
    tol = np.where(vv, TOL, 0.30)
    w = np.ones(n); w[0] = w[-1] = 1e6; y = cl.copy()
    for it in range(60):
        z = whit(y, w, LAM)
        y = y + (np.clip(z, cl - tol, cl + tol) - z)                     # 관 밖으로 나간 만큼 목표를 밀어 넣음
    z = np.clip(z, cl - tol, cl + tol)
    z = whit(z, w, LAM / 50)
elif mode == "da":
    import librosa
    yt = librosa.load("../work/bye_tc_090.wav", sr=16000)[0]; ts = d["target_speech"][0]
    fr = librosa.util.frame(np.pad(yt, (0, 160)), frame_length=160, hop_length=160); db = 20 * np.log10(np.sqrt((fr**2).mean(0)) + 1e-7)
    quiet = db[int(ts * 100): int(ts * 100) + n] < -40
    # 쉼(0.15초↑) 가운데를 경계로 구절 나눔 → 구절 경계에서 v4 지도 값 고정, 구절 안 선형
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if j - i >= 15 and i > 0 and j < n: runs.append((i, j))
            i = j
        else: i += 1
    knots = [0] + [ (a + b) // 2 for a, b in runs] + [n - 1]
    z = np.interp(np.arange(n), knots, cl[knots])
    # 꺾임은 쉼 안에서 부드럽게(쉼 길이만큼 가우시안 평활 · 말 구간엔 영향 작게)
    s = np.diff(z) / dt; sig = np.full(len(s), 1.0)
    for a, b in runs: sig[a:b] = max(1.0, (b - a) / 4)
    s2 = np.array([np.average(s[max(0, k - int(3*sig[k])):k + int(3*sig[k]) + 1], weights=np.exp(-0.5*((np.arange(max(0, k - int(3*sig[k])), min(len(s), k + int(3*sig[k]) + 1)) - k)/sig[k])**2)) for k in range(len(s))])
    z = np.concatenate([[z[0]], z[0] + np.cumsum(s2) * dt]); z = (z - z[0]) * (cl[-1] - cl[0]) / (z[-1] - z[0]) + cl[0]
    print("구절", len(knots) - 1, "쉼", [(round(a*dt,2), round(b*dt,2)) for a, b in runs])
for i in range(1, n): z[i] = max(z[i], z[i-1] + 1e-4)
d2 = dict(d); d2["map"] = [[round(float(a), 3), round(float(b), 3)] for a, b in zip(tau, z)]; d2["note"] = f"아나운서매끈 {mode} λ={LAM}"
s = np.diff(z) / dt; d2["speed_min"], d2["speed_max"] = round(float(s.min()), 2), round(float(s.max()), 2)
json.dump(d2, open(out, "w"), ensure_ascii=False, indent=1)
r = evaluate(d2); r.pop("lags"); print(mode, "속도", d2["speed_min"], d2["speed_max"], r)
