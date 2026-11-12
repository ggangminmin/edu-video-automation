# 깨끗한 음성(타임라인 audio 대로) 5ms RMS — 창 안 무음 구간(−50dB 밑 ≥25ms)과 골짜기(−45 밑 국소 최소)
import sys,json,subprocess,numpy as np
tl=json.load(open(sys.argv[1]));SR=16000
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32)
c={};V=np.zeros(int((tl["total"]+1)*SR),np.float32)
for s in tl["audio"]:
    k=s.get("src");f="v090.wav" if k is None else k.replace("work/","")
    if f not in c:c[f]=load(f)
    y=c[f][int(s["src_from"]*SR):int(s["src_to"]*SR)]*float(s.get("gain",1.0));o=int(round(s["out"]*SR));V[o:o+len(y)]+=y[:max(0,len(V)-o)]
H=80;db=20*np.log10(np.sqrt(np.mean(V[:len(V)//H*H].reshape(-1,H)**2,1))+1e-9)
for spec in sys.argv[2:]:
    a,b=map(float,spec.split(":"));i0,i1=int(a*200),int(b*200);runs=[];j=i0
    while j<i1:
        if db[j]<-50:
            k=j
            while k<i1 and db[k]<-50:k+=1
            if k-j>=5: runs.append(f"{j/200:.3f}~{k/200:.3f}({(k-j)*5}ms min{db[j:k].min():.0f})")
            j=k
        else:j+=1
    vs=[f"{m/200:.3f}:{db[m]:.0f}" for m in range(i0+3,i1-3) if db[m]<=-45 and db[m]==db[m-3:m+4].min() and db[m]>=-50]
    print(f"[{a},{b}] 무음:",", ".join(runs) or "없음"," | 골짜기:",", ".join(vs) or "없음")
    if "-v" in sys.argv[0:1] or True:
        print("   ", " ".join(f"{i/200:.3f}:{db[i]:.0f}" for i in range(i0,i1,4)))
