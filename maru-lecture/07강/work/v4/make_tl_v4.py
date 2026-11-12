# 07강 v4 (오더53 · 11/11 민석) = 타임라인_v3 + ① 8장 n90(오더 #89) 「접착과 결합 구조는 뒤에서 하자 원인을…」 소리 = 음성/마루시공 7강 나레이션 수정.wav 0.9배
#   ② 9장 n108/n109(오더 #107/#108) 넘김: 「제품의 보관과」 → n109 로 · n109 시작 = 「제품의」 실소리 −0.09
#  새 음성: v4/new_raw.wav(원본 복사 sha256 ca84034a) → atempo=0.9 · 48k mono(v4/new_090.wav) → 0~4.40 · gain G · 앞 5ms/뒤 15ms 페이드 → v4/fix_090.wav
#  v090·새 조각 둘 다 모노 → render07 aformat mono 에서 게인 변화 없음(09강 v7 스테레오 함정 없음). 게인은 최종 mp4 (L+R)/2 로 다시 잼(out_loud.py)
#  자리(5ms RMS −40dB): 옛 말 v090 330.56~334.905(out 377.454~381.799, 4.345초) · 새 말 0.06~4.34(4.28초) → 차 −0.065 → Δ = −1프레임(아래)
#  새 말끝 = 옛 말끝 + Δ(→ 장 끝 텀 1.71 그대로) · 🆕1차(−1프레임) gap_check silencedetect 앞 문장끝 쉼 1.498 미달 → Δ = −1프레임(앞 쉼 ≈1.53)
#  새 조각 자리 = ../중간점_새음성/07_8장.wav(= work/v4/fix_090.wav 같은 파일 · announcer 검사기 자리, 09강 v7 방식)
import json, os, subprocess, sys
L = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = f"{L}/work"
FPS = 30000 / 1001; D = round(-1 / FPS, 6); G = float(sys.argv[1]) if len(sys.argv) > 1 else -0.8
P_OUT, P_SRC, P_TO = 376.9738, 330.0795, 334.9607          # v3 8장 마지막 조각
OFF = P_OUT - P_SRC
NEW_ON, NEW_END, NEW_LEN = 0.055, 4.34, 4.40
OLD_END = 334.905; T_NEW = round(OLD_END + OFF + D - NEW_END, 6)
SPLIT = 381.0                                               # 이 뒤(v3 시각) = Δ 이동
FIX = f"{W}/v4/fix_090.wav"
if not os.path.exists(FIX) or os.environ.get("REDO"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/v4/new_090.wav", "-af",
        f"atrim=0:{NEW_LEN},asetpts=PTS-STARTPTS,volume={G}dB,afade=t=in:st=0:d=0.005,afade=t=out:st={NEW_LEN - 0.015}:d=0.015",
        "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", FIX], check=True)
tl = json.load(open(f"{L}/타임라인_v3.json"))
sh = lambda t: round(t + D, 6)
A = []
for a in tl["audio"]:
    if abs(a["out"] - P_OUT) < 1e-6:
        A.append(dict(a, src_to=round(T_NEW - OFF, 6)))
        A.append(dict(slide=8, out=T_NEW, src_from=0.0, src_to=NEW_LEN, src="../중간점_새음성/07_8장.wav", gain=1.0, note=f"오더53 새 음성(7강 나레이션 수정 0.9배 · {G}dB)"))
    elif a["out"] > SPLIT: A.append(dict(a, out=sh(a["out"])))
    else: A.append(a)
tl["audio"] = A
for s in tl["slides"]:
    if s["slide"] >= 9:
        for k in ("start", "voice_start", "src_offset"): s[k] = sh(s[k])
    if s["slide"] >= 8:
        s["end"] = sh(s["end"]); s["voice_end"] = sh(s["voice_end"])
# 「제품의」 실소리: v090 395.325(5ms RMS 쉼 394.95~395.325 끝 · 앞 창 「…되는지도」/뒤 창 「제품의 보관과…」) → v3 out
p9 = [a for a in A if a["slide"] == 9 and a["src_from"] <= 395.325 < a["src_to"]][0]
JE_ON = round(p9["out"] + 395.325 - p9["src_from"], 3)        # 이미 Δ 들어간 out
for x in tl["subs"]:
    n = x["n"]
    if n == 90:
        x["voice_on"] = round(T_NEW + NEW_ON, 3); x["start"] = round(x["voice_on"] - 0.09, 6); x["how"] = "v4 새 음성(오더53) 실소리 −0.09"
    elif n >= 91:
        x["start"] = sh(x["start"]); x["voice_on"] = round(x["voice_on"] + D, 3)
    if n == 108: x["text"] = "남은 재료를 다음에 사용해도 되는지도"; x["v4"] = "오더53 추가: 「제품의 보관과」 → n109"
    if n == 109:
        x["text"] = "제품의 보관과 사용 지침으로 확인합니다"; x["voice_on"] = JE_ON; x["start"] = round(JE_ON - 0.09, 6)
        x["how"] = "v4 「제품의」 실소리 −0.09(v090 395.325 · 쉼 끝)"; x["v4"] = "오더53 추가: 넘김 「되는지도 /」"
    if n >= 89: x["end"] = sh(x["end"])
S = tl["subs"]
for i in range(1, len(S)):
    if S[i]["slide"] == S[i - 1]["slide"]: S[i - 1]["end"] = S[i]["start"]
for an in tl["anchors"]:
    if an["name"] == "끝인사":
        for k in ("in", "clip_t0", "out"): an[k] = sh(an[k])
E = tl["ending"]
for k in ("zoom_blur", "card", "black"): E[k] = [sh(t) for t in E[k]]
for k in ("logo_off", "bye_freeze"): E[k] = sh(E[k])
tl["total"] = sh(tl["total"])
tl["params"]["v4"] = f"오더53: 8장 n90 소리 = 7강 나레이션 수정 0.9배(work/v4/fix_090.wav, {G}dB) · 그 뒤 Δ{D}(−1프레임) · 9장 n108/n109 넘김 「되는지도 / 제품의」 · 그 외 v3 와 같음"
json.dump(tl, open(f"{L}/타임라인_v4.json", "w"), ensure_ascii=False, indent=1)
print("D", D, "T_NEW", T_NEW, "JE_ON", JE_ON, "total", tl["total"])
for x in S[87:92] + S[106:110]: print(x["n"], round(x["start"],3), x["voice_on"], round(x["end"],3), x["text"])
for s in tl["slides"][6:9]: print(s["slide"], s["start"], s["end"], s["voice_end"])
