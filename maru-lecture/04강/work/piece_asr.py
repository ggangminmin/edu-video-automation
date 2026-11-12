import sys, json, subprocess, numpy as np, mlx_whisper
x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
for ab in sys.argv[1:]:
    a,b=map(float,ab.split(":")); r=mlx_whisper.transcribe(x[int(a*16000):int(b*16000)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)
    print(ab, r["text"])
