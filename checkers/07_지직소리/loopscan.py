#!/usr/bin/env python3
"""loopscan.py src... — 반복 조각(정상 신호) 탐지: 50ms 창 대역에너지(lo/mid/hi)가 연속 ≥0.25s 동안 ±0.3dB 안 + 레벨 > -75dBFS(디지털 무음 아님) → 지직 후보
11/12: 파일을 못 읽거나 소리가 0.25초보다 짧으면 OK 가 아니라 ERROR(종료코드 2) — 「검사 안 함」이 「통과」로 보이던 것 고침."""
import sys,subprocess,numpy as np
bad=0
for src in sys.argv[1:]:
    sr=48000
    pr=subprocess.run(['ffmpeg','-v','error','-i',src,'-map','0:a:0','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True)
    x=np.frombuffer(pr.stdout[:len(pr.stdout)//4*4],np.float32).astype(np.float64)
    if pr.returncode!=0 or len(x)<sr//4:
        print(src.split('/')[-1],'ERROR 소리를 못 읽음(검사 안 함) —',(pr.stderr.decode(errors='replace').strip().splitlines() or ['소리가 없거나 0.25초 미만'])[-1]); bad=1; continue
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
sys.exit(2 if bad else 0)
