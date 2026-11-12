#!/usr/bin/env python3
"""loopscan.py src... — 반복 조각(정상 신호) 탐지: 50ms 창 대역에너지(lo/mid/hi)가 연속 ≥0.25s 동안 ±0.3dB 안 + 레벨 > -75dBFS(디지털 무음 아님) → 지직 후보"""
import sys,subprocess,numpy as np
for src in sys.argv[1:]:
    sr=48000
    x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-map','0:a:0','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32).astype(np.float64)
    fl=2400;F=np.fft.rfftfreq(fl,1/sr);win=np.hanning(fl);R=[]
    for i in range(0,len(x)-fl,fl):
        P=np.abs(np.fft.rfft(x[i:i+fl]*win))**2
        b=[10*np.log10(P[(F>=a)&(F<c)].sum()+1e-20) for a,c in ((80,1000),(1000,4000),(4000,12000))]
        R.append(b+[20*np.log10(np.sqrt(np.mean(x[i:i+fl]**2))+1e-12)])
    R=np.array(R);n=len(R);hits=[];i=0
    while i<n-1:
        j=i
        while j+1<n and np.all(np.abs(R[j+1,:3]-R[i,:3])<0.3) and R[i,3]>-75: j+=1
        if (j-i+1)*0.05>=0.25: hits.append((i*0.05,(j+1)*0.05,R[i,3])); i=j+1
        else: i+=1
    name=src.split('/')[-1]
    print(name, 'OK' if not hits else ' '.join(f'{a:.2f}-{b:.2f}({b-a:.2f}s,{l:.0f}dBFS)' for a,b,l in hits))
