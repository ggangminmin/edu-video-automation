import mlx_whisper, json
r = mlx_whisper.transcribe("v090_16k.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
w = [[x["start"], x["end"], x["word"]] for s in r["segments"] for x in s.get("words", [])]
json.dump(w, open("mlxwords.json", "w"), ensure_ascii=False)
json.dump(r["text"], open("mlxtext.json", "w"), ensure_ascii=False)
print("words", len(w))
