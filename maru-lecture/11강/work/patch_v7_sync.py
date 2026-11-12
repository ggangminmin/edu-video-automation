# 11강 v7 1차 scene_sub 「너무빠름」 1곳 → 검사기 말 시작 −0.09 로(12강 work/patch_v4_sync.py 방식) · 타임라인_v7.json 의 subs 만, 앞 줄 end 같이
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
FIX = {71: 287.39}   # n: scene_sub voice_t (1차 lead 0.337 · 「…하므로 / 평면」 쉼 뒤 말 시작)
p = "../타임라인_v7.json"; t = json.load(open(p)); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        new = q(FIX[x["n"]] - 0.09); print(x["n"], round(x["start"], 3), "→", round(new, 3), x["text"])
        x["start"] = new; x["voice_on"] = FIX[x["n"]]; x["how"] += " · 패치(scene_sub 말 시작 −0.09)"
        S[i - 1]["end"] = new
json.dump(t, open(p, "w"), ensure_ascii=False, indent=1)
