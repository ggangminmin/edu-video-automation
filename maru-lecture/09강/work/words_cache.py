# <wav>_words.json 캐시 만들기(오더09_공용/lipcheck2.py 와 같은 형식 [단어, 시작, 끝]) — heavy_run asr 로
import sys, json, mlx_whisper
for p in sys.argv[1:]:
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
    json.dump(dict(text=r["text"], words=[(w["word"].strip(), round(w["start"], 3), round(w["end"], 3)) for s in r["segments"] for w in s["words"]]),
              open(p.replace(".wav", "_words.json"), "w"), ensure_ascii=False, indent=0)
    print(p, r["text"])
