# 줄 첫 어절 실소리 = 받아쓰기 자르기(18강 v4c 방식): [t−0.9, t] 끝 글자 · [t, t+1.3] 첫 글자 를 t 격자로 + 5ms dB
import sys, json, re, subprocess, numpy as np, mlx_whisper
tl = json.load(open(sys.argv[1])); SR = 16000
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
cache = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src"); f = "v090.wav" if k is None else k.replace("work/", "")
    if f not in cache: cache[f] = load(f)
    y = cache[f][int(s["src_from"]*SR):int(s["src_to"]*SR)] * float(s.get("gain",1.0)); o = int(round(s["out"]*SR)); V[o:o+len(y)] += y[:max(0,len(V)-o)]
def asr(a, b): return re.sub(r"\s","",mlx_whisper.transcribe(V[int(a*SR):int(b*SR)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)["text"])
H = 80; db = 20*np.log10(np.sqrt(np.mean(V[:len(V)//H*H].reshape(-1,H)**2,1))+1e-9)
for spec in sys.argv[2:]:
    a, b, st = map(float, spec.split(":"))
    print("dB", " ".join(f"{i/200:.3f}:{db[i]:.0f}" for i in range(int(a*200), int(b*200))))
    for t in np.arange(a, b + 1e-6, st): print(f"  t={t:.3f} 앞「{asr(t-0.9,t)[-8:]}」 뒤「{asr(t,t+1.3)[:8]}」")
