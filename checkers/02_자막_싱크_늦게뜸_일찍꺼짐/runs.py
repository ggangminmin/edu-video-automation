#!/usr/bin/env python3
"""runs.py <audio> <out.json> [hp] — 말 구간(sync_check 와 같은 기준). hp=1 이면 200Hz~4k 대역만(BGM 섞인 믹스용)."""
import sys,json,subprocess,numpy as np
a,out=sys.argv[1:3]; hp=len(sys.argv)>3
SR=16000; af=['-af','highpass=f=250,lowpass=f=3800'] if hp else []
raw=subprocess.run(['ffmpeg','-v','error','-i',a,'-map','0:a:0','-ac','1','-ar',str(SR)]+af+['-f','s16le','-'],capture_output=True).stdout
x=np.frombuffer(raw,np.int16).astype(np.float32)/32768
hop=160;n=len(x)//hop;db=20*np.log10(np.sqrt((x[:n*hop].reshape(n,hop)**2).mean(1)+1e-12))
thr=np.percentile(db,99)-(14 if not hp else 12); sp=db>thr
runs=[];s=None
for i,v in enumerate(sp):
    if v and s is None:s=i
    if not v and s is not None: runs.append([s,i]);s=None
if s is not None: runs.append([s,len(sp)])   # 11/12: 말하다가 파일이 끝나면 마지막 구간이 빠지던 것
m=[]
for r in runs:
    if m and r[0]-m[-1][1]<8: m[-1][1]=r[1]
    else: m.append(r)
R=[(round(a*hop/SR,3),round(b*hop/SR,3)) for a,b in m if b-a>=8]
json.dump(dict(thr=float(thr),runs=R),open(out,'w')); print(len(R),'runs thr',round(float(thr),1))
