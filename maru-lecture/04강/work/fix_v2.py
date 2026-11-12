# 04강 v2 = 타임라인_v1 + scene_sub 「늦음」 진짜 3줄(받아쓰기 자르기 격자 · 검사_v1/scene_sub_grid*.txt) 줄 시작만 고침 — 소리·장·아나운서 그대로
#  3 「제6강에…」: 「제」 4.905 시작 → 「제│육」 사이 쉼(5.11~5.19) 뒤를 잡았던 것(newline_onset 은 그 쉼 끝을 실소리로 봄)
#  167·190 「몇 데시벨 이하인가요?」: 「몇」 703.355 / 796.775 시작 → 「몇│데시벨」 사이 쉼 뒤를 잡았던 것
import json
tl = json.load(open("../타임라인_v1.json")); S = tl["subs"]
FIX = {3: 4.905, 167: 703.355, 190: 796.775}
for k, s in enumerate(S):
    if s["n"] in FIX:
        on = FIX[s["n"]]; was = s["start"]; s["voice_on"] = on; s["start"] = on - 0.09; S[k - 1]["end"] = s["start"]
        s["how"] = f"v2 받아쓰기 자르기 손 실측(앞「…」 끝 · 뒤 첫 어절) · was {was:.3f}"; print(s["n"], round(was, 3), "→", round(s["start"], 3), s["text"])
for a, c in zip(S, S[1:]): assert a["end"] <= c["start"] + 1e-6 and c["start"] > a["start"] + 0.3, (a["n"], c["n"])
tl["params"]["v2"] = "v1 scene_sub 늦음 진짜 3줄(3·167·190) 줄 시작만 고침 · 그 밖 v1 과 같음"
json.dump(tl, open("../타임라인_v2.json", "w"), ensure_ascii=False, indent=1)
