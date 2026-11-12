import sys, json, mlx_whisper
src, out = sys.argv[1], sys.argv[2]
r = mlx_whisper.transcribe(src, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
w = [(x["start"], x["end"], x["word"]) for s in r["segments"] for x in s.get("words", [])]
json.dump(dict(text=r["text"], words=w, segs=[(s["start"], s["end"], s["text"]) for s in r["segments"]]), open(out, "w"), ensure_ascii=False)
print("ok", len(w))
