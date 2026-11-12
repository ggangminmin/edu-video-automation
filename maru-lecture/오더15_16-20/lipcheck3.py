# 오더15-2 검산: lipcheck2(단어 짝) + 단어 시작 보정 — whisper 단어 시작 ±0.35초 안에 쉼 끝(−40dB ≥0.05초)이 있으면 그 쉼 끝 = 실제 말 시작
#  (whisper 가 앞 단어 끝소리 안에 다음 단어 시작을 찍는 오류 — 18강 「개인」 9.92 ↔ 실제 10.09). 쉼 끝이 한쪽에만 있으면 「한쪽만 쉼」으로 표시
import sys, os, json, re, difflib, subprocess, numpy as np
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
def sil_end(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=n=-40dB:d=0.05", "-f", "null", "-"], capture_output=True, text=True).stderr
    return np.array(list(map(float, re.findall(r"silence_end: ([\d.]+)", o))))
def words(p):
    E = sil_end(p); out = []
    for w, a, b in json.load(open(p.replace(".wav", "_words.json")))["words"]:
        t = re.sub(r"[^가-힣0-9]", "", w)
        if not t: continue
        k = E[np.abs(E - a) <= 0.35] if len(E) else []
        out.append((t, float(k[np.argmin(np.abs(k - a))]) if len(k) else a, len(k) > 0))
    return out
C, T = words(cw), words(tw)
sm = difflib.SequenceMatcher(None, [w[0] for w in C], [w[0] for w in T], autojunk=False)
errs = []
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        (wc, c_t, c_s), (_, t_t, t_s) = C[a + k], T[b + k]
        if not (cs <= c_t <= ce and ts <= t_t <= te): continue
        e = round(cs + float(np.interp(c_t - cs, cl, tau)) - (cs + t_t - ts), 3)
        errs.append((wc, e, "둘다쉼끝" if c_s and t_s else "한쪽만쉼" if c_s != t_s else "말 이어짐(whisper)"))
both = [abs(e) for _, e, k in errs if k == "둘다쉼끝"]
res = dict(n=len(errs), both_n=len(both), both_max=round(max(both), 3) if both else None, over=[x for x in errs if abs(x[1]) > 0.1])
json.dump(dict(res, pairs=errs), open(wj.replace(".json", "_lip3.json"), "w"), ensure_ascii=False, indent=1)
print(os.path.basename(wj), "단어", res["n"], "· 둘다 쉼 끝", res["both_n"], "최대", res["both_max"], "· 0.1 넘음", res["over"])
