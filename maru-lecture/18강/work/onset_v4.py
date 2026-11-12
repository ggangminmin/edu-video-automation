# 18강 v4 cx U1 대응: 시작 시각이 v3c 와 다른 자막 줄마다 첫 어절 실소리 시작을 깨끗한 음성(타임라인 audio 대로 깐 v090·인삿말·끝인사)에서 잼
#  ① 5ms RMS: voice_on(받아쓰기) ±0.15초 안 가장 깊은 골짜기 → 골짜기+10dB 넘는 첫 시각 = 소리 시작  ② mlx 받아쓰기: [시작, +1.3초] 첫 어절 = 그 줄 첫 어절 · [시작−0.8, 시작] 에 그 어절 없음
import json, sys, os, numpy as np, re, subprocess
def _load(f): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
tl = json.load(open(sys.argv[1])); SR = 16000
src = {None: _load("v090.wav")}
V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in src: src[k] = _load("../" + k if not k.startswith("work/") else k.replace("work/", ""))
    y = src[k][int(s["src_from"] * SR):int(s["src_to"] * SR)]; o = int(s["out"] * SR); V[o:o + len(y)] += y
np.save("clean_v4_16k.npy", V)
H = 80
db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
old = {(round(s["start"], 4)) for s in json.load(open("../타임라인_v3c.json"))["subs"]}
rows = []
for s in tl["subs"]:
    if round(s["start"], 4) in old or not s.get("voice_on"): continue
    v = s["voice_on"]
    if os.environ.get("USE_VOICE"):
        rows.append(dict(n=s["n"], text=s["text"], sub=round(s["start"], 4), asr_on=v, valley=None, valley_db=None, onset=v, lead=round(v - s["start"], 3))); continue
    i0, i1 = int((v - 0.15) * 200), int((v + 0.15) * 200)
    m = i0 + int(np.argmin(db[i0:i1])); j = m
    while db[j] < db[m] + 10: j += 1
    on = j / 200
    rows.append(dict(n=s["n"], text=s["text"], sub=round(s["start"], 4), asr_on=v, valley=round(m / 200, 3), valley_db=round(float(db[m]), 1), onset=round(on, 3), lead=round(on - s["start"], 3)))
import mlx_whisper
for r in rows:
    a = V[int((r["onset"] - 0.03) * SR):int((r["onset"] + 1.3) * SR)]; b = V[int((r["onset"] - 0.9) * SR):int((r["onset"] - 0.03) * SR)]
    ta = mlx_whisper.transcribe(a, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
    tb = mlx_whisper.transcribe(b, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
    w0 = r["text"].split()[0].strip(",.")
    r.update(after=ta, before=tb, first_ok=ta.replace(" ", "").startswith(w0[:2]), before_ok=w0[:2] not in tb.replace(" ", "")[-4:])
    print(r, flush=True)
json.dump(rows, open(sys.argv[2] if len(sys.argv) > 2 else "../검사_v4/onset_v4.json", "w"), ensure_ascii=False, indent=1)
