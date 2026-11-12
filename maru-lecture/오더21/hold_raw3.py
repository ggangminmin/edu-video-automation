# 의심 줄 정밀: 깨끗한 음성 [자막−1.5, +1.5] mlx word_timestamps → 이 줄 첫 단어 시작 → ±0.12 안 가장 낮은 음량(30ms 평활) 자리 = 말 시작
import json, re, subprocess, numpy as np, mlx_whisper
SR = 16000; nz = lambda t: re.sub(r"[^가-힣0-9]", "", t)
SUS = [(12, 112), (12, 119), (12, 187), (13, 5), (13, 76), (13, 122), (15, 30), (15, 63), (15, 78), (15, 96), (12, 189), (13, 60), (15, 24)]
H = {(r["강"], r["줄"]): r for r in json.load(open("오더21/hold_raw.json"))}
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
V = {}; out = []
for N, n in SUS:
    r = H[(N, n)]; tln = "타임라인_v3c.json" if r["판"] == "v3c" else "타임라인_v3.json"
    if N not in V:
        tl = json.load(open(f"{N}강/{tln}")); T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
        for a in tl["audio"]:
            p = f"{N}강/" + a["src"] if a.get("src") else f"{N}강/work/v090.wav"
            if p not in cache: cache[p] = load(p)
            seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
            i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
        n10 = SR // 100; m = len(v) // n10; d = 20 * np.log10(np.sqrt((v[:m * n10].reshape(m, n10) ** 2).mean(1)) + 1e-9); V[N] = (v, np.convolve(d, np.ones(3) / 3, "same"))
    v, ds = V[N]; t0 = r["자막시작"]; a0 = t0 - 1.5
    p = "/private/tmp/claude-501/hold3.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", p], input=v[int(a0 * SR):int((t0 + 1.5) * SR)].tobytes())
    W = [(w["start"] + a0, w["end"] + a0, w["word"].strip()) for s in mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)["segments"] for w in s["words"]]
    head = nz(r["자막"]); best = None
    for i, (s_, e_, w) in enumerate(W):
        cat = nz("".join(x[2] for x in W[i:i + 3]))
        if cat[:2] == head[:2] or (cat[:1] == head[:1] and cat[1:3] == head[1:3]) or cat[:3] == head[1:4]:
            if best is None or abs(s_ - t0) < abs(best[0] - t0): best = (s_, w)
    if best:
        k0 = int(round(best[0] * 100)); seg = ds[k0 - 12:k0 + 13]; kk = k0 - 12 + int(np.argmin(seg)); on = kk / 100
    else: on = None
    out.append(dict(강=N, 줄=n, 자막=r["자막"], 자막시작=round(t0, 3), 단어=best and best[1], 단어시작=best and round(best[0], 3), 말시작=on, 자막_말=None if on is None else round(on - t0, 3),
                    words=[(round(s_ - t0, 2), w) for s_, e_, w in W if t0 - 1.2 < s_ < t0 + 1.2]))
    print(N, n, r["자막"][:12], "word", best, "→ lead", out[-1]["자막_말"], out[-1]["words"], flush=True)
json.dump(out, open("오더21/hold_raw3.json", "w"), ensure_ascii=False, indent=1)
