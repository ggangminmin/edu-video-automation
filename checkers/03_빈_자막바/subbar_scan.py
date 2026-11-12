#!/usr/bin/env python3
"""subbar_scan.py <mp4> <out.json> [--screen 화면설정.json] — 자막바 전 프레임 글자 영역 변화 검출(읽기 전용).
자막바 위치 · 색 = 화면 설정(subbar · text_area · bar_fill · border · border_line · text_dark_max). 설정이 없으면 멈춤(QA_SCREEN 도 읽음).
글자 안쪽(text_area)만 회색 1/2 축소 → 연속 프레임 평균차. 변화 프레임 = 하드컷 후보. 바 존재 = 바 채움색 비율.
(10/19 전: 국가데이터처 숫자 191,933 1538x91 · #EAEAEA · #2A7170 이 박혀 있었음 → 화면설정_예시_국가데이터처.json)"""
import sys,json,subprocess,numpy as np
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'03_빈_자막바')); import screen_cfg
S=screen_cfg.load()
mp4,out=sys.argv[1:3]; fps=S['fps']
ta=S['text_area']; x,y,w,h=ta['x'],ta['y'],ta['w'],ta['h']; W,H=w//2,h//2
sb=S['subbar']; bl=S['border_line']; BW=max(1,bl['w']//10)
FILL=np.array(screen_cfg.rgb(S['bar_fill'])); FT=S['bar_fill_tol']; TEAL=np.array(screen_cfg.rgb(S['border'])); TT=S['border_tol']; DK=S['text_dark_max']
p=subprocess.Popen(['ffmpeg','-v','error','-i',mp4,'-map','0:v:0','-vf',f'crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=area,format=gray','-f','rawvideo','-'],stdout=subprocess.PIPE,bufsize=10**8)
q=subprocess.Popen(['ffmpeg','-v','error','-i',mp4,'-map','0:v:0','-vf',screen_cfg.crop(sb)+',scale=192:12:flags=area,format=rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,bufsize=10**8)
r=subprocess.Popen(['ffmpeg','-v','error','-i',mp4,'-map','0:v:0','-vf',screen_cfg.crop(bl)+f',scale={BW}:1:flags=area,format=rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,bufsize=10**8)
prev=None;D=[];BAR=[];DARK=[];BORDER=[]
while True:
    b=p.stdout.read(W*H); c=q.stdout.read(192*12*3); e=r.stdout.read(BW*3)
    if len(b)<W*H: break
    f=np.frombuffer(b,np.uint8).astype(np.int16); g=np.frombuffer(c,np.uint8).reshape(-1,3).astype(int)
    bar=float((np.abs(g-FILL).max(1)<FT).mean()); BAR.append(round(bar,3))
    DARK.append(int((f<DK).sum()))   # 글자(어두운) 화소 수
    t=np.frombuffer(e,np.uint8).reshape(-1,3).astype(int); BORDER.append(round(float((np.abs(t-TEAL).max(1)<TT).mean()),2))   # 바 위 테두리(border) 비율
    D.append(0.0 if prev is None else float(np.abs(f-prev).mean())); prev=f
D=np.array(D); ch=[]
for i in range(1,len(D)):
    if D[i]>2.0 and D[i]>=D[max(0,i-1)] and D[i]>=D[min(len(D)-1,i+1)]: ch.append(i)
json.dump({'fps':fps,'n':len(D),'diff':[round(v,2) for v in D.tolist()],'bar':BAR,'dark':DARK,'border':BORDER,'changes':ch},open(out,'w'))
print('frames',len(D),'changes',len(ch))
