# 세 근거(규칙 24): #21(n22) 시작 · #22(n23) 넘김 — 깨끗한 v4 5ms RMS + 앞 창 · 뒤 창 받아쓰기 / 바뀐 구간 앞뒤 2초 받아쓰기(최종 mp4, BGM 포함)
import mlx_whisper, json, numpy as np, subprocess
c = np.load("clean_v4.npy").astype(np.float32)
def rms(a, b):
    s = c[int(a*48000):int(b*48000)].astype(np.float64); f = s[:len(s)//240*240].reshape(-1,240); d = 20*np.log10(np.sqrt((f**2).mean(1))+1e-12)
    return " ".join(f"{a+i*0.005:.3f}:{v:.0f}" for i, v in enumerate(d))
def asr(x):
    x = x[::3].copy() if len(x) and x.dtype == np.float32 and asr.sr == 48000 else x
    r = mlx_whisper.transcribe(x, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return r["text"].strip()
asr.sr = 48000
def cl(a, b):
    import scipy.signal as ss
    return ss.resample_poly(c[int(a*48000):int(b*48000)], 1, 3).astype(np.float32)
def mp4(a, b):
    return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",str(a),"-t",str(b-a),"-i","../../05강_v4.mp4","-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32)
R = {"rms_n22": rms(78.85, 79.06), "rms_n23": rms(82.40, 82.86)}
tr = lambda x: mlx_whisper.transcribe(x, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
W = {"n22 앞 창 75.4~78.996": cl(75.4, 78.996), "n22 뒤 창 78.996~82.45": cl(78.996, 82.45),
     "n23 앞 창 79.0~82.803": cl(79.0, 82.803), "n23 뒤 창 82.803~87.0": cl(82.803, 87.0)}
for k, x in W.items(): R[k] = tr(x)
for k, (a, b) in {"mp4 바뀐 구간 앞뒤 2초 76.94~84.44": (76.94, 84.44), "mp4 73.9~87.4(#20~#22 + 장 컷)": (73.9, 87.4)}.items(): R[k] = tr(mp4(a, b))
for k, v in R.items(): print(k, "→", v)
json.dump(R, open("../../검사_v4/받아쓰기_근거.json", "w"), ensure_ascii=False, indent=1)
