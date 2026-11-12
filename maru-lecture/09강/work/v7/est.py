# 렌더 경로 그대로(aformat mono) 옛 v090 문장 vs 새 조각(게인 G) — LUFS · 5ms 발화칸 RMS 차
import subprocess, numpy as np, re, sys
def get(p, a, b, extra=""):
    return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-af",f"aformat=sample_rates=48000:channel_layouts=mono,atrim={a}:{b}{extra}","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
def lufs(x):
    o = subprocess.run(["ffmpeg","-f","f64le","-ar","48000","-ac","1","-i","-","-af","ebur128","-f","null","-"],input=x.tobytes(),capture_output=True).stderr.decode(); return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS",o)[-1])
def rms(x):
    f = x[:len(x)//240*240].reshape(-1,240); r = np.sqrt((f**2).mean(1)); r = r[20*np.log10(r+1e-12) > -40]; return 20*np.log10(np.sqrt((r**2).mean()))
old = get("v090.wav", 11.9109, 16.165); new0 = get("v7/new_090.wav", 0, 3.52)
print("old LUFS", lufs(old), "RMS", round(rms(old),2), "peak", round(20*np.log10(np.abs(old).max()),2))
for G in [float(g) for g in sys.argv[1:]]:
    n = new0 * 10**(G/20); print(f"G {G}: LUFS {lufs(n)} (차 {lufs(n)-lufs(old):+.2f}) RMS {rms(n):.2f} (차 {rms(n)-rms(old):+.2f}) peak {20*np.log10(np.abs(n).max()):.2f}")
