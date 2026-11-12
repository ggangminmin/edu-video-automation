# 새 소리(인삿말·끝인사) 단어 시각 받아쓰기 → JSON (자막 시각·문장 대조용)
import sys, json, re, mlx_whisper
for p in sys.argv[1:]:
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
    W = [(w["word"].strip(), round(w["start"], 3), round(w["end"], 3)) for s in r["segments"] for w in s["words"]]
    json.dump(dict(text=r["text"], words=W), open(p.replace(".wav", "_words.json"), "w"), ensure_ascii=False, indent=0)
    print(p, r["text"])
