# v2 검사기 결과(말 시작 실측, v2 출력 시각) → 0.9배 원본 시각 onsets_v3.json + 손 검증 20줄(evalsync GT)과 대조
import json
v1 = json.load(open("tl_v1.json")); v2 = json.load(open("tl_v2.json"))
r = json.load(open("../../검수/검사기/v2_결과.json"))
o1 = {s["slide"]: s.get("src_offset", 0) for s in v1["slides"]}; o2 = {s["slide"]: s.get("src_offset", 0) for s in v2["slides"]}
sl = {x["n"]: x["slide"] for x in v2["subs"]}
GT = {12:50.900,17:68.170,32:127.169,41:163.912,50:195.903,52:203.553,97:364.143,104:385.687,107:395.354,120:446.216,133:496.541,146:540.468,158:586.369,162:598.144,165:610.434,167:616.311,196:723.698,198:729.254,204:750.264,215:789.761}
on = {}
for x in r["sync"]:
    if "voice_t" in x: on[x["n"]] = round(x["voice_t"] - o2[sl[x["n"]]], 3)
print("측정", len(on), "/", len(v2["subs"]), "판정불가", [x["n"] for x in r["sync"] if "voice_t" not in x])
err = []
for n, g in GT.items():
    gs = g - o1[sl[n]]
    if n in on: err.append(round(on[n] - gs, 3)); print(n, "GT", round(gs, 3), "실측", on[n], "차", round(on[n] - gs, 3))
print("GT 차 최대", max(map(abs, err)) if err else None)
json.dump(on, open("onsets_v3.json", "w"), indent=1)
