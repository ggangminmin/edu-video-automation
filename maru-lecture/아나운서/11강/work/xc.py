import sys,subprocess,numpy as np
def env(f):
    raw=subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    x=np.frombuffer(raw,np.int16).astype(float); hop=80  # 5ms
    e=np.sqrt(np.add.reduceat(x**2,np.arange(0,len(x),hop))/hop); return np.log1p(e)
a,b=env(sys.argv[1]),env(sys.argv[2])  # a=clip, b=reference
a=(a-a.mean())/a.std(); b=(b-b.mean())/b.std()
c=np.correlate(np.pad(a,(0,len(b))),b,'valid') if False else np.correlate(np.concatenate([a,np.zeros(len(b))]),b,'valid')
lag=int(np.argmax(c)); n=min(len(b),len(a)-lag)
r=np.corrcoef(a[lag:lag+n],b[:n])[0,1]
print(f"ref offset in clip = {lag*0.005:.3f}s  corr={r:.3f}")
