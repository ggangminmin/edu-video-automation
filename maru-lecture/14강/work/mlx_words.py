import mlx_whisper, json
r = mlx_whisper.transcribe("v090_16k.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
out = [[w["start"], w["end"], w["word"]] for s in r["segments"] for w in s.get("words", [])]
json.dump(out, open("mlxwords.json", "w"), ensure_ascii=False)
json.dump([[s["start"], s["end"], s["text"]] for s in r["segments"]], open("mlxsegs.json", "w"), ensure_ascii=False)
print("words", len(out))
