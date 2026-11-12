import mlx_whisper, json, sys
r = mlx_whisper.transcribe(sys.argv[1], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True)
w = [dict(w=x["word"], s=round(x["start"],3), e=round(x["end"],3)) for s in r["segments"] for x in s["words"]]
json.dump(dict(text=r["text"], words=w), open(sys.argv[2], "w"), ensure_ascii=False, indent=1); print(r["text"]); print(w)
