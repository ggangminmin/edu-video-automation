# 검사: 문장 안 줄 경계마다 [onset, +1.3s] 받아쓰기가 그 줄 첫 말로 시작하는지, [onset-1.0, onset] 이 그 줄 첫 말을 포함하지 않는지
import json, re, numpy as np, subprocess, mlx_whisper
tl = json.load(open("../타임라인_초안.json"))
off = {s["slide"]: s.get("src_offset", 0) for s in tl["slides"]}
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    seg = x[int(a*16000):int(b*16000)]
    r = mlx_whisper.transcribe(seg, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False, initial_prompt=None)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
NUM = {"일":"1","이":"2","삼":"3","사":"4","오":"5","육":"6","칠":"7","팔":"8","구":"9","십":"10"}
out = []; bad = 0
for k, s in enumerate(tl["subs"]):
    if s.get("how") in ("문장시작",) or k == 0 or s["slide"] == 1: continue
    on = s["voice_on"] - off[s["slide"]]
    after = tr(on, on + 1.3); before = tr(max(0, on - 1.0), on)
    head = n(s["text"])[:2]
    okA = after.startswith(head) or after[:2] in (head,) or (head[:1] in NUM and after[:1] == NUM[head[:1]])
    okB = head not in before[-3:]
    flag = "OK" if okA and okB else "확인"
    if flag != "OK": bad += 1
    out.append(dict(n=s["n"], how=s["how"], text=s["text"], after=after, before=before, result=flag))
    print(s["n"], flag, s["how"], "|", s["text"][:14], "| 뒤:", after[:12], "| 앞:", before[-10:], flush=True)
json.dump(out, open("check_bound.json", "w"), ensure_ascii=False, indent=1)
print("경계", len(out), "확인 필요", bad)
