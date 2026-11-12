# 자막 줄 시작(말 시작) 검산: 원본(0.9배) 시각 on 에서 [on, on+1.3] 받아쓰기가 그 줄 첫 글자로 시작하고 [on-1.0, on] 끝에 그 글자가 없는지
import json, re, difflib, numpy as np, subprocess, mlx_whisper, sys
tl = json.load(open("../타임라인_초안.json")); off = {s["slide"]: s.get("src_offset", 0) for s in tl["slides"]}
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    r = mlx_whisper.transcribe(x[int(max(0,a)*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
NUM = str.maketrans({"일":"1","이":"2","삼":"3","사":"4"})
res = []
for s in tl["subs"]:
    if s["how"] in ("인삿말", "끝인사"): continue
    on = s["voice_on"] - off[s["slide"]]; head = n(s["text"])[:3]
    af, bf = tr(on, on + 1.3), tr(on - 1.0, on)
    ok_s = max(difflib.SequenceMatcher(None, af[:3], h).ratio() for h in (head, head.translate(NUM))) >= 0.6
    ok_b = not any(difflib.SequenceMatcher(None, bf[-3-k:][:3], head).ratio() >= 0.75 for k in range(3))
    res.append(dict(n=s["n"], slide=s["slide"], on=round(on,3), how=s["how"], text=s["text"][:16], after=af[:10], before=bf[-8:], ok=ok_s and ok_b))
    if not (ok_s and ok_b): print("걸림", res[-1], flush=True)
json.dump(res, open("verify_on.json", "w"), ensure_ascii=False, indent=0)
print("검산", len(res), "줄 · 걸림", sum(not r["ok"] for r in res))
