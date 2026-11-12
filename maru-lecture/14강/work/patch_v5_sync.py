# 14강 v5: scene_sub 1차에서 걸린 새 줄 시작 1곳 → 검사기 말 시작(voice_t) − 0.09 (resplit_v5.py 뒤 덮어 씀 · 12강 patch_v4_sync 방식)
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
FIX = {181: 748.055}   # 「비용 부담 주체가 정해집니다」 lead 0.441 너무빠름 (「구분해야」 뒤 쉼)
p = "../타임라인_v5.json"; t = json.load(open(p)); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        v = FIX[x["n"]]; st = q(v - 0.09)
        print(x["n"], x["text"], round(x["start"], 3), "→", round(st, 3))
        x["start"] = st; x["voice_on"] = v; x["how"] += " · scene_sub voice_t 로 고침"; S[i - 1]["end"] = st
json.dump(t, open(p, "w"), ensure_ascii=False, indent=1)
