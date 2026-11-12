# 입 싱크 검산(#8): 클립 자체 소리(입을 만든 소리)·타입캐스트 소리를 각각 단어 단위로 받아써 같은 단어끼리 짝짓고,
#  warp 지도로 「그 단어의 입 모양이 화면에 나오는 출력 시각」과 「타입캐스트가 그 단어를 말하는 출력 시각」 차이를 잰다. 기준 ≤0.1초.
# 실행: ~/.venvs/tts/bin/python lipcheck.py <clip.wav> <target.wav> <warp.json>
import sys, json, re, difflib, numpy as np, mlx_whisper
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
import subprocess
def sils(p):                                                       # −40dB 0.12초↑ 쉼 → 단어 시작이 쉼 안에 찍히면 쉼 끝으로(whisper 단어 시작은 쉼 안에 일찍 찍힘)
    o = subprocess.run(["ffmpeg", "-i", p, "-af", "silencedetect=n=-40dB:d=0.12", "-f", "null", "-"], capture_output=True, text=True).stderr
    a = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)]; b = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]
    return list(zip(a, b))
def snap(t, S):
    for a, b in S:
        if a - 0.02 <= t < b: return b
    return t
def words(p):
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
    out = []
    for s in r["segments"]:
        for w in s["words"]:
            t = re.sub(r"[^가-힣0-9]", "", w["word"])
            if t: out.append((t, snap(w["start"], SIL[p]), w["end"]))
    return out, r["text"]
SIL = {cw: sils(cw), tw: sils(tw)}
C, ctext = words(cw); T, ttext = words(tw)
print("클립:", ctext); print("타입캐스트:", ttext)
sm = difflib.SequenceMatcher(None, [w[0] for w in C], [w[0] for w in T])
errs = []
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        c_t, t_t = C[a + k][1], T[b + k][1]
        if not (cs <= c_t <= ce and ts <= t_t <= te): continue
        u_voice = cs + (t_t - ts)                                  # 타입캐스트가 그 단어를 말하는 출력 시각
        u_mouth = cs + float(np.interp(c_t - cs, cl, tau))          # 그 단어 입 모양이 나오는 출력 시각(지도 역함수)
        errs.append((C[a + k][0], round(u_mouth - u_voice, 3)))
e = np.array([x[1] for x in errs])
print("짝지은 단어", len(errs), "/", len(T), " 오차 중앙", round(float(np.median(np.abs(e))), 3), " 최대", round(float(np.abs(e).max()), 3))
print([x for x in errs if abs(x[1]) > 0.1])
json.dump(dict(pairs=errs, median=float(np.median(np.abs(e))), max=float(np.abs(e).max()), n=len(errs), n_target=len(T)),
          open(wj.replace(".json", "_lip.json"), "w"), ensure_ascii=False, indent=1)
