# 09강 v7 (오더52 · 11/9 민석: 2장 「첫 줄이 … 하고」 지직거림 → 음성/9강 음성 수정본.wav 로 교체) = 타임라인_v6b + 그 구간 소리만 새 음성
#  새 음성: v7/new_raw.wav(원본 복사, sha 52200190) → atempo=0.9 · 48k mono(v7/new_090.wav) → 0~3.52 · gain −3.3dB(옛 v090 구간 11.92~16.16 과 RMS −0.2 / LUFS +0.6) · 앞 5ms 페이드인 · 뒤 15ms 페이드아웃 → v7/fix_090.wav
#  자리: 옛 말 v090 11.95~16.145 (out 27.489~31.684) → 새 말 0.050~3.500. 뒤 「넘어가는」 앞 쉼(말끝 16.145 → 16.24) 그대로 = 새 말끝을 옛 말끝 + Δ 에 맞춤.
#  Δ = −22프레임(−0.734067, 원래 차 −0.744 를 프레임 격자로 · 남는 10ms 는 앞 문장끝 쉼 쪽) · 그 뒤 전부 Δ 만큼 당김(장 컷·자막·아나운서·엔딩·길이)
import json, os, subprocess
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); W = f"{L}/work"
FPS = 30000 / 1001; D = round(-22 / FPS, 6); G = -3.3
OFF = 27.0089 - 11.47                       # v6b 2장 셋째 조각 out − src
NEW_ON, NEW_END, NEW_LEN = 0.050, 3.500, 3.520
OLD_END = 16.145; T_NEW = round(OLD_END + OFF + D - NEW_END, 6)       # 새 조각 out 시작
SPLIT = 31.0                                  # 이 out 뒤(옛 시각)는 Δ 만큼 당김 — 옛 말끝 31.684 · 「넘어가는」 31.78 사이가 아니라 31.0 이후 첫 대상부터
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/v7/new_090.wav", "-af",
                f"atrim=0:{NEW_LEN},asetpts=PTS-STARTPTS,volume={G}dB,afade=t=in:st=0:d=0.005,afade=t=out:st={NEW_LEN - 0.015}:d=0.015",
                "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", f"{W}/v7/fix_090.wav"], check=True)
tl = json.load(open(f"{L}/타임라인_v6b.json"))
sh = lambda t: round(t + D, 6)
# ---- 오디오
A = []
for a in tl["audio"]:
    if a["slide"] == 2 and abs(a["out"] - 27.0089) < 1e-6:
        a1 = dict(a, src_to=round(T_NEW - OFF, 6))
        a2 = dict(slide=2, out=T_NEW, src_from=0.0, src_to=NEW_LEN, src="../중간점_새음성/09_2장.wav", gain=1.0, note="오더52 새 음성(9강 음성 수정본 0.9배 · −3.3dB)")
        tail_out = round(T_NEW + NEW_LEN, 6); a3 = dict(a, out=tail_out, src_from=round(tail_out - D - OFF, 6))
        A += [a1, a2, a3]
    elif a["out"] > 27.1: A.append(dict(a, out=sh(a["out"])))
    else: A.append(a)
tl["audio"] = A
# ---- 장
for s in tl["slides"]:
    if s["slide"] >= 3:
        s["start"] = sh(s["start"]); s["voice_start"] = sh(s["voice_start"]); s["src_offset"] = sh(s["src_offset"])
    if s["slide"] >= 2:
        s["end"] = sh(s["end"]); s["voice_end"] = sh(s["voice_end"])
# ---- 자막
for x in tl["subs"]:
    if x["n"] == 9:
        x["voice_on"] = round(T_NEW + NEW_ON, 3); x["start"] = round(x["voice_on"] - 0.09, 6)
        x["how"] = "v7 새 음성(오더52) 실소리 −0.09"; x["v090_on_note"] = "v090_on 11.95 = 옛 음성 자리(이 문장 소리는 ../중간점_새음성/09_2장.wav 0.050~)"
    elif x["n"] >= 10:
        x["start"] = sh(x["start"]); x["voice_on"] = round(x["voice_on"] + D, 3)
        if x["n"] == 10: x["how"] = x["how"] + " · v7 Δ 당김(실소리 −0.09)"
    if x["n"] >= 8: x["end"] = sh(x["end"])
S = tl["subs"]
for i in range(1, len(S)):
    if S[i]["slide"] == S[i - 1]["slide"]: S[i - 1]["end"] = S[i]["start"]
# ---- 아나운서 · 엔딩 · 길이
for an in tl["anchors"]:
    if an["name"] == "끝인사":
        for k in ("in", "clip_t0", "out"): an[k] = sh(an[k])
E = tl["ending"]
for k in ("zoom_blur", "card", "black"): E[k] = [sh(t) for t in E[k]]
for k in ("logo_off", "bye_freeze"): E[k] = sh(E[k])
tl["total"] = sh(tl["total"])
tl["params"]["v7"] = f"오더52: 2장 n9 「첫 줄이…하고」 소리 = 9강 음성 수정본 0.9배(../중간점_새음성/09_2장.wav = work/v7/fix_090.wav 같은 파일, {G}dB · 오더38 14강 방식 자리) · 그 뒤 전부 Δ{D}(−22프레임) · 그 외 v6b 와 같음"
json.dump(tl, open(f"{L}/타임라인_v7.json", "w"), ensure_ascii=False, indent=1)
print("D", D, "T_NEW", T_NEW, "n9", S[8]["start"], S[8]["voice_on"], "n10", S[9]["start"], S[9]["voice_on"], "total", tl["total"])
for a in A[2:7]: print(a)
