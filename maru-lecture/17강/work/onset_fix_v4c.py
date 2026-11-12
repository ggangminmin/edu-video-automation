# 17강 v4c: v4b 의 「줄나눔v4」 줄 시작을 실소리(음성만 재구성 · 10ms RMS)로 다시 잼 — cx v4b 반려(61·89 선행)
import json, numpy as np, subprocess as sp, sys
FPS=30000/1001; q=lambda t: round(t*FPS)/FPS
tl=json.load(open("../타임라인_v4b.json"))
SR=16000; N=int((tl["total"]+1)*SR); v=np.zeros(N,np.float32)
src={None:"v090.wav"}
for a in tl["audio"]:
    f=a.get("src") or "work/v090.wav"; f=f.replace("work/","")
    x=np.frombuffer(sp.run(["ffmpeg","-v","error","-i",f,"-ss",str(a["src_from"]),"-to",str(a["src_to"]),"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)*a.get("gain",1.0)
    i=int(a["out"]*SR); v[i:i+len(x)]+=x[:N-i]
db=20*np.log10(np.sqrt(np.mean(v[:N//160*160].reshape(-1,160)**2,1))+1e-9)
TH=-40
def onset(st, prev_st):
    # st 근처: [st-0.3, st+1.2] 안 가장 늦게 끝나는 쉼(≥0.10s) 중 st+1.0 전에 끝나는 것 → 그 끝 = 말 시작. 쉼 없으면 None
    a=int((st-0.3)*100); b=int((st+1.2)*100); runs=[]; r0=None
    for i in range(a,b):
        if db[i]<TH:
            if r0 is None: r0=i
        else:
            if r0 is not None and i-r0>=10: runs.append((r0,i))
            r0=None
    runs=[r for r in runs if r[1]/100<=st+1.0 and r[0]/100>prev_st+0.3]
    return runs[-1][1]/100 if runs else None
MAN={73:273.35,123:469.00}   # 쉼 0.08초·짧은 골(−49dB 1칸)이라 자동이 못 잡은 곳 — 10ms RMS 눈으로 잼(73 「사용자가」 ㅅ 시작 · 123 「가져오지」 ㄱ 파열 뒤)
out=[]; rep=[]
S=tl["subs"]
for k,s in enumerate(S):
    y=dict(s)
    if s.get("how","").startswith("줄나눔"):
        on=MAN.get(s["n"]) or onset(s["start"]+0.09, S[k-1]["start"])
        if on is not None:
            ns=q(on-0.09)
            rep.append((s["n"],round(s["start"],3),round(on,3),round(s["start"]+0.09-on,3),s["text"][:20]))
            if abs(ns-s["start"])>0.5/FPS:
                y["start"]=ns; y["voice_on"]=round(on,3); y["how"]="줄나눔v4c(실소리 RMS −0.09)"
                out[-1]["end"]=ns
        else: rep.append((s["n"],round(s["start"],3),None,None,s["text"][:20]))
    out.append(y)
for r in rep: print(r)
t2=dict(tl); t2["subs"]=out; t2["params"]=dict(tl["params"]); t2["params"]["v4c"]="cx v4b 반려 61·89 선행 → 줄나눔 줄 시작 = 음성만 재구성 RMS(−40dB, 쉼 ≥0.1초) 끝 −0.09"
for a,b in zip(out,out[1:]): assert b["start"]>a["start"]+0.3
json.dump(t2,open("../타임라인_v4c.json","w"),ensure_ascii=False,indent=1)
np.save("voice_v4c_db.npy",db)
