import numpy as np, subprocess, sys
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
def env(x, a, b):
    s = x[int(a*48000):int(b*48000)]; f = s[:len(s)//240*240].reshape(-1,240); return 20*np.log10(np.sqrt((f**2).mean(1))+1e-12)
def runs(e, a, th=-40):
    on = e > th; out=[]; i=0
    while i < len(on):
        if on[i]:
            j=i
            while j<len(on) and on[j]: j+=1
            out.append((round(a+i*0.005,3), round(a+j*0.005,3))); i=j
        else: i+=1
    return out
if __name__=='__main__':
    v = load("../v090.wav"); n = load("new_090.wav")
    print("old v090 329.0-336.5 runs>-40:", runs(env(v,329.0,336.5),329.0))
    print("new runs>-40:", runs(env(n,0,len(n)/48000),0))
    e = env(n,0,0.3); print("new head", np.round(e[:30],1))
    e = env(n,len(n)/48000-0.6,len(n)/48000); print("new tail", np.round(e,1))
    e = env(v,330.0,330.7); print("old head 330.0", np.round(e,1))
    e = env(v,334.6,335.3); print("old tail 334.6", np.round(e,1))
