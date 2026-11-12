import mlx_whisper, sys
for f in sys.argv[1:]:
    r = mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    print(f, [ (round(s["start"],2), s["text"]) for s in r["segments"]])
