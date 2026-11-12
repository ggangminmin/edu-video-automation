#!/usr/bin/env python3
"""passed_match.py <master_index.npz> <passed_dir> <out.md> — 민석 합격 클립(passed/*.mp4)이 새 마스터에 그대로 들어갔는지.
화면 설정 필수(--screen 또는 QA_SCREEN — 자막바 위치 · fps). 마스터 인덱스(frame_index.py)와 같은 설정을 쓴다.
화면 48x27 로 위치(오프셋)를 찾고, 그 오프셋에서 화면차 + 자막바 영역(96x6)차를 전 샘플(최대 240점) 검증. 자막 유무·글자 차이는 바 영역 지표로 잡는다."""
import sys,os,glob,subprocess,numpy as np
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'03_빈_자막바')); import screen_cfg
S=screen_cfg.load()
idx,pdir,out=sys.argv[1:4]; W,H=48,27; BW,BH=96,6; FPS=S['fps']
Z=np.load(idx); M=Z['frame'].astype(np.int16); MB=Z['bar'].astype(np.int16)
def ts(f): t=f/FPS; return f'{int(t//60)}:{t%60:05.2f}'
def grab(mp4,vf,n):
    b=subprocess.run(['ffmpeg','-v','error','-i',mp4,'-map','0:v:0','-vf',vf,'-f','rawvideo','-'],capture_output=True).stdout
    m=len(b)//n; return np.frombuffer(b[:m*n],np.uint8).reshape(m,n).astype(np.int16)
L=['# 합격 클립 ↔ 마스터 대조','',f'마스터 인덱스 {idx} ({len(M)}f) · 화면차/바차 = 0~255 평균 화소차 · 바차 ≥ 10 = 자막 유무/글자 다름','','|클립|길이|마스터 위치|화면차 평균/최대|바차 평균/최대(어디)|다른 샘플|판정|','|---|---|---|---|---|---|---|']
for clip in sorted(glob.glob(os.path.join(pdir,'*.mp4'))+glob.glob(os.path.join(pdir,'*.mov'))):
    C=grab(clip,f'scale={W}:{H}:flags=area,format=gray',W*H); CB=grab(clip,screen_cfg.crop(S['subbar'])+f',scale={BW}:{BH}:flags=area,format=gray',BW*BH); n=min(len(C),len(CB))
    step=max(1,n//240); ks=np.arange(0,n,step)
    best=np.array([int(np.abs(M-C[k]).mean(1).argmin()) for k in ks[::2]])
    offs=best-ks[::2]; vals,cnts=np.unique(offs//3,return_counts=True); off0=int(vals[cnts.argmax()]*3)
    bo=None;bd=1e9
    for o in range(max(0,off0-3),off0+4):
        pos=o+ks
        if pos[-1]>=len(M) or pos[0]<0: continue
        d=np.abs(M[pos]-C[ks]).mean(1)
        if d.mean()<bd: bd=d.mean();bo=o;dd=d
    if bo is None: L.append(f'|{os.path.basename(clip)}|{n}f|-|-|-|-|❌ 위치 못 찾음|'); print(clip,'위치 못 찾음'); continue
    pos=bo+ks; db=np.abs(MB[pos]-CB[ks]).mean(1)
    bad=[int(k) for k,x,y in zip(ks,dd,db) if x>=8 or y>=10]
    # 다른 샘플 구간 묶기
    rng=[]; 
    for k in bad:
        if rng and k-rng[-1][1]<=step*2: rng[-1][1]=k
        else: rng.append([k,k])
    rs=' '.join(f'{ts(bo+a)}~{ts(bo+b+step)}' for a,b in rng[:8])+(' …' if len(rng)>8 else '')
    v='✅ 그대로' if not bad else ('⚠️ 일부 다름' if len(bad)<len(ks)*0.4 else '❌ 다름')
    row=f'|{os.path.basename(clip)}|{n}f {n/FPS:.1f}s|f{bo}~f{bo+n} ({ts(bo)}~{ts(bo+n)})|{dd.mean():.1f}/{dd.max():.0f}|{db.mean():.1f}/{db.max():.0f}({ts(bo+int(ks[db.argmax()]))})|{len(bad)}/{len(ks)} {rs}|{v}|'
    L.append(row); print(row)
open(out,'w').write('\n'.join(L))
