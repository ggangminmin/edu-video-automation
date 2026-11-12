# #8 검산: 렌더 영상 소리의 인삿말·끝인사 구간 받아쓰기 + 하이젠 소리 섞임(포락선 상관: 타입캐스트 vs 하이젠)
import json, re, numpy as np, subprocess, mlx_whisper
tl = json.load(open("../타임라인_v3.json")); SR = 16000
def load(p, ss=None, t=None):
    a = ["ffmpeg", "-v", "error"] + (["-ss", str(ss), "-t", str(t)] if ss is not None else []) + ["-i", p, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.int16).astype(np.float32) / 32768
def env(y): n = len(y) // 160; return np.sqrt((y[:n * 160].reshape(n, 160) ** 2).mean(1))
def corr(a, b): n = min(len(a), len(b)); return round(float(np.corrcoef(env(a[:n]), env(b[:n]))[0, 1]), 3)
out = {}
for name, src, hg, a_out in [("인삿말", "greet_a10_090.wav", "../../아나운서/11강/11_인삿말_090.wav", tl["audio"][0]["out"]),
                             ("끝인사", "bye_tc_090.wav", "../../아나운서/11강/11_끝인사_090.wav", tl["audio"][-1]["out"])]:
    tc = load(src); dur = len(tc) / SR
    v = load("../11강_v3.mp4", a_out, dur)
    clip_t0 = a_out - (0.69 if name == "인삿말" else 1.36)          # 하이젠 소리를 클립 원래 자리에 깔았다면 놓였을 자리
    h = load(hg); hv = load("../11강_v3.mp4", clip_t0, len(h) / SR)
    txt = mlx_whisper.transcribe(v, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"]
    ref = mlx_whisper.transcribe(tc, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"]
    nr = lambda s: re.sub(r"[^가-힣0-9]", "", s)
    out[name] = dict(영상받아쓰기=txt.strip(), 타입캐스트받아쓰기=ref.strip(), 글자같음=nr(txt) == nr(ref),
                     상관_영상vs타입캐스트=corr(v, tc), 상관_영상vs하이젠소리=corr(hv, h))
    print(name, out[name], flush=True)
json.dump(out, open("../voice_check_v3.json", "w"), ensure_ascii=False, indent=1)
