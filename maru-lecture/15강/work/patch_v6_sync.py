# 15강 v6: scene_sub 1차에서 걸린 새 줄 시작 → 검사기 말 시작(voice_t) − 0.09 (12강 patch_v4_sync.py 방식, resplit_v6.py 실행 뒤 덮어 씀)
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
FIX = {128: 508.68}   # scene_sub v6 1차 voice_t (128 쉼경계 lead 0.439 너무빠름)
p = "../타임라인_v6.json"; t = json.load(open(p)); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        v = FIX[x["n"]]; st = q(v - 0.09)
        print(x["n"], x["text"], round(x["start"], 3), "→", round(st, 3))
        x["start"] = st; x["voice_on"] = v; x["how"] += " · scene_sub voice_t 로 고침"; S[i - 1]["end"] = st
json.dump(t, open(p, "w"), ensure_ascii=False, indent=1)
