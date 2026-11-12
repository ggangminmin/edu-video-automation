# 규칙 24 세 근거 받아쓰기: 깨끗한 v4 음성 앞/뒤 창 + mp4(BGM 포함) 바뀐 구간 앞뒤 2초
import numpy as np, subprocess, mlx_whisper, json
SR = 48000; c = np.load("clean_v4.npy").astype(np.float32)
mp = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","../../07강_v4.mp4","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
def t(x): return mlx_whisper.transcribe(x, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
def cw(a, b): s = c[int(a*SR):int(b*SR)]; return t(s[::3].copy())
R = {}
R["n90 앞창 373.95~377.48(실소리 전)"] = cw(373.95, 377.48)
R["n90 뒤창 377.48~381.90"] = cw(377.48, 381.90)
R["n109 앞창 445.15~447.955(실소리 전)"] = cw(445.15, 447.955)
R["n109 뒤창 447.955~452.30"] = cw(447.955, 452.30)
R["mp4 n90 앞뒤 2초 375.43~383.83(BGM 포함)"] = t(mp[int(375.43*16000):int(383.83*16000)])
R["mp4 8장 끝~9장 첫 문장 368.9~388.0"] = t(mp[int(368.9*16000):int(388.0*16000)])
R["mp4 n108~109 443.1~454.4"] = t(mp[int(443.1*16000):int(454.4*16000)])
for k, v in R.items(): print(k, "→", v)
json.dump(R, open("../../검사_v4/받아쓰기_근거.json", "w"), ensure_ascii=False, indent=1)
