#!/usr/bin/env python3
"""capdiff.py <idx_prev.npz> <idx_new.npz> <subbar_prev.json> <subbar_new.json> <prev.mp4> <new.mp4> <out_prefix> [search]
직전 후보 ↔ 새 후보 자막 글자 대조(읽기 전용). 같은 시계면 search=0, 다르면 ±search 프레임 안에서 화면(48x27)으로 짝 프레임을 찾는다.
새 후보의 글자 자막 구간마다 중간 프레임의 바 영역(96x6)을 직전 후보 짝 프레임과 비교 → 글자 마스크 불일치 ≥35% = 글자 다름/유무 다름 → 목록 + 나란히 시트.
11/12: 직전 후보 자막 구간도 거꾸로 대조해 「새 후보에서 통째로 사라진 자막」을 따로 적는다."""
import sys,json,subprocess,numpy as np,os

def _probe_fps(path, fallback=24000/1001):
    """영상의 실제 프레임 속도(ffprobe). 못 읽으면 fallback. (10/19: 23.976 이 박혀 있던 것을 프로젝트마다 읽게)"""
    try:
        out = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',path],capture_output=True,text=True).stdout.strip()
        a,b = out.split('/'); return float(a)/float(b)
    except Exception:
        return fallback
from PIL import Image,ImageDraw,ImageFont
ip,inew,sp,sn,vp,vn,outp=sys.argv[1:8]; search=int(sys.argv[8]) if len(sys.argv)>8 else 0; FPS=_probe_fps(vn)
P=np.load(ip);N=np.load(inew);PF=P['frame'].astype(np.int16);NF=N['frame'].astype(np.int16)
PB=(P['text']<140);NB=(N['text']<140)   # 글자 마스크(355x16) — 비교 = 1-IoU ×100
def bd(x,y):
    u=(x|y).sum(); return 0.0 if u==0 else 100.0*(1-(x&y).sum()/u)
def load_segs(path):
    S=json.load(open(path));bar=np.array(S['bar']);dark=np.array(S['dark']);ch=set(S['changes']);n=len(bar)
    txt=(bar>.4)&(dark>=200); segs=[];i=0
    while i<n:
        if not txt[i]: i+=1;continue
        j=i+1
        while j<n and txt[j] and j not in ch: j+=1
        if j-i>=4: segs.append((i,j))
        i=j
    return segs,txt
segs,txt=load_segs(sn)
psegs,ptxt=load_segs(sp)   # 11/12: 직전 후보 쪽 자막 구간도 본다(새판에서 통째로 사라진 자막)
def ts(f): t=f/FPS; return f'{int(t//60)}:{t%60:05.2f}'
rows=[]
for a,b in segs:
    m=(a+b)//2
    if search==0: pm=m
    else:
        lo,hi=max(0,m-search),min(len(PF),m+search); d=np.abs(PF[lo:hi]-NF[m]).mean(1)+1e-4*np.abs(np.arange(lo,hi)-m); pm=lo+int(d.argmin())   # 11/12: 화면이 멈춘 구간은 똑같은 프레임이 여럿 → 같은 값이면 제자리에 가까운 쪽
    if pm>=len(PB): continue
    # 구간 안 여러 점(시작+3f, 중간, 끝-3f) 모두 비교해 최대 바차
    pts=[a+3,m,b-4]; dd=[]
    for q in pts:
        pq=pm+(q-m)
        if 0<=pq<len(PB): dd.append(bd(PB[pq],NB[q]))
    md=max(dd) if dd else 0
    if md>=35: rows.append((a,b,pm,md))   # 글자 마스크 불일치 35%↑ (같은 글자 ±1f 흔들림은 <15)
# 11/12 거꾸로 한 번 더: 직전 후보의 자막 구간 → 새 후보 짝 프레임에 글자 자막이 없으면 「사라짐」.
# (위 고리는 새 후보에 글자가 있는 구간만 돌아서, 자막이 통째로 빠진 곳은 비교 대상에도 안 들어가 0건으로 나왔다.)
gone=[]
for a,b in psegs:
    m=(a+b)//2
    if search==0: nm=m
    else:
        lo,hi=max(0,m-search),min(len(NF),m+search)
        if hi<=lo or m>=len(PF): nm=None
        else: d=np.abs(NF[lo:hi]-PF[m]).mean(1)+1e-4*np.abs(np.arange(lo,hi)-m); nm=lo+int(d.argmin())
    if nm is None or nm>=len(NB) or m>=len(PB):
        gone.append((a,b,None,100.0)); continue          # 새 후보가 더 짧아 짝 프레임이 없다
    pts=[q for q in (a+3,m,b-4) if 0<=nm+(q-m)<len(NB) and q<len(PB)]
    md=max((bd(PB[q],NB[nm+(q-m)]) for q in pts),default=0)
    # 글자 마스크가 35%↑ 다르고, 위 고리가 이미 적은 구간(직전 짝 프레임이 이 구간 안)이 아니면 적는다.
    # 화면이 멈춘 강의 슬라이드에선 짝 프레임이 옆 자막으로 잡힐 수 있어 「없음」뿐 아니라 「다름」도 여기서 잡는다.
    if md>=35 and not any(a<=r[2]<b for r in rows):
        gone.append((a,b,nm,md))
print('자막 구간',len(segs),'글자/유무 다른 구간',len(rows),'· 직전 후보 자막 구간',len(psegs),'중 새 후보에 그 글자가 없는 구간',len(gone))
os.makedirs('fr',exist_ok=True)   # 11/12: 단독으로 돌리면 fr/ 가 없어 증거 그림에서 멈추던 것
font=ImageFont.truetype('/System/Library/Fonts/AppleSDGothicNeo.ttc',20)
def crop(v,f):
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{f/FPS:.4f}','-i',v,'-frames:v','1','fr/cd.png']); return Image.open('fr/cd.png').convert('RGB').crop((150,925,1770,1030)).resize((900,58))
L=[f'# 자막 글자 대조 {os.path.basename(vp)} → {os.path.basename(vn)}','',f'새 후보 자막 구간 {len(segs)} 중 글자가 다른 구간 {len(rows)} (글자 마스크 불일치 ≥35%)','','|새 구간|직전 짝 프레임|바차|','|---|---|---|']
sheet=[]
for a,b,pm,md in rows:
    L.append(f'|{ts(a)}~{ts(b)} f{a}-{b}|f{pm} ({ts(pm)})|{md:.0f}|')
    m=(a+b)//2; row=Image.new('RGB',(1840,150),'white'); d=ImageDraw.Draw(row)
    d.text((8,2),f'새 {ts(a)}~{ts(b)} f{a}-{b} (바차 {md:.0f})  왼쪽=직전 f{pm} / 오른쪽=새 f{m}',fill='black',font=font)
    for i,(v,f) in enumerate(((vp,pm-(m-a)+3),(vn,a+3))): row.paste(crop(v,f),(10+i*920,28))
    for i,(v,f) in enumerate(((vp,pm+(b-4-m)),(vn,b-4))): row.paste(crop(v,f),(10+i*920,90))
    sheet.append(row)
if gone:
    L+=['',f'## 새 후보에서 사라졌거나 달라진 자막 {len(gone)} (직전 후보의 자막 구간 기준 — 새 후보 짝 프레임에 그 글자가 없음)','','|직전 구간|새 짝 프레임|','|---|---|']
    for a,b,nm,md in gone:
        L.append(f'|{ts(a)}~{ts(b)} f{a}-{b}|'+(f'f{nm} ({ts(nm)})|' if nm is not None else '짝 없음(새 후보가 짧음)|'))
        if nm is None: continue
        m=(a+b)//2; row=Image.new('RGB',(1840,150),'#fff0f0'); d=ImageDraw.Draw(row)
        d.text((8,2),f'새 후보에 없음: 직전 {ts(a)}~{ts(b)} f{a}-{b}  왼쪽=직전 f{m} / 오른쪽=새 f{nm}',fill='black',font=font)
        for i,(v,f) in enumerate(((vp,m),(vn,nm))): row.paste(crop(v,f),(10+i*920,28))
        sheet.append(row)
if sheet:
    Sh=Image.new('RGB',(1840,150*len(sheet)),'white')
    for j,r in enumerate(sheet): Sh.paste(r,(0,150*j))
    Sh.save(outp+'.jpg',quality=85)
open(outp+'.md','w').write('\n'.join(L)); print('\n'.join(L[4:]))
