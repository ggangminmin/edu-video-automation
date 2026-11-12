#!/usr/bin/env python3
"""capsync.py <subbar.json> <runs.json> <scd.log> <out_prefix> [whisper.json]
마스터 단독 자막↔대사 스템 싱크 전수(읽기 전용, 빌더 표 안 씀).
자막 구간 = 자막바(bar>.4)+글자(dark>=200) 연속, 경계 = subbar_scan changes.
판정(브리프 기준: 첫소리에 켜고 말끝+0.3s 끔, 같은 자막 안 쉼에 안 꺼짐, 다른 화면 이전 자막 없음, 빈 바 없음):
 LATE    자막 켜짐이 그 말 첫소리보다 0.20s↑ 늦음
 MIDON   자막 교체/켜짐이 말 도중(앞말 구간 안쪽 0.12s↑)
 MIDOFF  자막이 꺼지는데(교체 아님) 말 도중
 LINGER  말끝 뒤 자막 1.0s↑ 남음(0.6~1.0 = 참고)
 CROSS   화면 컷 뒤에 앞 문장 자막이 남음(말끝 < 컷−0.15, 컷 뒤 0.25s↑)
 EMPTY   글자 없는 자막바 6f↑ (바 테두리 실존 조건 — 흰 카드 바닥 오검출 방지. 테두리색 · 바 위치는 subbar_scan 이 화면 설정에서 읽어 json 에 담음 → 이 파일은 화면 설정 불필요)
"""
import sys,json,re,bisect,numpy as np
sb,rj,scd,outp=sys.argv[1:5]; wj=sys.argv[5] if len(sys.argv)>5 else None
S=json.load(open(sb)); FPS=S['fps']; bar=np.array(S['bar']); dark=np.array(S['dark']); ch=set(S['changes']); n=len(bar)
border=np.array(S.get('border',[1.0]*n))   # 없으면 옛 json: 테두리 검사 생략
R=json.load(open(rj))['runs']; st=np.array([a for a,b in R]); en=np.array([b for a,b in R])
cuts=[]
for m in re.finditer(r'lavfi\.scd\.score:\s*([\d.]+),\s*lavfi\.scd\.time:\s*([\d.]+)',open(scd).read()):
    if float(m.group(1))>=14: cuts.append(float(m.group(2)))
cuts=np.array(cuts)
W=None
if wj:
    W=[]
    for seg in json.load(open(wj))['transcription']:
        t0=seg['offsets']['from']/1000; t1=seg['offsets']['to']/1000; W.append((t0,t1,seg['text']))
def words(a,b):
    if not W: return ''
    return ''.join(t for t0,t1,t in W if t0<b and t1>a).strip()
def ts(t): return f'{int(t//60)}:{t%60:05.2f}'
txt=(bar>.4)&(dark>=200); emp=(bar>.4)&(dark<200)&(border>0.5)   # 빈 바 = 바 테두리가 실제로 있을 때만(흰 카드 바닥 오검출 방지, 10/14)
segs=[];i=0
while i<n:
    if not txt[i]: i+=1;continue
    j=i+1
    while j<n and txt[j] and j not in ch: j+=1
    if j-i>=4: segs.append((i,j))
    i=j
empties=[];i=0
while i<n:
    if not emp[i]: i+=1;continue
    j=i+1
    while j<n and emp[j]: j+=1
    if j-i>=6: empties.append((i,j))
    i=j
def inside(t,pad=.12):
    k=np.searchsorted(st,t)-1
    return k>=0 and st[k]+pad<t<en[k]-pad
rows=[]
for k,(a,b) in enumerate(segs):
    t0,t1=a/FPS,b/FPS
    swap_in = a in ch and k>0 and segs[k-1][1]==a      # 앞 자막에서 바로 교체돼 켜짐
    swap_out= k+1<len(segs) and segs[k+1][0]==b          # 다음 자막으로 바로 교체돼 꺼짐
    # 이 자막의 말: 켜짐 뒤 첫 말 구간(또는 켜짐 직전 1.2s 안에 시작한 구간)
    kk=np.searchsorted(st,t0-1.2)
    s_on=None
    for q in range(kk,len(st)):
        if st[q]>=t1-0.1: break
        if en[q]>t0-0.05: s_on=float(st[q]); break
    # 말끝 = 꺼짐 전 마지막 구간 끝(꺼짐이 구간 안이면 그 구간 끝 = 말중)
    q=np.searchsorted(st,t1+0.05)-1
    s_off=float(en[q]) if q>=0 and en[q]>t0 else None
    fl=[];info={}
    if inside(t0):
        q0=np.searchsorted(st,t0)-1; fl.append(f'MIDON(앞말 {en[q0]-t0:.2f}s 더 이어짐)'); info['midon']=round(float(en[q0]-t0),2)
    elif s_on is not None and s_on<t0-0.20 and not inside(t0):
        # s_on 이 앞 자막의 말이 아닌지: 앞 자막 꺼짐 이후에 시작한 말이면 지연
        prev_end=segs[k-1][1]/FPS if k>0 else -1
        if s_on>=prev_end-0.3 or not swap_in:
            fl.append(f'LATE(첫소리 뒤 {t0-s_on:.2f}s)'); info['late']=round(t0-s_on,2)
    if inside(t1) and not swap_out:
        q1=np.searchsorted(st,t1)-1; fl.append(f'MIDOFF(말 {en[q1]-t1:.2f}s 남았는데 꺼짐)'); info['midoff']=round(float(en[q1]-t1),2)
    tail=None
    if s_off is not None and not inside(t1):
        tail=t1-s_off; info['tail']=round(tail,2)
        if tail>=1.0: fl.append(f'LINGER(말끝 뒤 {tail:.2f}s 남음)')
        elif tail>=0.6: fl.append(f'linger참고({tail:.2f}s)')
    cin=[float(c) for c in cuts if t0+0.1<c<t1-0.05]
    for c in cin:
        if s_off is not None and s_off<c-0.15 and t1-c>=0.25 and not inside(c):
            fl.append(f'CROSS(컷 {ts(c)} 뒤 앞자막 {t1-c:.2f}s)'); info['cross']=round(c,2)
    rows.append(dict(k=k,f0=a,f1=b,t0=round(t0,2),t1=round(t1,2),s_on=None if s_on is None else round(s_on,2),s_off=None if s_off is None else round(s_off,2),swap_in=swap_in,swap_out=swap_out,flags=fl,**info,text=words(s_on if s_on else t0, s_off if s_off else t1)))
erows=[dict(f0=a,f1=b,t0=round(a/FPS,2),t1=round(b/FPS,2),frames=b-a) for a,b in empties]
json.dump(dict(segs=rows,empty=erows),open(outp+'.json','w'),ensure_ascii=False,indent=0)
from collections import Counter
C=Counter(f.split('(')[0] for r in rows for f in r['flags'])
L=[f'# 자막↔대사 스템 싱크 전수 — {outp}',f'자막 구간 {len(segs)} · 말 구간 {len(R)} · 화면 컷 {len(cuts)} · 빈 바 {len(empties)}','',
   '판정 수: '+', '.join(f'{k} {v}' for k,v in C.items()),'',
   '|#|켜짐|꺼짐|첫소리|말끝|판정|대사(whisper)|','|---|---|---|---|---|---|---|']
for r in rows:
    if not r['flags']: continue
    L.append(f"|{r['k']}|{ts(r['t0'])} f{r['f0']}|{ts(r['t1'])} f{r['f1']}|{ts(r['s_on']) if r['s_on'] is not None else '-'}|{ts(r['s_off']) if r['s_off'] is not None else '-'}|{' / '.join(r['flags'])}|{r['text'][:40]}|")
L+=['','## 빈 자막바(글자 없음)','','|시작|끝|프레임|','|---|---|---|']+[f"|{ts(e['t0'])} f{e['f0']}|{ts(e['t1'])} f{e['f1']}|{e['frames']}|" for e in erows]
open(outp+'.md','w').write('\n'.join(L))
print('segs',len(segs),'flags',dict(C),'empty',len(empties))
