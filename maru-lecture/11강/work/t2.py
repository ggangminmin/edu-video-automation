import json,numpy as np,re,subprocess
db=np.load("rmsdb.npy"); H=0.005
exec(open("evalsync.py").read().split("v1={n")[0])
def sil(d=0.05,th=-40):
    o=subprocess.run(["ffmpeg","-hide_banner","-i","v090.wav","-af",f"silencedetect=n={th}dB:d={d}","-f","null","-"],capture_output=True,text=True).stderr
    return list(zip(map(float,re.findall(r"silence_start: ([\d.]+)",o)),map(float,re.findall(r"silence_end: ([\d.]+)",o))))
S=sil()
def onset(est,prev):
    c=[(s0,e0) for s0,e0 in S if est-0.5<=s0<=est+0.3 and est-0.15<=e0<=est+0.8 and s0>prev+0.3]
    if c: return min(c,key=lambda z:abs(z[1]-est))[1],"sil"
    a=int((est-0.12)/H); b=int((est+0.3)/H)
    seg=db[a:b]; i=int(np.argmin(seg)); tmin=(a+i)*H
    # 골 뒤에서 소리가 다시 오르는 지점(골+6dB)
    j=a+i
    while j<b+40 and db[j]<db[a+i]+4: j+=1
    return j*H,"dip"
cont=[52,104,107,120,146,165,167,204]
for n in cont:
    est=Tm[n-1]; prev=Tm[n-2]
    t,how=onset(est,prev); print(n,how,"err",round(t-gt_src[n],3))
