import mlx_whisper, json, numpy as np, subprocess
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","../v090.wav","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
A=392.40
R={}
for k,(a,b) in {"full":(392.40,398.10)}.items():
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False, word_timestamps=True)
    R[k]=dict(text=r["text"].strip(), words=[(w["word"], round(a+w["start"],3), round(a+w["end"],3)) for s in r["segments"] for w in s["words"]]); print(k, R[k])
json.dump(R, open("asr_107.json","w"), ensure_ascii=False, indent=1)
