# 11강 v3 타임라인 — 오더 06
#  · 텀은 장면 바뀌기 전에: 말 끝 → (텀) → 다음 장면 + 새 자막 같은 프레임 → 0.09초 뒤 말
#    텀 값은 v2 그대로: 보통 POST 0.30 + PRE 1.00 = 말 사이 1.30초 / 문제 대기 = 문제 낭독 끝 → 컷 5.5초
#  · 자막 시작 = 말 시작(onsets_v3.json, 받아쓰기 확인한 실제 소리 시작) − 0.09초
#  · 구조(민석 확정 11/2 20:1x): 표지(1) + 팀장 인삿말 클립 → 2 「이번 강의의 내용」(아나운서 없음, 나레이션만) → … →
#    27 = 팀장 끝인사 클립(자체 음성 0.9배가 클로징 나레이션을 대신 · 타입캐스트 27번 구간 안 씀) → 엔딩
import json, os
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
v2 = json.load(open("tl_v2.json"))                       # v2 타임라인(줄·장면·음성 조각 원본 시각)
ON = {int(k): v for k, v in json.load(open("onsets_v3.json")).items()}   # 줄 번호(1부터) → 0.9배 원본 음성 말 시작(초)
LEAD = 0.09; POST, PRE, QUIZ_WAIT, HOLD_END = 0.30, 1.00, 5.5, 3.5
GAP = POST + PRE - LEAD                                  # 말 끝 → 컷 1.21 (컷 → 말 0.09, 합 1.30 = v2 와 같음)
QUIZ = {17, 19, 21, 23, 25}
SELF = {15}                                              # 「스스로 확인하기」 화면 = 낭독 뒤 3초 대기(규칙 17, 민석 11/2 20:3x)
SELF_WAIT = 3.0
ANN = "../../아나운서/11강"
# 인삿말 자막 = 클립 받아쓰기, 고유 표기만 강의인삿말/audio_10 파일 이름대로(「마루시공전문가 민간자격」, 반장 결정 11/2)
# #8(11/2 20:2x): 하이젠 클립 소리 버림 → 소리 = 타입캐스트 0.9배, 클립 영상을 그 소리에 맞춰 다시 뽑음(warp_clip.py · 입싱크_방식.md)
#  인삿말 소리 = 강의인삿말/audio_10 atempo 0.9(greet_a10_090.wav) · 클립 = greet_warp.mp4(타깃 0초 = 클립 0.69초)
#  줄 시작 = 타깃 쉼 끝(0.49·1.529·4.340(「제」 앞 ㅈ 막힘 끝)·7.017·10.607) + 0.69
G = dict(clip="greet_warp.mp4", wav="greet_a10_090.wav", at=0.69, src_to=14.832, dur=16.163, voice_end=0.69 + 14.63,
         lines=[(1.180, "안녕하세요"), (2.219, "마루시공전문가 민간자격 온라인 강의"), (5.030, "제11강에 오신 여러분을 환영합니다"),
                (7.707, "11강에서는 패턴 시공을 조금 더 깊이 살펴보고"), (11.297, "기둥과 문틀 주변 등 복잡한 공간을 시공하는 방법을 배웁니다")],
         gain=1.072)                                     # −19.4 LUFS → 나레이션 −18.8(+0.6dB)
OPEN = dict(clip=f"{ANN}/11_오프닝_idle.mp4", idle=1.0)  # 클립 1.000초 = 0.9배 원본 0초
# 끝인사 소리 = 본문 v090.wav 773.085~789.598(타입캐스트 마무리 멘트, bye_tc_090.wav) · 클립 = bye_warp.mp4(타깃 0초 = 클립 1.36초)
#  줄 시작(클립초) = v2 검증 말 시작(원본 −773.085) + 1.36 : 0.05·3.222·6.424·10.900·12.931
BYE = dict(clip="bye_warp.mp4", wav="bye_tc_090.wav", at=1.36, src_to=16.513, dur=18.756, voice_end=1.36 + 16.47,
           on=[1.41, 4.582, 7.784, 12.26, 14.291], gain=1.0)
off2 = {s["slide"]: s.get("src_offset", 0) for s in v2["slides"]}
lines = []                                               # (줄번호, 장면, 글, 원본 말시작)
for x in v2["subs"]:
    lines.append(dict(n=x["n"], slide=x["slide"], text=x["text"], on=ON.get(x["n"], round(x["voice_on"] - off2[x["slide"]], 3))))
# v3 검사(scene_sub_check v3_결과 + lead_probe 받아쓰기)에서 앞 줄 말끝이 남은 채 뜬 줄 → 실측 말 시작으로 늦춤(초, src_n 기준)
#  16 「잊는」(긋고 끝 76.0) · 82·84·92·135·205 = 검사기 voice_t − 지금 voice_on
DELTA = {16: 0.22, 82: 0.156, 84: 0.236, 92: 0.196, 135: 0.10, 205: 0.25, 208: 0.175}
for l in lines:
    if l["n"] in DELTA: l["on"] = round(l["on"] + DELTA[l["n"]], 3)
src_end = {s["slide"]: round(s["voice_end"] - s["src_offset"], 3) for s in v2["slides"] if "voice_end" in s}
seg = {a["slide"]: a for a in v2["audio"]}

tl = {"slides": [], "subs": [], "audio": [], "anchors": []}
# --- 표지 + 인삿말 (클립 0초 = 영상 0초)
tl["audio"].append(dict(slide=1, out=G["at"], src_from=0.0, src_to=G["src_to"], src="work/" + G["wav"], gain=G["gain"]))
tl["anchors"].append(dict(name="인삿말", **{"in": 0.0, "clip": G["clip"], "clip_t0": 0.0}))
cut = q(G["dur"])        # 인삿말 클립 끝 = 표지→2 컷(손 위치 달라 컷 프레임에서 교체 · 클립 끝 뒤 정지 화면 금지 → 말 끝→컷 0.84, 말 사이 0.93 = 00강 표지→2 0.97)
for i, (t, txt) in enumerate(G["lines"]):
    tl["subs"].append(dict(slide=1, start=q(t - LEAD), voice_on=round(t, 3), text=txt, part="인삿말"))
tl["slides"].append(dict(slide=1, start=0.0, end=cut, note="표지 + 인삿말 아나운서"))

slides = sorted(set(l["slide"] for l in lines))
for k, s in enumerate(slides):
    ls = [l for l in lines if l["slide"] == s]
    if s == 27:                                           # 끝인사 클립: 원본 = 클립 시각
        for l, t in zip(ls, BYE["on"]): l["on"] = t
        a, b = BYE["on"][0], BYE["voice_end"]
    else:
        a = ls[0]["on"]; b = src_end[s]
    start = cut                                           # 이 장면 컷 = 첫 자막 시작
    off = start + LEAD - a                                # 출력 = 원본 + off
    if s == 27:
        tl["audio"].append(dict(slide=s, out=round(off + BYE["at"], 4), src_from=0.0, src_to=BYE["src_to"], src="work/" + BYE["wav"], gain=BYE["gain"]))
    else:
        s0 = max(a - 0.05, seg[s]["src_from"]) if s != 2 else 0.0
        s1 = seg[s]["src_to"]
        tl["audio"].append(dict(slide=s, out=round(s0 + off, 4), src_from=round(s0, 4), src_to=round(s1, 4)))
    for j, l in enumerate(ls):
        st = start if j == 0 else q(l["on"] + off - LEAD)
        tl["subs"].append(dict(slide=s, start=st, voice_on=round(l["on"] + off, 3), text=l["text"], src_n=l["n"]))
    wait = QUIZ_WAIT if s in QUIZ else (SELF_WAIT if s in SELF else (HOLD_END if s == slides[-1] else GAP))
    end = q(b + off + wait)
    tl["slides"].append(dict(slide=s, start=start, end=end, voice_start=round(a + off, 3), voice_end=round(b + off, 3),
                             gap_after_voice=round(end - (b + off), 3), gap_before_voice=round(a + off - start, 3),
                             quiz_wait=s in QUIZ, self_check_wait=s in SELF, src_offset=round(off, 4)))
    if s == 27:
        tl["anchors"].append(dict(name="끝인사", **{"in": start, "clip": BYE["clip"], "clip_t0": round(off, 4), "out": q(off + BYE["dur"])}))
    cut = end
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1
    x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut
T = cut
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
tl["params"] = dict(LEAD=LEAD, GAP_voice_to_cut=GAP, cut_to_voice=LEAD, QUIZ_WAIT=QUIZ_WAIT, SELF_WAIT=SELF_WAIT, HOLD_END=HOLD_END,
                    voice="v090.wav(11강 0.9배)", greet=G["wav"], bye=BYE["wav"], 입싱크="#8 warp_clip.py", bgm="BGM/Approxima.mp3 -20dB", 구조="민석 확정: 2번 아나운서 없음 · 27번 = 끝인사 클립(영상만, 소리 = 타입캐스트 마무리 멘트)")
json.dump(tl, open("../타임라인_v3.json", "w"), ensure_ascii=False, indent=1)
print("자막", len(tl["subs"]), "총길이", tl["total"])
for x in tl["slides"]: print(x["slide"], round(x["start"], 3), round(x["end"], 3), x.get("gap_before_voice"), x.get("gap_after_voice"))
