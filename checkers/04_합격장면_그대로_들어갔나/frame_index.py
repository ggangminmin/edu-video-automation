#!/usr/bin/env python3
"""frame_index.py <mp4> <out.npz> [--screen 화면설정.json] — 전 프레임 인덱스: 화면 48x27 회색 + 자막바 영역(화면 설정 subbar) 96x6 회색 + 글자 영역(text_area) (합격 클립 대조용, 읽기 전용).
화면 설정 필수(--screen 또는 QA_SCREEN). 국가데이터처 = 화면설정_예시_국가데이터처.json."""
import sys,subprocess,numpy as np
import os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'03_빈_자막바')); import screen_cfg
S=screen_cfg.load()
mp4,out=sys.argv[1:3]; W,H=48,27; BW,BH=96,6
def grab(vf,n):
    p=subprocess.Popen(['ffmpeg','-v','error','-i',mp4,'-map','0:v:0','-vf',vf,'-f','rawvideo','-'],stdout=subprocess.PIPE,bufsize=10**8)
    b=p.stdout.read(); m=len(b)//n; return np.frombuffer(b[:m*n],np.uint8).reshape(m,n)
F=grab(f'scale={W}:{H}:flags=area,format=gray',W*H); B=grab(screen_cfg.crop(S['subbar'])+f',scale={BW}:{BH}:flags=area,format=gray',BW*BH)
T=grab(screen_cfg.crop(S['text_area'])+',scale=355:16:flags=area,format=gray',355*16)   # 글자 영역(글자 대조용)
m=min(len(F),len(B),len(T)); np.savez(out,frame=F[:m],bar=B[:m],text=T[:m]); print('frames',m)
