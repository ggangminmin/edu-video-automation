# 오더34: newline_onset_check 걸림 줄 — 검사기 쉼 끝 vs 손 실측 두 시각에서 [t−0.03, +1.3] · [t−0.9, t−0.03] 받아쓰기 대조
# 실행(cwd=NN강/work): heavy_run.sh asr python asr_two.py <t1> <t2> ...
import json, sys, numpy as np, subprocess, mlx_whisper
def _load(f): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
tl = json.load(open("../타임라인_v4b.json")); SR = 16000; src = {None: _load("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in src: src[k] = _load(k.replace("work/", ""))
    y = src[k][int(s["src_from"] * SR):int(s["src_to"] * SR)]; o = int(s["out"] * SR); V[o:o + len(y)] += y
for t in map(float, sys.argv[1:]):
    a = mlx_whisper.transcribe(V[int((t - 0.03) * SR):int((t + 1.3) * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
    b = mlx_whisper.transcribe(V[int((t - 0.9) * SR):int((t - 0.03) * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
    print(t, "뒤:", a, "| 앞:", b, flush=True)
