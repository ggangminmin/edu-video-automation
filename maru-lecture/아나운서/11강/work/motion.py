import sys,subprocess,numpy as np
f,ss,t=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
w,h=270,480
raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(t),'-i',f,'-vf',f'scale={w}:{h},format=gray','-f','rawvideo','-'],capture_output=True).stdout
a=np.frombuffer(raw,np.uint8).reshape(-1,h,w).astype(np.int16)
d=[np.abs(a[i]-a[i-1]).mean() for i in range(1,len(a))]
out=[]
for i in range(0,len(d),5): out.append(f"{ss+(i+1)/25:.1f}:{np.mean(d[i:i+5]):.2f}")
print(' '.join(out))
