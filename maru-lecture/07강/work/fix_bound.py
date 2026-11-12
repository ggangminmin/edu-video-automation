# (15강 판 복사 · 강 번호 자동)
# 걸린 경계·골짜기 경계: 음량 골짜기 후보들 중 [t-1.0,t]에 첫 말이 없고 [t,t+1.3]이 첫 말로 시작하는 가장 이른 t
import json, re, difflib, numpy as np, subprocess, mlx_whisper
from lec import N
tl = json.load(open("../타임라인_초안.json")); off = {s["slide"]: s.get("src_offset", 0) for s in tl["slides"]}
BODY = [x for x in tl["subs"] if "part" not in x]   # 인삿말 줄 제외
cb = {c["n"]: c for c in json.load(open("check_bound.json"))}
DB = np.load("rmsdb.npy"); H = 0.005
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
def starts(after, head): return difflib.SequenceMatcher(None, after[:len(head)], head).ratio() >= 0.6
def ends_with(before, head): return any(difflib.SequenceMatcher(None, before[-len(head)-k:][:len(head)], head).ratio() >= 0.75 for k in range(0, 3))
targets = [c["n"] for c in cb.values() if c["result"] != "OK" or c["how"] == "골짜기"]
over = {}
for N in targets:
    s = tl["subs"][N - 1]; prev = tl["subs"][N - 2]
    LI = BODY.index(s)   # lines 순번(align.py on[] 인덱스)
    on = s["voice_on"] - off[s["slide"]]; pon = prev["voice_on"] - off[prev["slide"]]
    head = n(s["text"])[:3]
    a0 = int(max(pon + 0.4, on - 0.9) / H); b0 = int((on + 0.4) / H)
    seg = DB[a0:b0]
    mins = [a0 + i for i in range(2, len(seg) - 2) if seg[i] == seg[i-2:i+3].min() and seg[i] < seg[max(0,i-20):i+20].max() - 6]
    cands = []
    for j in mins:
        k = j
        while k < j + 40 and DB[k] < DB[j] + 6: k += 1
        cands.append(round(k * H, 3))
    cands = sorted(set(cands))
    pick = None; log = []
    for t in cands:
        af, bf = tr(t, t + 1.3), tr(max(0, t - 1.0), t)
        ok = starts(af, head) and not ends_with(bf, head)
        log.append((t, ok, af[:8], bf[-8:]))
        if ok: pick = t; break
    print(N, s["text"][:14], "원래", round(on, 3), "→", pick, log, flush=True)
    if pick is not None and abs(pick - on) > 0.02: over[LI] = pick
json.dump(over, open("onset_override.json", "w"), indent=1)
print("보정", len(over), over)
