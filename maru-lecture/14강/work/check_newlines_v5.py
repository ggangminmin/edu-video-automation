# 14강 v5: 새로 나눈 줄(how 에 줄나눔) 시작 vs 깨끗한 음성(v090 조각을 타임라인 audio 배치로) 실제 말 시작
import json, sys, numpy as np, subprocess as sp
TL = sys.argv[1] if len(sys.argv) > 1 else "../타임라인_v5.json"
tl = json.load(open(TL)); SR = 16000
def load(p): return np.frombuffer(sp.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
src = {}; tot = int((tl["total"] + 1) * SR); clean = np.zeros(tot, np.float32)
for a in tl["audio"]:
    p = "../" + a["src"] if a.get("src") else "v090.wav"
    if p not in src: src[p] = load(p)
    x = src[p][int(a["src_from"] * SR):int(a["src_to"] * SR)] * a.get("gain", 1.0)
    o = int(round(a["out"] * SR)); clean[o:o + len(x)] += x[:tot - o]
H = 80  # 5ms
fr = clean[:len(clean) // H * H].reshape(-1, H); db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
def onset(t, TH=-50, GAP=0.06):
    """t-0.35 ~ t+0.7 안: GAP 이상 조용한 구간 뒤 TH 넘는 첫 칸 중 t 에 가장 가까운 것(말 시작 후보)"""
    i0, i1 = int((t - 0.35) * 200), int((t + 0.7) * 200); best = None; q = 0
    for j in range(i0, i1):
        if db[j] < TH: q += 1
        else:
            if q >= GAP * 200:
                c = j / 200
                if best is None or abs(c - t) < abs(best - t): best = c
            q = 0
    return best
bad = 0; rows = []
for s in tl["subs"]:
    if "줄나눔" not in s.get("how", ""): continue
    on = onset(s.get("voice_on", s["start"]))
    lead = None if on is None else on - s["start"]
    flag = "?" if on is None else ("이름" if lead > 0.16 else ("늦음" if lead < 0 else "ok"))
    if flag != "ok": bad += 1
    rows.append((s["n"], round(s["start"], 3), on and round(on, 3), lead and round(lead, 3), flag, s["text"][:20]))
for r in rows: print(*r)
print("새 줄", len(rows), "· 걸림", bad)
if "-v" in sys.argv:
    for s in tl["subs"]:
        if "줄나눔" not in s.get("how", "") or s["n"] not in [int(x) for x in sys.argv[sys.argv.index("-v") + 1].split(",")]: continue
        t = s["start"]; j0 = int((t - 0.4) * 200)
        print(s["n"], round(t, 3), "voice_on", s.get("voice_on"), s["text"][:16])
        print("  ", " ".join(f"{(j0 + k) / 200:.3f}:{db[j0 + k]:.0f}" for k in range(0, 200, 2)))
if "-d" in sys.argv:
    print("--- 골짜기(쉼 없는 자리): voice_on −0.35~+0.15 안 가장 깊은 5ms 칸 → 그 뒤 첫 상승")
    for s in tl["subs"]:
        if "줄나눔" not in s.get("how", ""): continue
        v = s.get("voice_on", s["start"]); i0, i1 = int((v - 0.35) * 200), int((v + 0.15) * 200)
        k = i0 + int(np.argmin(db[i0:i1])); j = k
        while j < i1 + 40 and db[j] < db[k] + 12: j += 1
        print(s["n"], "sub", round(s["start"], 3), "골짜기", round(k / 200, 3), f"{db[k]:.0f}dB", "상승", round(j / 200, 3), "lead", round(j / 200 - s["start"], 3), s["text"][:14])
