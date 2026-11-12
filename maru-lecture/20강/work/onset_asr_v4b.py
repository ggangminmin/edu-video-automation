# 오더34 v4b: 새 줄 시작(실소리) 검증 — [시작−0.03, +1.3] 받아쓰기 첫 어절 = 그 줄 첫 어절 · [시작−0.9, −0.03] 끝에 그 어절 없음 (18강 onset_v4.py ② 와 같음)
# 실행(cwd=NN강/work): heavy_run.sh asr ~/.venvs/tts/bin/python ../../20강/work/onset_asr_v4b.py
import json, numpy as np, subprocess, mlx_whisper
def _load(f): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
tl = json.load(open("../타임라인_v4b.json")); SR = 16000; src = {None: _load("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in src: src[k] = _load(k.replace("work/", ""))
    y = src[k][int(s["src_from"] * SR):int(s["src_to"] * SR)]; o = int(s["out"] * SR); V[o:o + len(y)] += y
rows = json.load(open("onset_v4b.json")); out = []
for r in rows:
    if "onset" not in r: continue
    for name, t in (("asr", r["asr"]), ("onset", r["onset"])):
        a = V[int((t - 0.03) * SR):int((t + 1.3) * SR)]; b = V[int((t - 0.9) * SR):int((t - 0.03) * SR)]
        ta = mlx_whisper.transcribe(a, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
        tb = mlx_whisper.transcribe(b, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
        w0 = r["text"].split()[0].strip(",.")
        r[name + "_after"] = ta; r[name + "_before"] = tb
        r[name + "_ok"] = ta.replace(" ", "").startswith(w0[:2]) and w0[:2] not in tb.replace(" ", "")[-4:]
    print({k: r[k] for k in ("n", "text", "asr", "onset", "asr_ok", "onset_ok", "onset_after", "onset_before")}, flush=True)
    out.append(r)
json.dump(out, open("onset_v4b_asr.json", "w"), ensure_ascii=False, indent=1)
print("onset_ok", sum(r["onset_ok"] for r in out), "/", len(out), "· asr_ok", sum(r["asr_ok"] for r in out))
