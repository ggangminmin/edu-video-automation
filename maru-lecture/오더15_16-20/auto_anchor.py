# 오더15: warp 입싱크 0.1초 넘는 클립 → 쉼 경계 고정점 자동 짝(11강 입싱크_방식.md 2번을 자동으로)
#  클립·타깃 wav 각각 silencedetect −40dB d=0.12 → 타깃 쉼(시작·끝)을 지금 warp 지도로 클립 시각에 옮겨, ±0.4초 안 같은 종류 클립 쉼 경계와 짝
#  출력 = warp_clip2.py 6번째 인자 문자열 "클립초:타깃초,…"
import sys, json, re, subprocess, numpy as np
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
def sil(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    return list(zip(map(float, re.findall(r"silence_start: ([\d.]+)", o)), map(float, re.findall(r"silence_end: ([\d.]+)", o))))
SC = [(a, b) for a, b in sil(cw) if cs + 0.05 < a and b < ce - 0.05]; ST = [(a, b) for a, b in sil(tw) if ts + 0.05 < a and b < te - 0.05]
pairs = []
for a, b in ST:
    for kind, t in (("s", a), ("e", b)):
        c_est = cs + float(np.interp(t - ts, tau, cl))
        cand = [(x if kind == "s" else y) for x, y in SC]
        if not cand: continue
        c = min(cand, key=lambda v: abs(v - c_est))
        if abs(c - c_est) <= 0.4: pairs.append((round(c, 3), round(t, 3)))
pairs = sorted(set(pairs)); ok = []
for c, t in pairs:                                           # 단조(둘 다 증가)만
    if not ok or (c > ok[-1][0] and t > ok[-1][1]): ok.append((c, t))
print(",".join(f"{c}:{t}" for c, t in ok))
