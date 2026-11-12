# 줄 시작 손 실측: 타임라인 깨끗한 음성에서 n번 줄 기준점 ±0.5 의 골짜기 후보마다 [t−1.0,t] / [t,t+1.2] 받아쓰기
# 실행: ~/.venvs/tts/bin/python scan10.py <타임라인> n [n ...]
import sys, json, re, subprocess, numpy as np, mlx_whisper
tl = json.load(open(sys.argv[1])); SR = 16000
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
H = 80; db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
def tr(a, b): return mlx_whisper.transcribe(V[int(a * SR):int(b * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
S = {s["n"]: s for s in tl["subs"]}
for n in map(int, sys.argv[2:]):
    s = S[n]; ref = s.get("voice_on") or s["start"] + 0.09; prev = S.get(n - 1)
    print(f"\n## {n} 「{s['text'][:20]}」 앞줄 「{prev['text'][-12:] if prev else ''}」 ref {ref:.3f}")
    i0, i1 = int((ref - 0.6) * 200), int((ref + 0.5) * 200)
    print(" ".join(f"{i/200:.2f}:{db[i]:.0f}" for i in range(i0, i1, 2)))
    mins = [i for i in range(i0 + 3, i1 - 3) if db[i] == db[i - 3:i + 4].min() and db[i] < -25]
    for i in mins:
        t = i / 200; print(f"  t={t:.3f} {db[i]:.0f}dB | 앞 「{tr(t - 1.0, t)}」 | 뒤 「{tr(t, t + 1.2)}」", flush=True)
