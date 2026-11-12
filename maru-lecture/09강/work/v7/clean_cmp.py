import json, subprocess, numpy as np, re, sys
SR = 48000; D = "09강"
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {}
def clean(v):
    tl = json.load(open(f"{D}/타임라인_{v}.json")); T = tl["total"]; out = np.zeros(int((T + 1) * SR), np.float32)
    for a in tl["audio"]:
        p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
        if p not in cache: cache[p] = load(p)
        seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
        i0 = int(round(a["out"] * 1000)) * SR // 1000; out[i0:i0 + len(seg)] += seg[:len(out) - i0]
    return out[:int(T * SR)], tl
a, ta = clean("v6b"); b, tb = clean("v7")
np.save(f"{D}/work/v7/clean_v7.npy", b)
Dl = -22 * 1001 / 30000; k = int(round(Dl * SR))
def corr(x, y): return float(np.dot(x, y) / np.sqrt(np.dot(x, x) * np.dot(y, y)))
pre = int(27.40 * SR); print("앞(0~27.40) 상관", round(corr(a[:pre], b[:pre]), 6), "maxdiff", float(np.abs(a[:pre] - b[:pre]).max()))
s = int(31.70 * SR); x = a[s:]; y = b[s + k:s + k + len(x)]; n = min(len(x), len(y)); print("뒤(v6b 31.70~) Δ이동 상관", round(corr(x[:n], y[:n]), 6), "maxdiff", float(np.abs(x[:n] - y[:n]).max()))
# 5ms RMS around joins & gaps
def env(z, t0, t1, h=0.005):
    return [(round(t, 3), round(20 * np.log10(np.sqrt((z[int(t * SR):int((t + h) * SR)] ** 2).mean()) + 1e-9), 0)) for t in np.arange(t0, t1, h)]
print("이음매1 27.43~27.53", env(b, 27.43, 27.53))
print("이음매2 30.92~31.06", env(b, 30.92, 31.06))
# sample-step at joins (click): max |diff| in ±2ms window vs. neighbors
for t in (27.449833, 30.969833):
    i = int(round(t * SR)); w = b[i - 96:i + 96]; print("join", t, "max|Δsample|", float(np.abs(np.diff(w)).max()), "max|x|", float(np.abs(w).max()))
def sils(x, n=-40, d=0.04):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"silencedetect=n={n}dB:d={d}", "-f", "null", "-"], input=x.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
for nm, z, r in (("v6b", a, (24, 36)), ("v7", b, (24, 35.3))):
    seg = z[int(r[0] * SR):int(r[1] * SR)]; print(nm, "무음(-40,0.04)", [(round(u + r[0], 3), round(w + r[0], 3), round(w - u, 3)) for u, w in sils(seg)])
