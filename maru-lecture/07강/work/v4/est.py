import numpy as np, subprocess, re
from rms import load
def lufs(m):
    o = subprocess.run(["ffmpeg","-f","f64le","-ar","48000","-ac","1","-i","-","-af","ebur128","-f","null","-"],input=m.tobytes(),capture_output=True).stderr.decode(); return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS",o)[-1])
def rms(m):
    f = m[:len(m)//240*240].reshape(-1,240); r = np.sqrt((f**2).mean(1)); r = r[20*np.log10(r+1e-12) > -40]; return round(float(20*np.log10(np.sqrt((r**2).mean()))),3)
v = load("../v090.wav"); n = load("new_090.wav")
o = v[int(330.50*48000):int(334.96*48000)]; w = n[:int(4.40*48000)]
print("old", lufs(o), rms(o), "peak", 20*np.log10(abs(o).max()))
print("new", lufs(w), rms(w), "peak", 20*np.log10(abs(w).max()))
for nm,(a,b) in {"prev n88-89 368.94→src":(322.2883+0.5,329.6),"next slide9 first":(336.05,339.70)}.items():
    s=v[int(a*48000):int(b*48000)]; print(nm, lufs(s), rms(s))
