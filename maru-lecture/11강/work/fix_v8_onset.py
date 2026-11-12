# 11강 v8 타임라인 = v7 + 40번 「전용 로제트로 마감합니다」 시작만 = 실소리 166.485 − 0.09(팀장 11/3 결정)
#  근거: newline_onset_check v2 — 앞 「고」 165.79~165.96 → 쉼 165.96~166.485(525ms) → 「전용」(받아쓰기 166.45~ 「전용 로제트로 마감」) · v7 자막 165.766 = 0.72초 이름
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
t = json.load(open("../타임라인_v7.json")); S = t["subs"]
i = next(k for k, x in enumerate(S) if x["n"] == 40); x = S[i]
assert x["text"] == "전용 로제트로 마감합니다" and abs(x["start"] - 165.766) < 0.002, x
new = q(166.485 - 0.09); print(40, round(x["start"], 3), "→", round(new, 3))
x["start"] = new; x["voice_on"] = 166.485; x["how"] += " · v8 실소리 −0.09(newline_onset_check v2)"; S[i - 1]["end"] = new
t["params"]["v8"] = "11/3 팀장: 40번 시작 = 실소리 166.485 − 0.09 (v7 0.72초 이름)"
json.dump(t, open("../타임라인_v8.json", "w"), ensure_ascii=False, indent=1)
