# 앞 창 + 뒤 창 받아쓰기(규칙 24 추가 · 08강 136) — 깨끗한 음성(타임라인 audio 대로)
import sys, json, subprocess, numpy as np, mlx_whisper
tl = json.load(open(sys.argv[1])); SR = 16000
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
c = {}; V = np.zeros(int((tl["total"]+1)*SR), np.float32)
for s in tl["audio"]:
    k = s.get("src"); f = "v090.wav" if k is None else k.replace("work/","")
    if f not in c: c[f] = load(f)
    y = c[f][int(s["src_from"]*SR):int(s["src_to"]*SR)]*float(s.get("gain",1.0)); o = int(round(s["out"]*SR)); V[o:o+len(y)] += y[:max(0,len(V)-o)]
for spec in sys.argv[2:]:
    a, b = map(float, spec.split(":"))
    print(f"[{a:.3f},{b:.3f}] 「{mlx_whisper.transcribe(V[int(a*SR):int(b*SR)],path_or_hf_repo='mlx-community/whisper-large-v3-turbo',language='ko',condition_on_previous_text=False)['text'].strip()}」")
