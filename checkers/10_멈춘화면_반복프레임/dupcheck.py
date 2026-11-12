#!/usr/bin/env python3
"""dupcheck.py mp4 face=x,y,w,h — 반복(정지) 프레임 위치와 그 앞뒤 얼굴 움직임. 출력: 반복 프레임 수·간격·움직임 중 반복 비율"""
import sys,subprocess,numpy as np

def _probe_fps(path, fallback=24000/1001):
    """영상의 실제 프레임 속도(ffprobe). 못 읽으면 fallback. (10/19: 23.976 이 박혀 있던 것을 프로젝트마다 읽게)"""
    try:
        out = subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=r_frame_rate','-of','csv=p=0',path],capture_output=True,text=True).stdout.strip()
        a,b = out.split('/'); return float(a)/float(b)
    except Exception:
        return fallback
mp4=sys.argv[1];x,y,w,h=map(int,sys.argv[2].split(','))
raw=subprocess.run(['ffmpeg','-v','error','-i',mp4,'-vf','scale=480:270,format=gray','-f','rawvideo','-'],capture_output=True).stdout
f=np.frombuffer(raw,np.uint8).reshape(-1,270,480).astype(np.int16)
fx,fy,fw,fh=x//4,y//4,w//4,h//4
full=np.abs(np.diff(f,axis=0)).mean(axis=(1,2))
face=np.abs(np.diff(f[:,fy:fy+fh,fx:fx+fw],axis=0)).mean(axis=(1,2))
fps=_probe_fps(mp4)
dups=[i+1 for i,v in enumerate(full) if v<0.02]   # frame i+1 == frame i
mov=np.median(face[face>0.02]) if (face>0.02).any() else 0
print(f'{mp4.split("/")[-1]} frames {len(f)} dup {len(dups)} face_med_motion {mov:.2f}')
gaps=np.diff(dups) if len(dups)>1 else []
if len(gaps): print(' gap frames: med',int(np.median(gaps)),'min',int(min(gaps)),'max',int(max(gaps)))
bad=[]
for d in dups:
    a=face[d-2] if d-2>=0 else 0; b=face[d] if d<len(face) else 0
    if min(a,b)>0.6*mov and mov>0: bad.append((d,round(d/fps,2),round(a,2),round(b,2)))
print(' dup amid face motion (both sides ≥0.6×median):',len(bad))
print(' ',bad[:40])
