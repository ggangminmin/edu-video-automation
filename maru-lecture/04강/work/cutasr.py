# 받아쓰기 자르기: 인자 = 시각들(v090 초) → [t-1.2,t] / [t,t+1.3]
import sys, subprocess, numpy as np, mlx_whisper
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a,b): return mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
for t in map(float, sys.argv[1:]): print(t, "앞:", tr(t-1.2, t), "| 뒤:", tr(t, t+1.3), flush=True)
