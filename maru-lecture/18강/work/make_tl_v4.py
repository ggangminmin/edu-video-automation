# 18강 타임라인_v4 = p21 타임라인_v4초안 + #30(「소매와 끈, 장신구,」 짧음 → 「…긴 머리카락이」/「장비에 …」) + 아나운서 가(flow 클립·페이드인·끝인사 정지)
import json, sys
tl = json.load(open("../타임라인_v4초안.json"))
S = tl["subs"]
i = next(k for k, s in enumerate(S) if s["text"] == "소매와 끈, 장신구,")
a, b = S[i], S[i + 1]
assert b["text"] == "긴 머리카락이 장비에 말려들지 않도록 정리합니다"
# #30: 처음엔 「…긴 머리카락이」/「장비에 …」로 나눴으나 line_break_check 「주어 뒤」 위반 → 한 장으로 합침(37자, 가장 긴 카드 36자 · 쉼표 2 포함)
a["text"] = "소매와 끈, 장신구, 긴 머리카락이 장비에 말려들지 않도록 정리합니다"; a["end"] = b["end"]; a["n_v3d"] = [41, 42]
a["how"] = "문장시작(#30 민석: 짧은 카드 → 한 장)"
del S[i + 1]
for k, s in enumerate(S): s["n"] = k + 1

# 🆕 #30 과 같은 종류(쉼표 나열 조각 2초 안 됨) 3곳 — 앞뒤 카드 합쳐 다시 나눔(새 줄 시작 = 첫 어절 mlxwords 출력 시각 − 0.09)
def resplit(t1, t2, l1, l2, w_on):
    k = next(k for k, s in enumerate(S) if s["text"] == t1); x, y = S[k], S[k + 1]; assert y["text"] == t2, y["text"]
    assert (t1 + " " + t2).replace(" ", "") == (l1 + l2).replace(" ", "")
    cut = w_on - 0.09
    x["text"] = l1; x["end"] = cut
    y.update(text=l2, start=cut, voice_on=w_on, how="줄나눔v4(#30 같은 종류 · 어절 받아쓰기 −0.09)", sent_start=False)
resplit("반입, 절단, 접착,", "마감으로 작업이 바뀔 때 누가 어디에 있는지도 달라집니다", "반입, 절단, 접착, 마감으로 작업이 바뀔 때", "누가 어디에 있는지도 달라집니다", 67.482)
resplit("무게와 길이,", "이동 경로에 따라 두 사람이 함께 들거나 운반 장비를 사용합니다", "무게와 길이, 이동 경로에 따라 두 사람이 함께 들거나", "운반 장비를 사용합니다", 227.49)   # 「따라 /」 는 검사기 위반 → 연결어미 「들거나」 뒤
k = next(k for k, s in enumerate(S) if s["text"] == "무거운 운반에는 동선과"); x, y = S[k], S[k + 1]
assert y["text"] == "인원 및 장비 계획처럼 구체적으로 생각합니다"
x["text"] = "무거운 운반에는 동선과 인원 및 장비 계획처럼 구체적으로 생각합니다"; x["end"] = y["end"]; x["how"] = (x.get("how") or "") + " · #30 같은 종류 → 한 장(36자, 「계획처럼 /」 검사기 위반)"
del S[k + 1]
for k, s in enumerate(S): s["n"] = k + 1

cfg = json.load(open("../아나운서B/anchor_cfg.json"))   # warp 뒤 채움
for an in tl["anchors"]:
    c = cfg[an["name"]]; an.update(clip=c["clip"], clip_t0=c["clip_t0"], fade_in=0.5, clip_note=c["note"])
tl["ending"]["bye_freeze"] = cfg["bye_freeze"]; tl["ending"]["bye_freeze_note"] = cfg["bye_freeze_note"]
tl["params"]["v4_18"] = "18강 v4(p1V): p21 초안 + #30 · 아나운서 가(warp_s flow · 0.5초 페이드인 · 끝인사 말끝→정지→페이드)"
json.dump(tl, open("../타임라인_v4.json", "w"), ensure_ascii=False, indent=1)
print("ok", len(S))
