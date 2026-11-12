# 짧은 구간 받아쓰기: python cutasr.py <wav> a:b [a:b ...]
import sys, subprocess, numpy as np, mlx_whisper
f = sys.argv[1]
y = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout,np.float32)
for ab in sys.argv[2:]:
    a, b = map(float, ab.split(":"))
    print(ab, mlx_whisper.transcribe(y[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"], flush=True)
