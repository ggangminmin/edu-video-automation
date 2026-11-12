# 인삿말·끝인사 클립 줄 시작 후보를 짧은 구간 받아쓰기로 확인: [t, t+1.3] 이 그 줄 첫 말로 시작 · [t-1, t] 에 없음
import numpy as np, subprocess, re, mlx_whisper
def tr(x, a, b):
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
C = {"인삿말": [1.207, 2.373, 5.30, 5.38, 5.655, 8.554, 12.0, 12.2, 12.35],
     "끝인사": [1.214, 5.486, 8.951, 13.54, 13.928]}
for k, ts in C.items():
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"a_{k}.wav", "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(np.float32) / 32768
    for t in ts: print(k, t, "| 뒤:", tr(x, t, t + 1.3)[:10], "| 앞:", tr(x, max(0, t - 1.0), t)[-8:], flush=True)
