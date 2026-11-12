# 13강 v7 = 타임라인_v6 + newline_onset_check 걸림 5줄 시작 = 실측 말 시작 − 0.09 (팀장 오더 11/3) · 120(다른 후보→OK)·123·226(v2 판정불가)은 그대로 = 사람 확인
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
tl = json.load(open("../타임라인_v6.json"))
rows = {r["n"]: r for r in json.load(open("../../검수/검사기/newline_onset/13강.json"))["rows"]}
FIX = [5, 77, 106, 143]   # newline_onset_check v2: 123 = 판정불가 → 손대지 않음(사람 확인)
S = tl["subs"]; idx = {s["n"]: i for i, s in enumerate(S)}
log = []
for n in FIX:
    r = rows[n]; i = idx[n]; s = S[i]; p = S[i - 1]
    assert abs(s["start"] - r["t"]) < 0.002 and s["text"] == r["text"], (n, s["start"], r["t"])
    assert abs(p["end"] - s["start"]) < 1e-6, ("앞 줄과 붙어 있지 않음", n)
    new = q(r["onset"] - 0.09)
    log.append((n, round(s["start"], 3), round(new, 3), r["onset"], s["text"][:16]))
    s["start"] = new; s["voice_on"] = r["onset"]; s["how"] = "v7 시작 = newline_onset 실측 −0.09"; p["end"] = new
    assert new - p["start"] > 0.8 and s["end"] - new > 0.8, ("짧은 줄", n)
tl["params"]["v7"] = "v6 + newline_onset_check 걸림 4줄(5·77·106·143, v2 기준) 시작 = 실측 말 시작 −0.09 · 120·123·226 사람 확인(v2)"
json.dump(tl, open("../타임라인_v7.json", "w"), ensure_ascii=False, indent=1)
for x in log: print(x)
