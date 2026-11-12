# v2 ↔ v3 화면 차이: 5초마다 표본 · 바뀐 카드 묶음 창(±0.1초) 밖만 · RGB 평균 절대차 /255
import json, subprocess, numpy as np
a=json.load(open('../타임라인_v2.json'))['subs']; b=json.load(open('../타임라인_v3.json'))['subs']
ka={(round(x['start'],3),x['text']) for x in a}; kb={(round(x['start'],3),x['text']) for x in b}
win=[(x['start']-0.1,x['end']+0.1) for x in a if (round(x['start'],3),x['text']) not in kb]+[(x['start']-0.1,x['end']+0.1) for x in b if (round(x['start'],3),x['text']) not in ka]
def grab(f,t): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.3f}","-i",f,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout,np.uint8).astype(np.int16)
res=[]
for t in np.arange(2.5,920,5.0):
    if any(s<=t<=e for s,e in win): continue
    d=np.abs(grab('../07강_v2.mp4',t)-grab('../07강_v3.mp4',t)).mean(); res.append((round(float(t),1),round(float(d),4)))
mx=max(res,key=lambda r:r[1]); print("표본",len(res),"최대",mx,"0.1 넘는",[r for r in res if r[1]>=0.1])
json.dump(res,open('v3/fd/framediff.json','w'))
