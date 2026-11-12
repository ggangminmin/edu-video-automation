#!/usr/bin/env python3
"""crackle.py <wav/mp4> [cuts.json|-] — 구간별 지직 지표: 잡음 바닥(dB, 무음부 2-8k)·클릭 수(2차 미분 스파이크/초)·고역비(4-8k/0.1-1k, 유성)·스펙트럼 평탄도"""
import sys,subprocess,json,numpy as np
src=sys.argv[1];sr=48000
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-map','0:a:0','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32).astype(np.float64)
cuts=json.loads(sys.argv[2]) if len(sys.argv)>2 else {'all':{'t0':0,'t1':len(x)/sr}}
def an(a):
    fl=1024;hop=480;F=np.fft.rfftfreq(fl,1/sr);win=np.hanning(fl)
    rows=[]
    for i in range(0,len(a)-fl,hop):
        s=a[i:i+fl];P=np.abs(np.fft.rfft(s*win))**2+1e-20
        e=10*np.log10(P.sum())
        hi=P[(F>4000)&(F<8000)].sum();lo=P[(F>100)&(F<1000)].sum()
        fl_=np.exp(np.mean(np.log(P[(F>300)&(F<8000)])))/np.mean(P[(F>300)&(F<8000)])
        rows.append((e,10*np.log10(hi/lo),fl_,10*np.log10(P[(F>2000)&(F<8000)].sum())))
    r=np.array(rows);emax=r[:,0].max()
    v=r[:,0]>emax-25; q=r[:,0]<emax-45
    d2=np.abs(np.diff(a,2));thr=np.median(d2)*40
    clicks=(d2>thr).sum()/(len(a)/sr)
    return dict(hiratio=round(np.median(r[v,1]),1),flat=round(np.median(r[v,2]),3),floor=round(np.median(r[q,3]),1) if q.any() else None,clicks=round(clicks,1))
for k,c in cuts.items():
    a=x[int(c['t0']*sr):int(c['t1']*sr)]
    print(k,an(a))
