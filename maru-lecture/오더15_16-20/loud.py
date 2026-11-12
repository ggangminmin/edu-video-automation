# loud15.json 에 강 음성(v090)·인삿말(greet_a) Integrated LUFS 실측(ffmpeg ebur128) 더하기 — 곡 LUFS·길이는 오더09 실측 그대로
import sys, json, re, subprocess, os
n = sys.argv[1]; P = "오더15_16-20/loud15.json"
L = json.load(open(P)) if os.path.exists(P) else {k: v for k, v in json.load(open("오더09_공용/loud09.json")).items() if k in ("bgm", "bgm_dur")} | {"voice": {}, "greet": {}, "_note": "ebur128 Integrated LUFS · 곡 = 오더09 실측"}
def lufs(p):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
L["voice"][n] = lufs(f"{n}강/work/v090.wav"); L["greet"][n] = lufs(f"{n}강/work/greet_a{int(n)-1}_090.wav")
json.dump(L, open(P, "w"), ensure_ascii=False, indent=1); print("LUFS", n, "음성", L["voice"][n], "인삿말", L["greet"][n])
