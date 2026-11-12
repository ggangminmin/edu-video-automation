import sys, numpy as np, soundfile as sf
p, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); step=float(sys.argv[4]) if len(sys.argv)>4 else 0.01
x, sr = sf.read(p, start=int(a*48000) if 'v090' in p else 0); 
x, sr = sf.read(p); x = x if x.ndim==1 else x.mean(1)
for t in np.arange(a, b, step):
    s = x[int(t*sr):int((t+step)*sr)]
    print(f"{t:.3f} {20*np.log10(np.sqrt((s**2).mean())+1e-9):6.1f}")
