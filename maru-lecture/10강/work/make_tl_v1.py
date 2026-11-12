# 10강(오더43) 타임라인_v1 = 타임라인_v1_onset + 아나운서 「가」(20강 make_tl_v4 방식): fade_in 0.5 · 배치(규칙20, 검사_v1/배치.json) · ending.bye_freeze
# 순서: align.py → sent_check.py → align.py → fix09_tl10.py → fix23_tl10.py → resplit10.py → onset10.py → make_tl_v1.py
import json
import sys
SRC, DST = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("../타임라인_v1_onset.json", "../타임라인_v1.json")   # v2: 입력·출력 이름 인자
tl = json.load(open(SRC)); PL = json.load(open("../검사_v1/배치.json"))
import re, subprocess
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
# 🆕마지막 장(끝인사) 컷→말 0.07 → 0.09 로(gap_check 넘김합 1.764 < 1.766): 소리·클립·자막·엔딩을 같은 양만큼 뒤로(입 싱크 관계 그대로)
L = tl["slides"][-1]; ab = next(x for x in tl["audio"] if x["slide"] == L["slide"])
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "bye_tc_090.wav", "-af", "silencedetect=n=-40dB:d=0.02", "-f", "null", "-"], capture_output=True, text=True).stderr
on_src = float(re.findall(r"silence_end: ([0-9.]+)", o)[0]); DSH = round(L["start"] + 0.09 - (ab["out"] + on_src - ab["src_from"]), 4)
ab["out"] = round(ab["out"] + DSH, 4)
bye = next(x for x in tl["anchors"] if x["name"] == "끝인사"); bye["clip_t0"] = round(bye["clip_t0"] + DSH, 4); bye["out"] = bye["out"] + DSH
for k in ("voice_start", "voice_end", "src_offset"): L[k] = round(L[k] + DSH, 4)
L["end"] = q(L["voice_end"] + 3.5); L["gap_after_voice"] = round(L["end"] - L["voice_end"], 3); L["gap_before_voice"] = 0.09
LS = [x for x in tl["subs"] if x["slide"] == L["slide"]]
for i, x in enumerate(LS):
    x["voice_on"] = round(x["voice_on"] + DSH, 3)
    if i > 0: x["start"] = x["start"] + DSH; tl["subs"][tl["subs"].index(x) - 1]["end"] = x["start"]
T = L["end"]; LS[-1]["end"] = T
tl["ending"].update({"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)})
tl["total"] = round(T + 9.70, 3); tl["params"]["v1_last_shift"] = f"마지막 장 컷→말 0.09 맞춤 +{DSH}초(소리·클립·자막·엔딩 같이)"
print("마지막 장 밀기", DSH)
for a in tl["anchors"]:
    a["fade_in"] = 0.5; p = PL[a["name"]]
    if p.get("overlap_now", 0) > 0: a["x"] = p["x_new"]; a["place"] = f"지적 #9·규칙 20: 사진 겹침 {p['overlap_now']}화소 → 빈 공간 {p['free_run']} 가운데로(x {p['x_now']}→{p['x_new']}, 여백 {p['margin']})"
    else: a["place"] = "지적 #9·규칙 20: 안 가림 → 그대로"
_bye = next(a for a in tl["anchors"] if a["name"] == "끝인사"); tl["ending"]["bye_freeze"] = round(_bye["clip_t0"] + 18.0711, 3)   # 클립 시각 18.0511 = 입술 닫힌 첫 프레임(v1 실측 929.693 − clip_t0 911.6419) + 0.02
_off = next(x for x in tl["audio"] if x["slide"] == L["slide"]); _off = _off["out"] - _off["src_from"]
tl["ending"]["bye_freeze_note"] = (f"끝인사 마지막 단어 「살펴보겠습니다」 받아쓰기 끝 {16.48 + _off:.3f} · 실제 소리 끝(−40dB) {16.9 + _off:.3f} → 웃는 입(이 보임) 지나 입술 닫힌 첫 프레임 {_bye['clip_t0'] + 18.0511:.3f}(클립 18.0511초) 정지(trim end {tl['ending']['bye_freeze']:.3f})"
                                    f" → 알파 페이드 {_bye['out'] - 0.5:.3f}~{_bye['out']:.3f}. 말 끝 < 정지 < 페이드")
tl["params"]["v1_anchor"] = "warp_s flow 클립(아나운서B/run_warp.sh) · 등장 0.5초 알파 페이드인(인삿말 st=0 · 끝인사 cl_in+HF) · 끝인사 말끝→정지→페이드 · 배치 규칙20 · crop700"
tl["params"]["voice"] = "녹음_본문_04-20강/마루시공_-_10강.mp3 atempo=0.9 → work/v090.wav"
tl["params"]["greet"] = "강의인삿말/0.9배/인삿말_10강_090.wav → work/greet_a9_090.wav(48k) gain " + str([a for a in tl["audio"] if a.get("src") == "work/greet_a9_090.wav"][0]["gain"])
json.dump(tl, open(DST, "w"), ensure_ascii=False, indent=1)
print([(a["name"], a["x"], a["y"], a["fade_in"]) for a in tl["anchors"]], tl["ending"]["bye_freeze"], tl["total"], len(tl["subs"]))
