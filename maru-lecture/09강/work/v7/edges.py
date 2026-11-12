import numpy as np, soundfile as sf, sys
def mono(p):
    x, sr = sf.read(p); return (x.mean(1) if x.ndim > 1 else x), sr
def env(x, sr, a, b, h=0.001, w=0.005):
    ts = np.arange(a, b, h); return ts, np.array([20*np.log10(np.sqrt((x[int(t*sr):int((t+w)*sr)]**2).mean())+1e-9) for t in ts])
v, sr = mono("v090.wav"); n, _ = mono("v7/new_090.wav")
for name, x, a, b in [("old_on", v, 11.85, 12.0), ("old_end", v, 16.05, 16.30), ("new_on", n, 0.0, 0.12), ("new_end", n, 3.40, 3.6)]:
    ts, d = env(x, sr, a, b)
    up = [round(t,3) for t, y in zip(ts, d) if y > -40][:1]; dn = [round(t+0.005,3) for t, y in zip(ts, d) if y > -40][-1:]
    print(name, "first>-40", up, "last>-40 end", dn)
# 16.14~16.26 detail
ts, d = env(v, sr, 16.12, 16.27, 0.005); print(" ".join(f"{t:.3f}:{y:.0f}" for t, y in zip(ts, d)))
def lufs_rms(x, sr):
    import pyloudnorm as pl
    return pl.Meter(sr).integrated_loudness(x)
o = v[int(11.92*sr):int(16.16*sr)]; m = n[int(0.0*sr):int(3.52*sr)]
act = lambda z: z[np.abs(z) > 0] 
def actrms(z):
    fr = z[:len(z)//240*240].reshape(-1,240); r = np.sqrt((fr**2).mean(1)); r = r[20*np.log10(r+1e-9) > -40]; return 20*np.log10(np.sqrt((r**2).mean()))
print("active RMS old", round(actrms(o),2), "new", round(actrms(m),2))
try: print("LUFS old", round(lufs_rms(o,sr),2), "new", round(lufs_rms(m,sr),2))
except Exception as e: print("no pyloudnorm", e)
print("peak old", round(20*np.log10(np.abs(o).max()),2), "new", round(20*np.log10(np.abs(m).max()),2))
