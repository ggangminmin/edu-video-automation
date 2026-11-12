# 오더21/chk_piece/*.wav 받아쓰기 → 오더21/chk_piece/asr.json   (heavy_run.sh asr 로 실행)
import glob, json, mlx_whisper
out = {}
for p in sorted(glob.glob("오더21/chk_piece/*.wav")):
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    out[p.split("/")[-1][:-4]] = r["text"].strip()
json.dump(out, open("오더21/chk_piece/asr.json", "w"), ensure_ascii=False, indent=1); print(len(out))
