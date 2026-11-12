# warp 타깃 받아쓰기 단어 시작 보정 사본(원 캐시 그대로): 단어 시작 뒤 0.3초 안에서 쉼(−40dB ≥0.08)이 시작하고 그 쉼이 단어 끝 전에 끝나면 → 시작 = 쉼 끝
#  (18강 p1V `_fix_words` 방식 · 04강 bye 「5강에서는」 9.78 → 쉼 9.93~11.00 뒤)
import json, re, subprocess, shutil, sys
for base in sys.argv[1:]:
    o = subprocess.run(["ffmpeg","-hide_banner","-i",base+".wav","-af","silencedetect=n=-40dB:d=0.08","-f","null","-"],capture_output=True,text=True).stderr
    S = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]))
    d = json.load(open(base+"_words.json")); ch = []
    for w in d["words"]:
        for a, b in S:
            if w[1] - 0.02 <= a <= w[1] + 0.3 and b < w[2] + 0.6 and b > w[1] and b - a >= 0.12:   # 0.09 짧은 쉼(「조건과」 안)은 제외
                ch.append((w[0], w[1], round(b, 3))); w[1] = round(b, 3); w[2] = max(w[2], w[1] + 0.05); break
    shutil.copy(base+".wav", base+"_fix.wav"); json.dump(d, open(base+"_fix_words.json","w"), ensure_ascii=False, indent=0)
    print(base, "고친 단어", ch)
