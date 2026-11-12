# 🔒지금_규칙 23: 표지 인삿말 소리 = 강의인삿말/0.9배/인삿말_NN강_090.wav (이미 0.9배 — 48k 스테레오로만) + mlx 단어 받아쓰기
import subprocess, json, os, unicodedata as u, mlx_whisper
from lec import N
GD = "../../../강의인삿말/0.9배"
f = [x for x in os.listdir(GD) if u.normalize("NFC", x).startswith(f"인삿말_{N:02d}강_090")][0]
print(u.normalize("NFC", f))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{GD}/{f}", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", "greet_tc_090.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "greet_tc_090.wav", "-ar", "16000", "-ac", "1", "greet_tc_090_16k.wav"], check=True)
d0 = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{GD}/{f}"]))
d1 = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "greet_tc_090.wav"]))
r = mlx_whisper.transcribe("greet_tc_090_16k.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
w = [[x["start"], x["end"], x["word"]] for s in r["segments"] for x in s.get("words", [])]
json.dump(dict(src=u.normalize("NFC", f), dur_src=d0, dur_090=d1, text=r["text"], words=w), open("greet_tc_words.json", "w"), ensure_ascii=False, indent=0)
print(f"원본 {d0:.3f} → 0.9배 {d1:.3f} (÷0.9={d0/0.9:.3f})"); print(r["text"])
