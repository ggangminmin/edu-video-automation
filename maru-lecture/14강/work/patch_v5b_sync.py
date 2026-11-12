# 14강 v5b = 타임라인_v5 + cx 반려(113 선행 0.185) · 새 줄 19개 깨끗한 음성 점검(check_newlines_v5.py) → 쉼 뒤 시작 줄 중 어긋난 3곳 = 실제 말 시작 − 0.09
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
FIX = {113: 450.535,   # 「최종 적용안을…」 쉼 450.345~450.525 뒤 첫 자음 (resplit 이 옛 쉼 449.975 를 골라 0.185 선행 · cx 결함)
       47: 187.54,     # 「서로 다른…」 쉼 뒤 ㅅ 시작 (lead −0.014)
       71: 288.115}    # 「어떤 관리법을…」 쉼 뒤 시작 (lead −0.006)
t = json.load(open("../타임라인_v5.json")); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        v = FIX[x["n"]]; st = q(v - 0.09)
        print(x["n"], x["text"], round(x["start"], 3), "→", round(st, 3))
        x["start"] = st; x["voice_on"] = v; x["how"] += " · v5b 깨끗한 음성 말 시작 −0.09"; S[i - 1]["end"] = st
t["params"]["v5b"] = "cx 반려 113 + 새 줄 19 점검: 113·47·71 시작 = 깨끗한 음성 말 시작 −0.09"
json.dump(t, open("../타임라인_v5b.json", "w"), ensure_ascii=False, indent=1)
