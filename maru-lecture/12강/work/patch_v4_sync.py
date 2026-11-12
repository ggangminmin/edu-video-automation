# 오더25: scene_sub v4 1차에서 걸린 새 줄 시작 2곳 → 검사기 말 시작(voice_t) − 0.09 로 (resplit_v4.py 실행 뒤 덮어 씀)
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
FIX = {171: 708.36, 189: 780.88}   # scene_sub v4 voice_t (171 쉼경계 lead 0.186 너무빠름 · 189 얕은골짜기 lead 0.2 보류)
p = "../타임라인_v4.json"; t = json.load(open(p)); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        v = FIX[x["n"]]; st = q(v - 0.09)
        print(x["n"], x["text"], round(x["start"], 3), "→", round(st, 3))
        x["start"] = st; x["voice_on"] = v; x["how"] += " · scene_sub voice_t 로 고침"; S[i - 1]["end"] = st
json.dump(t, open(p, "w"), ensure_ascii=False, indent=1)
