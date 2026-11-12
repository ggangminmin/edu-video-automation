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
    a,b=map(float,spec.split(":"));print(spec," ".join(f"{i/200:.3f}:{db[i]:.0f}" for i in range(int(a*200),int(b*200),2)))
