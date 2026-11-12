# 04강: 경계 조각 훑기 걸림 자리만 긴 창(말끝 앞 2.2초 · 말 시작 뒤 2.2초) 받아쓰기 — 깨끗한 음성(타임라인 audio 표대로)
import sys, json, re, subprocess, numpy as np, mlx_whisper
tl = json.load(open(sys.argv[1])); SR = 16000; ks = [int(x) for x in sys.argv[2:]]
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
cache = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src"); f = "v090.wav" if k is None else k.replace("work/", "")
    if f not in cache: cache[f] = load(f)
    y = cache[f][int(s["src_from"]*SR):int(s["src_to"]*SR)] * float(s.get("gain",1.0)); o = int(round(s["out"]*SR)); V[o:o+len(y)] += y[:max(0,len(V)-o)]
def asr(a, b): return mlx_whisper.transcribe(V[int(a*SR):int(b*SR)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)["text"].strip()
S = {s["slide"]: s for s in tl["slides"]}
for k in ks:
    a, b = S[k], S[k + 1]
    print(f"{k}→{k+1} 끝[{a['voice_end']-2.2:.2f},{a['voice_end']+0.1:.2f}]「{asr(a['voice_end']-2.2, a['voice_end']+0.1)}」 · 첫[{b['voice_start']-0.1:.2f},{b['voice_start']+2.2:.2f}]「{asr(b['voice_start']-0.1, b['voice_start']+2.2)}」")
