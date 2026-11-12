import sys,subprocess,numpy as np
f,t=sys.argv[1],float(sys.argv[2]); w,h=270,480
raw=subprocess.run(['ffmpeg','-v','error','-t',str(t),'-i',f,'-vf',f'scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.int16)
d=np.array([np.abs(a[i]-a[i-1]).mean() for i in range(1,len(a))])
print(f"frames={len(a)} zero_diff(<0.05)={int((d<0.05).sum())} min={d.min():.2f} max={d.max():.2f}@{(d.argmax()+1)/25:.2f}s median={np.median(d):.2f}")
