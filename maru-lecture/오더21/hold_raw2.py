# hold_raw.py 의 의심 줄 재확인(fix_bound 방식): 자막 −0.4~+0.6 안 후보(무음 끝·음량 골짜기 뒤 +6dB) 마다 [c−1.0,c]·[c,c+1.0] 받아쓰기
#  → 「뒤 = 이 줄 첫 말로 시작 · 앞 끝 = 첫 말 없음」 인 가장 이른 후보 = 말 시작. 후보별 받아쓰기 전부 남김(눈 대조용)
import json, re, subprocess, numpy as np, mlx_whisper
SR = 16000; nz = lambda t: re.sub(r"[^가-힣0-9]", "", t)
R = [r for r in json.load(open("오더21/hold_raw.json")) if r["판단"] != "정상" or not r["받아쓰기맞음"] and r["검사기"] == "보류"]
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def asr(x):
    p = "/private/tmp/claude-501/hold_raw_tmp2.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", p], input=x.astype(np.float32).tobytes())
    return mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
V = {}; out = []
for r in R:
    N = r["강"]; tln = "타임라인_v3c.json" if r["판"] == "v3c" else "타임라인_v3.json"
    if N not in V:
        tl = json.load(open(f"{N}강/{tln}")); T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
        for a in tl["audio"]:
            p = f"{N}강/" + a["src"] if a.get("src") else f"{N}강/work/v090.wav"
            if p not in cache: cache[p] = load(p)
            seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
            i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
        n10 = SR // 100; m = len(v) // n10; d = 20 * np.log10(np.sqrt((v[:m * n10].reshape(m, n10) ** 2).mean(1)) + 1e-9); V[N] = (v, d, np.convolve(d, np.ones(3) / 3, "same"))
    v, d, ds = V[N]; t0 = r["자막시작"]; a, b = int((t0 - 0.4) * 100), int((t0 + 0.6) * 100)
    cand = set(i for i in range(a, b) if d[i - 1] < -40 <= d[i])
    for i in range(a + 2, b - 2):
        if ds[i] <= ds[i - 2:i + 3].min() and ds[i - 6:i].max() - ds[i] >= 4:
            j = i
            while j < b and ds[j] < ds[i] + 6: j += 1
            cand.add(j)
    head = nz(r["자막"])[:2]; tried = []; best = None
    for c in sorted(cand):
        A = asr(v[int((c / 100 - 1.0) * SR):int(c / 100 * SR)]); B = asr(v[int(c / 100 * SR):int((c / 100 + 1.0) * SR)])
        okc = nz(B)[:2] == head and head not in nz(A)[-3:]
        tried.append((round(c / 100 - t0, 2), A[-10:], B[:12], okc))
        if okc and best is None: best = c / 100
    out.append(dict(강=N, 줄=r["줄"], 자막=r["자막"], 검사기=r["검사기"], 검사기_lead=r["검사기_lead"], 에너지_lead=r["자막_말"],
                    말시작_lead=None if best is None else round(best - t0, 3), 후보=tried))
    print(N, r["줄"], r["자막"][:14], "→", out[-1]["말시작_lead"], [t for t in tried], flush=True)
json.dump(out, open("오더21/hold_raw2.json", "w"), ensure_ascii=False, indent=1)
