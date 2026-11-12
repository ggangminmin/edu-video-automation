#!/usr/bin/env python3
"""buzz.py <src> [--min 0.15] — 지직(주기 펄스 열) 탐지: 4-12k 대역 포락선 1ms, 200ms 창 자기상관 피크(지연 8~60ms)≥0.6 + 크레스트 높음 + 유성 배음 약함 → 구간 출력"""
import sys,subprocess,numpy as np
src=sys.argv[1];sr=48000
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-map','0:a:0','-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True).stdout,np.float32).astype(np.float64)
X=np.fft.rfft(x);F=np.fft.rfftfreq(len(x),1/sr);Xh=X.copy();Xh[(F<4000)|(F>12000)]=0
h=np.fft.irfft(Xh,len(x));env=np.abs(h)
m=48;n=len(env)//m;e=env[:n*m].reshape(n,m).max(1)  # 1ms
tot=np.sqrt(np.mean(x[:n*m].reshape(n,m)**2,1))
W=200;hits=[]
for i in range(0,n-W,20):
    s=e[i:i+W];
    if s.mean()<1e-4 or 20*np.log10(tot[i:i+W].mean()+1e-9)<-45: continue
    s=s-s.mean();ac=np.correlate(s,s,'full')[W-1:];ac=ac/ (ac[0]+1e-12)
    k=8+np.argmax(ac[8:60]);crest=e[i:i+W].max()/ (e[i:i+W].mean()+1e-12)
    if ac[k]>0.55 and crest>3.5: hits.append((i/1000,k,ac[k]))
# 병합
out=[];
for t,k,a in hits:
    if out and t-out[-1][1]<=0.06: out[-1][1]=t+0.2;out[-1][2]=max(out[-1][2],a)
    else: out.append([t,t+0.2,a,k])
mn=float(sys.argv[sys.argv.index('--min')+1]) if '--min' in sys.argv else 0.15
for s,t,a,k in out:
    if t-s>=mn: print(f'{s:.2f}-{t:.2f} ({t-s:.2f}s) ac{a:.2f} period{k}ms')
