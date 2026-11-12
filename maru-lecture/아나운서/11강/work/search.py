import numpy as np, subprocess, json, re, sys
sys.path.insert(0,sys.argv[1]); from pose import frames, measure
W=sys.argv[1]
def sil(f):
    o=subprocess.run(['ffmpeg','-i',f,'-af','silencedetect=n=-40dB:d=0.5','-f','null','-'],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r'silence_start: ([0-9.]+)',o)]; e=[float(x) for x in re.findall(r'silence_end: ([0-9.]+)',o)]
    return list(zip(s,e))
def thumb(fr): return fr[::8,::8].mean(2)
src={'greet':'_작업/인삿말/홀수_인삿말_수정.mp4','bye':'_작업/인삿말/홀수_끝인사.mp4'}
tg={'open0':frames('_작업/시연/hg_raw.mp4',0,0.04)[0],'close0':frames('_작업/아나운서/hg11_close.mp4',0,0.04)[0],'greetEnd':frames(src['greet'],86.56,0.04)[0]}
T={k:(measure(v),thumb(v)) for k,v in tg.items()}
res=[]
for k,f in src.items():
    for s,e in sil(f):
        s2,e2=s+0.08,e-0.08
        if e2-s2<0.6: continue
        fr=frames(f,s2,e2-s2)
        for i,x in enumerate(fr):
            p=measure(x); th=thumb(x)
            row=dict(src=k,t=round(s2+i/25,2),win=[round(s,2),round(e,2)],**p)
            for n,(tp,tt) in T.items(): row['d_'+n]=round(float(np.abs(th-tt).mean()),2)
            res.append(row)
json.dump(res,open(W+'/silent_poses.json','w'),ensure_ascii=False)
for n in T:
    best=sorted(res,key=lambda r:r['d_'+n])[:5]
    print(n,T[n][0]); [print('  ',r) for r in best]
