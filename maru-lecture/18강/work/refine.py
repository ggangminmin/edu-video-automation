import json,numpy as np,subprocess,re
sr=16000
x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(float)/32768
hop=80; win=320
n=len(x)//hop
rms=np.array([np.sqrt(np.mean(x[i*hop:i*hop+win]**2)+1e-12) for i in range(n)])
db=20*np.log10(rms+1e-9)
np.save("rmsdb.npy",db)
