# 오더52 받아쓰기 근거: 깨끗한 v7 음성 앞/뒤 창(규칙 24) + mp4 바뀐 구간 앞뒤 2초
import numpy as np, subprocess, mlx_whisper, json
SR = 48000; c = np.load("09강/work/v7/clean_v7.npy")
mp = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","09강/09강_v7.mp4","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
def t(seg16): return mlx_whisper.transcribe(seg16, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
def cw(a, b): s = c[int(a*SR):int(b*SR)]; return t(np.interp(np.arange(0, len(s), 3), np.arange(len(s)), s).astype(np.float32))
R = {}
R["n9 앞창 23.0~27.50(→ 실소리 27.50 전)"] = cw(23.0, 27.50)
R["n9 뒤창 27.50~30.0"] = cw(27.50, 30.0)
R["n10 앞창 27.40~31.045"] = cw(27.40, 31.045)
R["n10 뒤창 31.045~33.0"] = cw(31.045, 33.0)
R["mp4 바뀐 구간 앞뒤 2초 25.45~32.97(BGM 포함)"] = t(mp[int(25.45*16000):int(32.97*16000)])
R["mp4 2장 끝까지 25.45~39.6"] = t(mp[int(25.45*16000):int(39.6*16000)])
for k, v in R.items(): print(k, "→", v)
json.dump(R, open("09강/검사_v7/받아쓰기_근거.json", "w"), ensure_ascii=False, indent=1)
