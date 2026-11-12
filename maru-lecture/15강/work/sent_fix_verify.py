import numpy as np, subprocess, re, mlx_whisper
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a,b): return re.sub(r"[^가-힣0-9]","",mlx_whisper.transcribe(x[int(a*16000):int(b*16000)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",condition_on_previous_text=False)["text"])
for t in (513.29, 514.393, 697.5, 698.659, 699.627, 700.76, 701.959):
    print(t, "| 앞:", tr(t-1.2, t)[-10:], "| 뒤:", tr(t, t+1.3)[:10], flush=True)
