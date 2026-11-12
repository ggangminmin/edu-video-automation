# 최종 출력 음량(09강 v7b cx 방식 · 07강 v4 out_loud 사본): (L+R)/2 · 옛 v3 / 새 v4 같은 문장 창 · LUFS(ebur128) · 5ms 발화칸 RMS(−40 넘음) · 앞뒤 문장도
import subprocess, numpy as np, re, json
SR = 48000
def get(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ar","48000","-ac","2","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64).reshape(-1,2)
def lufs(m):
    o = subprocess.run(["ffmpeg","-f","f64le","-ar","48000","-ac","1","-i","-","-af","ebur128","-f","null","-"],input=m.tobytes(),capture_output=True).stderr.decode(); return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS",o)[-1])
def rms(m):
    f = m[:len(m)//240*240].reshape(-1,240); r = np.sqrt((f**2).mean(1)); r = r[20*np.log10(r+1e-12) > -40]; return round(float(20*np.log10(np.sqrt((r**2).mean()))),3)
W = {"옛 v3 #21": ("v3", 78.95, 82.10), "새 v4 #21": ("v4", 78.95, 82.47),
     "앞 #20(v3=v4)": ("v4", 73.95, 77.48), "뒤 #22(v4)": ("v4", 82.79, 85.58), "뒤 #22(v3)": ("v3", 82.42, 85.21)}
R = {}
for kind, pat in (("mp4", "../../05강_{}.mp4"), ("mix", "../mix_{}.wav")):
    X = {v: get(pat.format(v)) for v in ("v3", "v4")}; R[kind] = {}
    for k, (v, a, b) in W.items():
        m = X[v][int(a*SR):int(b*SR)].mean(1); R[kind][k] = dict(LUFS=lufs(m), RMS=rms(m))
    n = R[kind]["새 v4 #21"]
    for k in ("옛 v3 #21", "앞 #20(v3=v4)", "뒤 #22(v4)"):
        R[kind][f"새−{k}"] = dict(LU=round(n["LUFS"] - R[kind][k]["LUFS"], 2), RMS=round(n["RMS"] - R[kind][k]["RMS"], 3))
    x = X["v4"]; R[kind]["v4 전체 피크 dBFS"] = round(float(20*np.log10(np.abs(x).max())), 2); R[kind]["0dBFS 샘플"] = int((np.abs(x) >= 0.99997).sum())
    R[kind]["v4 L=R 최대차"] = float(np.abs(x[:,0]-x[:,1]).max())
print(json.dumps(R, ensure_ascii=False, indent=1)); json.dump(R, open("../../검사_v4/출력음량.json","w"), ensure_ascii=False, indent=1)
