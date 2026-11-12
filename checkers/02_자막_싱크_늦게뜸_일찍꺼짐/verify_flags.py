#!/usr/bin/env python3
"""verify_flags.py <master.mp4> <capsync.json> <whisper.json> <out_prefix> [--screen 화면설정.json] — capsync 판정 항목을 프레임·DTW 로 2차 검증(읽기 전용).
 화면 설정(fps · border · border_check · sheet_crop) 필수(--screen 또는 QA_SCREEN). 없으면 멈춤.
 EMPTY: 바 테두리(border 색 가로선 border_check 위 · 아래 띠) 실제 존재 여부 → 테두리 없으면 「흰 바닥 오검출」로 기각
 MIDON/LATE: 교체 시각 ↔ 뒤 자막 첫 단어 DTW 시각(토큰 나열) · MIDOFF: 꺼짐 시각 뒤 스템 dB
 시트: 판정마다 전체 프레임 + 바 크롭 3장(−3f, 0, +3f)"""
import sys,json,os,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFont
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'03_빈_자막바')); import screen_cfg
SC=screen_cfg.load(); BC=SC['border_check']; TEAL=np.array(screen_cfg.rgb(SC['border'])); TT=SC['border_tol']; CROP=tuple(SC['sheet_crop'])
V,cj,wj,outp=sys.argv[1:5]; FPS=SC['fps']
J=json.load(open(cj)); W=json.load(open(wj))['transcription']
tok=[]
for s in W:
    for t in s.get('tokens',[]):
        if t['text'].startswith('[') or t['text'].startswith('<|'): continue
        tok.append((t['t_dtw']*0.01-0.12 if t.get('t_dtw',-1)>=0 else s['offsets']['from']/1000,t['text']))
tok.sort()
def ts(t): return f'{int(t//60)}:{t%60:05.2f}'
os.makedirs('fr',exist_ok=True)
def frame(f):
    p=f'fr/{os.path.basename(V)[:12]}_{f}.png'
    if not os.path.exists(p): subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{f/FPS:.4f}','-i',V,'-frames:v','1',p])
    return Image.open(p).convert('RGB')
def border(im):
    a=np.asarray(im).astype(int)
    top=a[BC['top_y0']:BC['top_y1'],BC['x0']:BC['x1']]; bot=a[BC['bot_y0']:BC['bot_y1'],BC['x0']:BC['x1']]
    def teal(px): return float(((np.abs(px-TEAL).max(2))<TT).mean())
    return teal(top),teal(bot)
font=ImageFont.truetype('/System/Library/Fonts/AppleSDGothicNeo.ttc',22)
rows=[];L=[f'# 2차 검증 — {os.path.basename(V)}','','|항목|시각|판정 근거|결론|','|---|---|---|---|']
items=[]
for r in J['segs']:
    if not r['flags'] or 'linger' in r['flags'][0]: continue
    fl=r['flags'][0]; f=r['f1'] if 'MIDOFF' in fl else r['f0']; t=f/FPS
    near=' '.join(f'{x}({a-t:+.2f})' for a,x in tok if t-0.8<=a<=t+0.6)
    items.append((f'#{r["k"]} {ts(t)} f{f} {fl}',f,near,'DTW 단어↔교체 시각 보고 판단'))
for e in J['empty']:
    if e['f0']==0: continue
    m=(e['f0']+e['f1'])//2; tb=border(frame(m))
    concl='❌ 빈 바 (테두리 있음)' if min(tb)>0.5 else '기각: 바 테두리 없음(흰 바닥 오검출)'
    items.append((f'EMPTY {ts(e["t0"])}~{ts(e["t1"])} f{e["f0"]}-{e["f1"]} ({e["frames"]}f)',m,f'테두리 위 {tb[0]:.0%} 아래 {tb[1]:.0%}',concl))
for title,f,ev,concl in items:
    L.append(f'|{title}|{ts(f/FPS)}|{ev[:160]}|{concl}|')
    row=Image.new('RGB',(1920,330),'white'); d=ImageDraw.Draw(row)
    d.text((8,4),f'{title}  → {concl}',fill='black',font=font); d.text((8,300),ev[:150],fill=(60,60,60),font=font)
    row.paste(frame(f).resize((480,270)),(8,30))
    for i,ff in enumerate((f-3,f,f+3)):
        row.paste(frame(max(0,ff)).crop(CROP).resize((1400,91)),(500,32+i*88)); d.text((1780,32+i*88+60),f'f{ff}',fill='red',font=font)
    rows.append(row)
for i in range(0,len(rows),10):
    S=Image.new('RGB',(1920,330*min(10,len(rows)-i)),'white')
    for j,r in enumerate(rows[i:i+10]): S.paste(r,(0,330*j))
    S.save(f'{outp}_{i//10}.jpg',quality=85)
open(outp+'.md','w').write('\n'.join(L)); print('\n'.join(L))
