# 늦음/빠름 판정 줄 확인: 출력 시각 기준 깨끗한 음성에서 [자막시작-0.8, 자막시작] / [자막시작, +1.2] 받아쓰기
import json, sys, numpy as np, subprocess, re, mlx_whisper
r = json.load(open("../../검수/검사기/v3_결과.json")); tl = json.load(open("../타임라인_v3.json"))
SR = 16000
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
src = {}; voice = np.zeros(int((tl["total"]+1)*SR), np.float32)
for e in tl["audio"]:
    p = "../" + e["src"] if e.get("src") else "v090.wav"
    if p not in src: src[p] = load(p)
    s = src[p][int(e["src_from"]*SR):int(e["src_to"]*SR)]; o = int(round(e["out"]*SR)); voice[o:o+len(s)] += s*e.get("gain",1)
def tr(a,b): return re.sub(r"[^가-힣0-9]","",mlx_whisper.transcribe(voice[int(a*SR):int(b*SR)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)["text"])
ns = [int(x) for x in sys.argv[1].split(",")]
sm = {x["n"]: x for x in r["sync"]}
for n in ns:
    x = sm[n]; st = x.get("sub_t") or next(s["start"] for s in tl["subs"] if s["n"] == n)
    print(n, x.get("result"), x.get("lead"), x.get("text", "")[:14], "| 앞0.6:", tr(st-0.6, st)[-8:], "| 뒤:", tr(st, st+1.2)[:10], "| 측정말+1.2:", tr(x["voice_t"], x["voice_t"]+1.2)[:10] if "voice_t" in x else "", flush=True)
