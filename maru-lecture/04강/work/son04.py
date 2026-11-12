# 04강 문장 시작 재검(05강 son_fix 방식을 초안 구조에 맞춤): 앞 줄 voice_on ~ 이 문장 시작+1.4 안 가장 긴 무음(−40dB ≥0.08) 끝 vs 지금 시작
import json, re, subprocess
d = json.load(open("../타임라인_초안.json")); off = {s["slide"]: s["src_offset"] for s in d["slides"] if "src_offset" in s}
o = subprocess.run(["ffmpeg","-hide_banner","-i","v090.wav","-af","silencedetect=n=-40dB:d=0.08","-f","null","-"],capture_output=True,text=True).stderr
S = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]))
body = [x for x in d["subs"] if "part" not in x]; n = 0
for i, x in enumerate(body):
    if x["how"] != "문장시작" or i == 0 or body[i-1]["slide"] != x["slide"]: continue
    t = x["voice_on"] - off[x["slide"]]; p = body[i-1]["voice_on"] - off[x["slide"]]
    c = [(b - a, a, b) for a, b in S if a >= p + 0.2 and b <= t + 1.4]
    if not c: print("후보없음", x["n"], x["text"][:14]); continue
    dd, a, b = max(c)
    if abs(b - t) > 0.05: n += 1; print(x["n"], x["slide"], x["text"][:16], "지금", round(t, 3), "→ 긴무음끝", round(b, 3), "쉼", round(dd, 2))
print("어긋남", n)
