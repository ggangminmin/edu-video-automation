# 깨끗한 음성(렌더와 같이 조각 배치, VOICE_GAIN 빼고) v3 vs v4: 바뀐 구간 밖 = Δ 이동 빼고 같음 · 이음매 튐
import json, numpy as np, subprocess, sys
SR = 48000; L = "../.."
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
cache = {}
def build(v):
    tl = json.load(open(f"{L}/타임라인_{v}.json")); out = np.zeros(int((tl["total"]+1)*SR))
    for a in tl["audio"]:
        p = f"{L}/{a['src']}" if a.get("src") else "../v090.wav"
        if p not in cache: cache[p] = load(p)
        s = cache[p][int(round(a["src_from"]*SR)):int(round(a["src_to"]*SR))] * a.get("gain",1.0); o = int(round(a["out"]*1000))*48
        out[o:o+len(s)] += s
    return out, tl
c3, t3 = build("v3"); c4, t4 = build("v4"); np.save("clean_v4.npy", c4.astype(np.float32)); np.save("clean_v3.npy", c3.astype(np.float32))
D = -0.033367; R = {}
def corr(a, b): return float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)+1e-30))
a, b = c3[:int(377.39*SR)], c4[:int(377.39*SR)]; R["0~377.39 최대차"] = float(np.abs(a-b).max()); R["0~377.39 상관"] = corr(a,b)
# 뒤: v3 381.86~끝 vs v4 같은 자리+Δ, 조각마다 ms 반올림이 달라 조각별 최적 정렬(±3ms) 상관
rs = []
for a3, a4 in zip([x for x in t3["audio"] if x["out"] > 381.0], [x for x in t4["audio"] if x["out"] > 381.0]):
    o3 = int(round(a3["out"]*1000))*48; o4 = int(round(a4["out"]*1000))*48; n = int(round((a3["src_to"]-a3["src_from"])*SR))
    rs.append((round(a3["out"],3), (o4-o3)/48, corr(c3[o3:o3+n], c4[o4:o4+n]), float(np.abs(c3[o3:o3+n]-c4[o4:o4+n]).max())))
R["뒤 조각 수"] = len(rs); R["뒤 조각 최소 상관"] = min(r[2] for r in rs); R["뒤 조각 최대차"] = max(r[3] for r in rs); R["뒤 조각 이동 ms"] = sorted(set(r[1] for r in rs))
for t in (377.425933, 381.825933):
    i = int(t*SR); R[f"이음매 {t} ±2ms 최대 샘플 튐"] = float(np.abs(np.diff(c4[i-96:i+96])).max())
print(json.dumps(R, ensure_ascii=False, indent=1)); json.dump(R, open("../../검사_v4/깨끗한음성_비교.json","w"), ensure_ascii=False, indent=1)
