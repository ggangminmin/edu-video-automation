import mlx_whisper, json, numpy as np, subprocess
def load(p, a=0, b=None):
    x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
    return x[int(a*16000): int(b*16000) if b else None]
R = {}
for k, x in (("new_raw", load("new_raw.wav")), ("old_v090_55.4-63.2", load("../v090.wav", 55.4, 63.2))):
    r = mlx_whisper.transcribe(x, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False, word_timestamps=True)
    R[k] = dict(text=r["text"].strip(), words=[(w["word"], round(w["start"],3), round(w["end"],3)) for s in r["segments"] for w in s["words"]])
    print(k, "→", R[k]["text"]); print(R[k]["words"])
json.dump(R, open("asr_new.json","w"), ensure_ascii=False, indent=1)
