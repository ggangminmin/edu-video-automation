import sys, json, numpy as np, subprocess, mlx_whisper, re
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
o = subprocess.run(["ffmpeg","-i","v090_16k.wav","-af","silencedetect=n=-40dB:d=0.05","-f","null","-"],capture_output=True,text=True).stderr
S = list(zip([float(v) for v in re.findall(r"silence_start: ([\d.]+)",o)],[float(v) for v in re.findall(r"silence_end: ([\d.]+)",o)]))
over = json.load(open("onset_override.json"))
for t in map(float, sys.argv[1:]):
    a = t - 1.6
    r = mlx_whisper.transcribe(x[int(a*16000):int((t+1.6)*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
    ws = " ".join(f"{w['word'].strip()}@{a+w['start']:.2f}" for s in r["segments"] for w in s["words"])
    sil = [(round(s0,2),round(e0,2)) for s0,e0 in S if t-1.6 < e0 < t+1.6]
    print(f"{t}: {ws}\n   무음 {sil}")
