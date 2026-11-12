import numpy as np, subprocess, re, mlx_whisper
def X(k): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f"a_{k}.wav","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(x,a,b): return re.sub(r"[^가-힣0-9]","",mlx_whisper.transcribe(x[int(a*16000):int(b*16000)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)["text"])
g,b=X("인삿말"),X("끝인사")
for nm,x,a,c in (("g",g,11.0,12.06),("g",g,12.06,13.0),("g",g,4.3,5.30),("g",g,5.33,6.2),("b",b,12.4,13.41),("b",b,13.41,14.3),("b",b,12.4,13.63),("b",b,13.63,14.6)):
    print(nm,a,c,tr(x,a,c),flush=True)
d=g; h=80; db=[20*np.log10(np.sqrt(np.mean(d[i*h:i*h+320]**2))+1e-9) for i in range(int(12.06/0.005),int(12.4/0.005))]
print(" ".join(f"{12.06+j*0.005:.3f}:{v:.0f}" for j,v in enumerate(db) if j%3==0))
