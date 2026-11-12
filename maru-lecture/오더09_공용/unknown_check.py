# scene_sub 「판정불가·보류」 줄: 깨끗한 음성에서 voice_on 앞 0.12초 안 가장 조용한 30ms ↔ 뒤 0.15초 대비, 그리고 자막 선행(voice_on − start)
import sys, json, numpy as np, librosa
N = sys.argv[1]; tl = json.load(open(f"{N}강/타임라인_v2.json")); r = json.load(open(f"{N}강/검사_v2/scene_sub.json"))
subs = {x["n"]: x for x in tl["subs"]}; first = {}
for x in tl["subs"]: first.setdefault(x["slide"], x["n"])
out = []
for s in r["sync"]:
    if s["result"] not in ("판정불가", "보류"): continue
    x = subs[s["n"]]; t = x["voice_on"]
    for a in tl["audio"]:
        a0 = a["out"]; a1 = a0 + a["src_to"] - a["src_from"]
        if a0 <= t - 0.15 and t + 0.3 <= a1:
            y, _ = librosa.load(f"{N}강/" + (a["src"] if a.get("src") else "work/v090.wav"), sr=16000, offset=a["src_from"] + t - 0.15 - a0, duration=0.45); break
    db = lambda p, q: 20 * np.log10(np.sqrt((y[int(p * 16000):int(q * 16000)] ** 2).mean()) + 1e-7)
    pre = min(db(0.03 + k * 0.01, 0.06 + k * 0.01) for k in range(10)); post = db(0.15, 0.30)
    ok = post - pre >= 10
    out.append((s["n"], s["result"], "장면첫줄" if first[x["slide"]] == x["n"] else "", round(pre), round(post), round(t - x["start"], 3), "OK" if ok else "확인"))
for o in out: print(N, *o)
print(N, "확인 필요", sum(o[-1] == "확인" for o in out), "/", len(out))
