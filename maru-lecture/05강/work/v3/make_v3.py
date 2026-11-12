# 05강 v3(오더51 토막 자막): 타임라인_v2 → 타임라인_v3. 글자·소리·장·아나운서 그대로, 나눔 자리·자막 시각만.
# MERGE = 두 장 → 한 장(첫 장 시작 · 둘째 장 끝) · SPLIT = 새 나눔(둘째 장 시작 = 첫 어절 실소리 − 0.09)
# 실소리 = 깨끗한 음성 5ms RMS(v3/dbtrace.py) + 받아쓰기 앞 창 [t−1,t] · 뒤 창 [t,t+1.2](v3/probe.json · probe2.json)
import json, sys; sys.path.insert(0, "v3"); from plan import MERGE, SPLIT
tl = json.load(open("../타임라인_v2.json")); S = tl["subs"]
ON = {11: (41.62, 41.53), 81: (335.95, 335.86), 91: (375.235, 375.145), 99: (406.27, 406.18),
      193: (770.51, 770.45), 223: (888.74, 888.65), 229: (907.19, 907.10)}   # (실소리, 자막 시작)
new = []; i = 0
while i < len(S):
    x = S[i]
    if i in MERGE:
        y = S[i+1]; m = dict(x); m["text"] = x["text"] + " " + y["text"]; m["end"] = y["end"]; m["v3"] = f"한 장 합침(v2 n{x['n']}+n{y['n']})"
        new.append(m); i += 2; continue
    if i in SPLIT:
        y = S[i+1]; full = x["text"] + " " + y["text"]; a = SPLIT[i]; assert full.startswith(a + " "), i; b = full[len(a)+1:]
        on, st = ON[i]; x2 = dict(x, text=a, end=st); y2 = dict(y, text=b, start=st)
        if "v090_on" in y and "voice_on" in y: y2["v090_on"] = round(y["v090_on"] + on - y["voice_on"], 3)
        y2["voice_on"] = on; y2["how_on"] = "실소리 −0.09 · v3 토막(오더51)"
        x2["v3"] = y2["v3"] = f"다시 나눔(v2 n{x['n']}/n{y['n']})"; new += [x2, y2]; i += 2; continue
    new.append(x); i += 1
# 규칙 24 ⑥(팀장 11/9): 바뀐 카드 밖 newline_onset 걸림 줄 세 근거 → 늦게 뜨는 자막 1줄(v2 n179 「준비표와」) 고침
#  ㅈ 마찰 707.955~708.035(3kHz↑ 비 0.92~1.00 · v3/hf.py) · 앞 창 [706.965,707.965] 「…있…」(「준」 없음) · 뒤 창 [708.0,] 「준비」 → 실소리 707.955, 자막 708.007 = 0.05초 늦음
FIX = {"준비표와 작업 기록에는 정확한 명칭을 적는 편이 좋습니다": (707.955, 707.865)}
for k, x in enumerate(new):
    if x["text"] in FIX:
        on, st = FIX[x["text"]]; new[k-1]["end"] = st
        if "v090_on" in x and "voice_on" in x: x["v090_on"] = round(x["v090_on"] + on - x["voice_on"], 3)
        x["start"] = st; x["voice_on"] = on; x["how_on"] = "실소리(ㅈ 마찰) −0.09 · v3 규칙24⑥ 늦은 자막 고침"; x["v3"] = "시작 당김(v2 708.007)"
for k, x in enumerate(new): x["n"] = k + 1
tl["subs"] = new
tl["params"]["v3"] = "오더51 토막 자막: 한 장 합침 4 · 다시 나눔 7(둘째 장 시작 = 실소리 −0.09) · 늦은 자막 1줄 당김(n177 준비표와) · 소리·장·아나운서·BGM v2 그대로"
json.dump(tl, open("../타임라인_v3.json", "w"), ensure_ascii=False, indent=1)
# 확인: subs 밖 키 같음 · 글자 같음 · 시간 순서
v2 = json.load(open("../타임라인_v2.json"))
assert all(tl[k] == v2[k] for k in tl if k not in ("subs", "params"))
f = lambda L: "".join(s["text"] for s in L).replace(" ", ""); assert f(new) == f(S)
assert all(new[j]["end"] <= new[j+1]["start"] + 1e-6 and new[j]["start"] < new[j]["end"] for j in range(len(new)-1))
print("subs", len(S), "→", len(new), "OK")
