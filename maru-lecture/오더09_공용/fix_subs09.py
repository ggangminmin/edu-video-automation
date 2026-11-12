# scene_sub_check 가 「늦음·너무빠름」으로 잡은 줄 → 검사기 말 시작(voice_t)을 깨끗한 음성에서 확인(앞 0.12초 안 가장 조용한 30ms ≤ −35dB · 뒤 0.15초 ≥ 앞+10dB)
#  확인되면 sub_fix_NN.json 에 {줄 글: 출력 말 시작} 기록(fix09_tl.py 가 반영). 장면 첫 줄(장면 시작에 묶임)·확인 안 된 줄은 사람 확인으로.
import sys, json, numpy as np, librosa
N = sys.argv[1]; tl = json.load(open(f"{N}강/타임라인_v2.json")); r = json.load(open(f"{N}강/검사_v2/scene_sub.json"))
subs = {x["n"]: x for x in tl["subs"]}; first = {}
for x in tl["subs"]: first.setdefault(x["slide"], x["n"])
def clean_db(t0, t1):
    for a in tl["audio"]:
        src = f"{N}강/" + (a["src"] if a.get("src") else "work/v090.wav"); a0 = a["out"]; a1 = a0 + a["src_to"] - a["src_from"]
        if a0 <= t0 and t1 <= a1:
            y, _ = librosa.load(src, sr=16000, offset=a["src_from"] + t0 - a0, duration=t1 - t0); return y
    return None
fix, manual = {}, []
for s in r["sync"]:
    if s["result"] not in ("늦음", "너무빠름"): continue
    x = subs[s["n"]]; vt = s["voice_t"]
    if first[x["slide"]] == x["n"]: manual.append((s["n"], "장면 첫 줄", s["lead"])); continue
    y = clean_db(vt - 0.15, vt + 0.15)
    if y is None: manual.append((s["n"], "소리 조각 밖", s["lead"])); continue
    db = lambda a, b: 20 * np.log10(np.sqrt((y[int(a * 16000):int(b * 16000)] ** 2).mean()) + 1e-7)
    pre = min(db(0.03 + k * 0.01, 0.06 + k * 0.01) for k in range(10)); post = db(0.15, 0.30)
    if pre <= -35 and post - pre >= 10: fix[x["text"]] = round(vt, 3)
    else: manual.append((s["n"], f"확인 안 됨 pre{pre:.0f} post{post:.0f}", s["lead"]))
json.dump(fix, open(f"오더09_공용/sub_fix_{N}.json", "w"), ensure_ascii=False, indent=1)
print(N, "고침", len(fix), "| 사람 확인", manual)
