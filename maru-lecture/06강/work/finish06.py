# 06강 타임라인 마무리: 타임라인_v1초안(make_tl06) → 타임라인_<V>
#  ① 새 줄 시작 실소리 보정(onset06 결과 · 받아쓰기 ✓ · onset_man 손 실측) = ONSET[줄 글자] = 실소리(출력 초) → 자막 시작 = 실소리 − 0.09
#  ② 아나운서 자리(규칙 20 · chk/place06.py 실측) · ③ 끝인사 bye_freeze(입 다문 첫 프레임 · 눈으로 확인)
# 실행(cwd = 06강/work): python3 finish06.py <V> <bye_freeze> "<freeze 근거>"
import json, sys
V, FRZ, FRZ_NOTE = sys.argv[1], float(sys.argv[2]), sys.argv[3]
tl = json.load(open("../타임라인_v1초안.json"))
ONSET = {}
for f in ("onset_v1b.json", "onset_v1c.json"):
    for r in json.load(open(f)):
        if r.get("now") is not None and r["now"] != r.get("was"): ONSET[r["n"]] = (round(r["now"] + 0.09, 3), r.get("why"), r["text"])   # 줄 번호로(같은 글자 줄 있음: 「사 번, 헤링본」 16·20장)
S = tl["subs"]; rows = []
for tx, on in json.load(open("onset_man.json")).items():   # 손 실측(받아쓰기 자르기 확인) — 글자 하나뿐인 줄만
    ns = [x["n"] for x in tl["subs"] if x["text"] == tx]; assert len(ns) == 1, tx
    ONSET[ns[0]] = (on, "손 실측(받아쓰기 자르기)", tx)
for k, s in enumerate(S):
    if s["n"] in ONSET:
        on, why, tx = ONSET[s["n"]]; assert tx == s["text"], (s["n"], tx, s["text"])
        rows.append(dict(n=s["n"], text=s["text"], was=round(s["start"], 3), now=round(on - 0.09, 3), why=why))
        s["start"] = on - 0.09; s["voice_on"] = on; s["how"] = f"onset06({why} · 받아쓰기✓)"; S[k - 1]["end"] = s["start"]
for a, c in zip(S, S[1:]): assert a["end"] <= c["start"] + 1e-6 and c["start"] > a["start"] + 0.3, (a["n"], c["n"])
assert len(rows) == len(ONSET), (len(rows), len(ONSET))
PL = json.load(open("chk/배치06.json"))
for a in tl["anchors"]:
    r = PL[a["name"]]
    if r["overlap_now"] > 0:
        assert r["fits"] and r["overlap_new"] == 0; a["x"] = r["x_new"]; a["place"] = f"규칙 20: 표지 사진·글자 가림 {r['overlap_now']}px → 빈 공간 가운데 x{r['x_new']}(여백 {r['margin']})"
    else: a["place"] = "규칙 20: 안 가림 → 그대로"
tl["ending"]["bye_freeze"] = FRZ; tl["ending"]["bye_freeze_note"] = FRZ_NOTE
tl["params"]["onset"] = "새 줄 시작 = newline_onset_check --all 실소리 − 0.09 + 받아쓰기 확인(onset06.py) · 손 실측 onset_man.json"
json.dump(tl, open(f"../타임라인_{V}.json", "w"), ensure_ascii=False, indent=1)
for r in rows: print(r)
print("보정", len(rows), "· anchors", [(a["name"], a["x"], a["y"]) for a in tl["anchors"]], "· freeze", FRZ, "· total", tl["total"])
