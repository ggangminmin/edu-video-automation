# 깨끗한 음성(타임라인_v2 audio 대로 · BGM 없음) 16k + 5ms RMS dB · 단어 시각(출력 시간)
import json, re, numpy as np, subprocess
tl = json.load(open("../타임라인_v2.json")); S = tl["subs"]
SR, H = 16000, 80; FR = SR / H
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
W = [(a, w) for a, b, w in json.load(open("mlxwords.json"))]
def words_out(t0, t1):
    out = []
    for seg in tl["audio"]:
        if seg.get("src"): continue
        o0 = seg["out"]
        for a, w in W:
            if seg["src_from"] - 0.05 <= a < seg["src_to"]:
                to = o0 + max(a, seg["src_from"]) - seg["src_from"]
                if t0 <= to <= t1: out.append((round(to, 3), w.strip()))
    return sorted(out)
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
def pauses(a, b, TH=-50, GAP=6):
    i0, i1 = int(a * FR), int(b * FR); r = []; j = i0
    while j < i1:
        if db[j] < TH:
            k = j
            while k < i1 and db[k] < TH: k += 1
            if k - j >= GAP:
                m = k
                while m < len(db) - 6 and not all(db[m:m + 6] > TH): m += 1
                r.append((round(j / FR, 3), round(m / FR, 3), k - j))
            j = k
        else: j += 1
    return r
