import mlx_whisper, json, numpy as np, subprocess
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","../v090.wav","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
for a,b in ((392.40,395.20),(392.40,395.32),(395.20,398.10),(395.32,398.10)):
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    print(a,b,r["text"].strip())
