# 18강 타임라인_v4b(cx v4 반려 D1·U1 고침) / v4 = p21 타임라인_v4초안 + #30(「소매와 끈, 장신구,」 짧음 → 「…긴 머리카락이」/「장비에 …」) + 아나운서 가(flow 클립·페이드인·끝인사 정지)
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

# cx v4 D1: 「비산에는 …」 는 글자 그대로인데 p21 resplit 이 시작을 549.282067→549.215333(−2f)로 옮김 → v3c 시각으로 되돌림(변경표 밖 변경 0)
k = next(k for k, s in enumerate(S) if s["text"] == "비산에는 구역 관리와 적절한 장비 및 보호구,")
S[k]["start"] = 549.2820666666667; S[k - 1]["end"] = S[k]["start"]; S[k]["how"] = "무음끝"; S[k]["voice_on"] = 549.366

# cx v4 U1: 줄 나눔으로 새로 생긴 줄 시작 = mlxwords 단어 시각 −0.09 였는데 받아쓰기 시각이 −0.06~+0.25초 틀림
#  → 깨끗한 음성 5ms RMS 단어 사이 골짜기 뒤 −50dB 를 30ms 이상 넘는 첫 시각 = 실소리 시작(검사_v4b/onset50.json · 골짜기 −45dB 보다 얕은 29번은 골짜기 자체) − 0.09
ONSET = {"누가 어디에": 67.4, "설명서의 안전": 114.435, "완전히 멈춘": 117.55, "무릎 보호대처럼": 167.725, "동선을 나눠": 211.005, "운반 장비를": 227.835, "중간에 자세를": 233.46, "담당자를 먼저": 266.615, "재개 조건을": 285.24, "표면 아래의": 291.79, "사용 제한을": 326.705, "공구가 닿는": 356.195, "충돌 위험이": 409.82, "현재 위험이": 432.97, "상태를 공유합니다": 483.09, "공구를 사용할": 500.465, "판단하지 않습니다": 620.195, "유지되는 작업": 631.865, "해당 공구의": 898.02, "배치와 장비": 905.94}
for k_, on in ONSET.items():
    k = [k for k, s in enumerate(S) if s["text"].startswith(k_)]; assert len(k) == 1, k_; k = k[0]
    S[k]["start"] = on - 0.09; S[k]["voice_on"] = on; S[k - 1]["end"] = S[k]["start"]
    S[k]["how"] = "줄나눔v4b(실소리 −50dB 30ms 상승 −0.09)"
cfg = json.load(open("../아나운서B/anchor_cfg.json"))   # warp 뒤 채움
for an in tl["anchors"]:
    c = cfg[an["name"]]; an.update(clip=c["clip"], clip_t0=c["clip_t0"], fade_in=0.5, clip_note=c["note"])
tl["ending"]["bye_freeze"] = cfg["bye_freeze"]; tl["ending"]["bye_freeze_note"] = cfg["bye_freeze_note"]
tl["params"]["v4_18"] = "18강 v4(p1V): p21 초안 + #30 · 아나운서 가(warp_s flow · 0.5초 페이드인 · 끝인사 말끝→정지→페이드)"
json.dump(tl, open("../타임라인_v4b.json", "w"), ensure_ascii=False, indent=1)
print("ok", len(S))
