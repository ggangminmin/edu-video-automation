# 오더34+팀장「19·20 ① = 가」: 타임라인_v4초안(줄 나눔) → 타임라인_v4 = anchors clip B(flow) · fade_in 0.5 · ending.bye_freeze
# 실행(cwd=20강/work): python3 make_tl_v4.py <bye_freeze> "<메모>"
import json, sys
tl = json.load(open("../타임라인_v4초안.json"))
for a in tl["anchors"]:
    a["clip_prev"] = a["clip"]; a["clip"] = f"../아나운서B/20_{a['name']}_flow2.mp4"; a["fade_in"] = 0.5
tl["ending"]["bye_freeze"] = float(sys.argv[1]); tl["ending"]["bye_freeze_note"] = sys.argv[2]
tl["params"]["v4_anchor"] = "오더33 방식: B flow 클립 · 등장 0.5초 알파 페이드인(인삿말 st=0 · 끝인사 cl_in+HF) · 클립에만 있는 말 없음(받아쓰기 대조)"
json.dump(tl, open("../타임라인_v4.json", "w"), ensure_ascii=False, indent=1)
print("ok", [(a["name"], a["clip"], a.get("x")) for a in tl["anchors"]], tl["ending"])
