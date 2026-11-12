import sys, subprocess, numpy as np, mlx_whisper
f=sys.argv[1]
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a,b): return mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
for t in map(float, sys.argv[2:]): print(t, "앞:", tr(max(0,t-1.5), t), "| 뒤:", tr(t, t+1.2), flush=True)
