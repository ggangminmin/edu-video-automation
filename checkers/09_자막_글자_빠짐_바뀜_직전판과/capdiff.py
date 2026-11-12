#!/usr/bin/env python3
"""capdiff.py <idx_prev.npz> <idx_new.npz> <subbar_prev.json> <subbar_new.json> <prev.mp4> <new.mp4> <out_prefix> [search]
직전 후보 ↔ 새 후보 자막 글자 대조(읽기 전용). 같은 시계면 search=0, 다르면 ±search 프레임 안에서 화면(48x27)으로 짝 프레임을 찾는다.
새 후보의 글자 자막 구간마다 중간 프레임의 바 영역(96x6)을 직전 후보 짝 프레임과 비교 → 바차 ≥10 = 글자 다름/유무 다름 → 목록 + 나란히 시트."""
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
S=json.load(open(sn));bar=np.array(S['bar']);dark=np.array(S['dark']);border=np.array(S.get('border',[1]*len(bar)));ch=set(S['changes']);n=len(bar)
txt=(bar>.4)&(dark>=200)
segs=[];i=0
while i<n:
    if not txt[i]: i+=1;continue
    j=i+1
    while j<n and txt[j] and j not in ch: j+=1
    if j-i>=4: segs.append((i,j))
    i=j
def ts(f): t=f/FPS; return f'{int(t//60)}:{t%60:05.2f}'
rows=[]
for a,b in segs:
    m=(a+b)//2
    if search==0: pm=m
    else:
        lo,hi=max(0,m-search),min(len(PF),m+search); d=np.abs(PF[lo:hi]-NF[m]).mean(1); pm=lo+int(d.argmin())
    if pm>=len(PB): continue
    # 구간 안 여러 점(시작+3f, 중간, 끝-3f) 모두 비교해 최대 바차
    pts=[a+3,m,b-4]; dd=[]
    for q in pts:
        pq=pm+(q-m)
        if 0<=pq<len(PB): dd.append(bd(PB[pq],NB[q]))
    md=max(dd) if dd else 0
    if md>=35: rows.append((a,b,pm,md))   # 글자 마스크 불일치 35%↑ (같은 글자 ±1f 흔들림은 <15)
print('자막 구간',len(segs),'글자/유무 다른 구간',len(rows))
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
if sheet:
    Sh=Image.new('RGB',(1840,150*len(sheet)),'white')
    for j,r in enumerate(sheet): Sh.paste(r,(0,150*j))
    Sh.save(outp+'.jpg',quality=85)
open(outp+'.md','w').write('\n'.join(L)); print('\n'.join(L[4:]))
