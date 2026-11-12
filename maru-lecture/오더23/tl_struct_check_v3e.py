# 오더23: 오더09_공용/tl_struct_check.py 복사 · v2→v3 경로만
# 타임라인 단계 구조 검사(scene_sub_check 의 렌더 전 부분): ① 장면 시작 프레임 = 그 장면 첫 자막 시작 · 장면 경계를 넘는 자막 0
#  ② 자막 선행(voice_on − start) 0~0.16초 · ③ 빈 바(첫 자막~끝 자막 사이 틈) 0 · ④ 장면 연속(틈·겹침 0) · 텀(말 끝→컷) 강 규칙대로
import sys, json
N = sys.argv[1]; tl = json.load(open(f"{N}강/타임라인_v3e.json")); E = 1e-3
S = tl["slides"]; U = tl["subs"]; bad = []
for a, b in zip(S, S[1:]):
    if abs(a["end"] - b["start"]) > E: bad.append(("장면틈", a["slide"], round(b["start"] - a["end"], 3)))
for s in S:
    ss = [x for x in U if x["slide"] == s["slide"]]
    if s["slide"] != 1 and abs(ss[0]["start"] - s["start"]) > E: bad.append(("첫자막≠장면", s["slide"]))
    if ss[-1]["end"] - s["end"] > E: bad.append(("경계넘음", s["slide"]))
    if s["slide"] > 1 and ss[-1]["end"] < s["end"] - E: bad.append(("장면끝 전 자막 끝", s["slide"]))
for x in U:
    ld = x["voice_on"] - x["start"]
    if not (-E <= ld <= 0.16 + E): bad.append(("선행", x["n"], round(ld, 3), x["text"][:12]))
for a, b in zip(U, U[1:]):
    if abs(a["end"] - b["start"]) > E: bad.append(("빈바", a["n"], round(b["start"] - a["end"], 3)))
gaps = {}
for s in S[1:]:
    g = round(s.get("gap_after_voice", 0), 1); gaps.setdefault(g, []).append(s["slide"])
print(N, "걸림", len(bad), bad[:10], "| 말끝→컷 분포", {k: v for k, v in sorted(gaps.items())}, "| 총", tl["total"])
