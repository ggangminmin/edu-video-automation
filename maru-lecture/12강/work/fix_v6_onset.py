# 12강 v6 타임라인 = v5 + newline_onset_check(11/3) 걸림 중 4줄 시작만 = 실측 말 시작 − 0.09(프레임 격자) · 앞 줄 end 같이
#  실측 = 검수/검사기/newline_onset/12강.json(깨끗한 음성 5ms RMS 쉼 끝 −50dB 30ms). 「다른 후보 → OK」 78·171 은 손대지 않음(사람 확인)
import json
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
R = {r["n"]: r for r in json.load(open("../../검수/검사기/newline_onset/12강.json"))["rows"]}
FIX = [21, 42, 112, 117]
t = json.load(open("../타임라인_v5.json")); S = t["subs"]
for i, x in enumerate(S):
    if x["n"] in FIX:
        r = R[x["n"]]; assert r["text"] == x["text"] and abs(r["t"] - x["start"]) < 0.002, (r, x)
        new = q(r["onset"] - 0.09)
        print(x["n"], round(x["start"], 3), "→", round(new, 3), f"(소리 {r['onset']} · 앞 선행 {r['lead']} → {round(r['onset'] - new, 3)})", x["text"][:20])
        assert S[i - 1]["slide"] == x["slide"] and new > S[i - 1]["start"] + 0.5
        x["start"] = new; x["voice_on"] = r["onset"]; x["how"] = (x.get("how") or "") + " · v6 실소리 −0.09(newline_onset_check)"
        S[i - 1]["end"] = new
t["params"]["v6"] = "11/3 팀장: newline_onset_check 걸림 4줄(21·42·112·117) 시작 = 실측 말 시작 − 0.09. 78·171(다른 후보→OK)은 사람 확인"
json.dump(t, open("../타임라인_v6.json", "w"), ensure_ascii=False, indent=1)
