# 5ms RMS(dBFS, L+R)/2 프로파일 — 옛 v090 #21 구간 · 새 new_090
import numpy as np, subprocess, sys
def load(p, a=0, b=None):
    x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
    return x[int(a*48000): int(b*48000) if b else None]
def prof(x, t0):
    f = x[:len(x)//240*240].reshape(-1,240); d = 20*np.log10(np.sqrt((f**2).mean(1))+1e-12)
    return [(round(t0+i*0.005,3), round(v,1)) for i,v in enumerate(d)]
def segs(p, th=-40, mingap=0.15):
    on=[];cur=None
    for t,v in p:
        if v>th:
            if cur is None: cur=[t,t+0.005]
            elif t-cur[1]>mingap: on.append(cur); cur=[t,t+0.005]
            else: cur[1]=t+0.005
    if cur: on.append(cur)
    return [(round(a,3),round(b,3)) for a,b in on]
o = prof(load("../v090.wav", 55.4, 63.3), 55.4); n = prof(load("new_090.wav"), 0)
print("old v090 발화칸(-40, 쉼>0.15):", segs(o))
print("new 발화칸:", segs(n))
print("new 길이", len(load("new_090.wav"))/48000)
print("old 59.3~60.1:", [x for x in o if 59.3<=x[0]<=60.1])
print("new head:", n[:20]); print("new tail:", n[-30:])
