# 타임라인 깨끗한 음성 출력 시각 구간 받아쓰기: python asr_out.py <타임라인> a:b ...
import sys, json, subprocess, numpy as np, mlx_whisper
tl = json.load(open(sys.argv[1])); SR = 16000
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
for ab in sys.argv[2:]:
    a, b = map(float, ab.split(":")); print(ab, mlx_whisper.transcribe(V[int(a * SR):int(b * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"], flush=True)
