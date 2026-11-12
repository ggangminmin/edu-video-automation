# 0.9배 음성 → mlx-whisper 단어 시각 [[from,to,word],...] (11강 mlxwords.json 과 같은 형식)
import json, mlx_whisper
r = mlx_whisper.transcribe("v090_16k.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True)
w = [[x["start"], x["end"], x["word"]] for s in r["segments"] for x in s.get("words", [])]
json.dump(w, open("mlxwords.json", "w"), ensure_ascii=False)
print(len(w))
