# 05강 v4 (오더54 · 11/11 민석 「5강 이 음성으로 교체」) = 타임라인_v3 + 3장 #21(n22) 「공구의 안전커버와 날, 고정 상태를 확인하고」 소리 = 음성/5강 나레이션 수정본.wav 0.9배
#  새 음성: v4/new_raw.wav(원본 복사 sha256 814d24ff) → atempo=0.9 · 48k **stereo(L=R, v090 과 같은 채널 구성)** (v4/new_090.wav = ../../중간점_새음성/05강_수정_090.wav)
#   → 0~3.53 · gain G · 앞 5ms/뒤 15ms 페이드 → ../../중간점_새음성/05_3장.wav (= v4/fix_090.wav)
#  v090·새 조각 둘 다 스테레오 L=R → render05 71줄 aformat mono 다운믹스를 똑같이 탐(+3.01dB 차 없음). 게인은 최종 mp4 (L+R)/2 로 다시 잼(out_loud.py)
#  자리(5ms RMS −40dB): 옛 말 v090 56.44~59.51(3.07초) · 새 말 0.055~3.495(3.44초) → +0.37
#   #20 문장끝→#21 쉼 v3 1.534(≥1.53 경계) → #21 실소리 그대로 · #21 말끝→#22 쉼(문장 안, 원래 0.370) 은 Δ=11프레임(0.367033)으로 0.365
#   새 조각 뒤 = v090 59.545~(옛 말끝 −40 뒤 −70 무음)부터 이어 붙임 → #22 와 그 뒤 전부 Δ
import json, os, subprocess, sys
L = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); W = f"{L}/work"; NS = os.path.dirname(L) + "/중간점_새음성"
FPS = 30000 / 1001; D = round(11 / FPS, 6); G = float(sys.argv[1]) if len(sys.argv) > 1 else 1.7
P_OUT, P_SRC, P_TO = 78.4919, 55.9363, 62.6926                 # v3 3장 마지막 조각
OFF = P_OUT - P_SRC
OLD_ON, OLD_END = 56.44, 59.51; NEW_ON, NEW_END, NEW_LEN = 0.055, 3.495, 3.53
T_NEW = round(OLD_ON + OFF - NEW_ON, 6)                        # 새 실소리 = 옛 실소리 자리
C_OUT = round(T_NEW + NEW_LEN, 6)                              # 이어 붙일 v090 조각 출력 시각
C_SRC = round(C_OUT - (P_OUT + D) + P_SRC, 6)                  # 그 조각 원음 시작(Δ 뒤 시각과 맞춤)
SPLIT = 80.0                                                    # 이 뒤(v3 시각) = Δ 이동
FIX = f"{NS}/05_3장.wav"
if not os.path.exists(FIX) or os.environ.get("REDO"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{NS}/05강_수정_090.wav", "-af",
        f"atrim=0:{NEW_LEN},asetpts=PTS-STARTPTS,volume={G}dB,afade=t=in:st=0:d=0.005,afade=t=out:st={NEW_LEN - 0.015}:d=0.015",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", FIX], check=True)
tl = json.load(open(f"{L}/타임라인_v3.json"))
sh = lambda t: round(t + D, 6)
A = []
for a in tl["audio"]:
    if abs(a["out"] - P_OUT) < 1e-6 and not a.get("src"):
        A.append(dict(a, src_to=round(T_NEW - OFF, 6)))
        A.append(dict(slide=3, out=T_NEW, src_from=0.0, src_to=NEW_LEN, src="../중간점_새음성/05_3장.wav", gain=1.0, note=f"오더54 새 음성(5강 나레이션 수정본 0.9배 · {G:+}dB)"))
        A.append(dict(slide=3, out=C_OUT, src_from=C_SRC, src_to=P_TO, note="오더54: 새 조각 뒤 v090 이어 붙임(#21→#22 쉼 원래대로)"))
    elif a["out"] > SPLIT: A.append(dict(a, out=sh(a["out"])))
    else: A.append(a)
tl["audio"] = A
for s in tl["slides"]:
    if s["slide"] >= 4:
        for k in ("start", "voice_start", "src_offset"): s[k] = sh(s[k])
    if s["slide"] >= 3:
        s["end"] = sh(s["end"]); s["voice_end"] = sh(s["voice_end"])
for x in tl["subs"]:
    n = x["n"]
    if n == 22:
        x["voice_on"] = round(T_NEW + NEW_ON, 3); x["start"] = round(x["voice_on"] - 0.09, 6); x["how"] = "v4 새 음성(오더54) 실소리 −0.09"; x["v4"] = "오더54 소리 교체"
    elif n >= 23:
        x["start"] = sh(x["start"]); x["voice_on"] = round(x["voice_on"] + D, 3)
    if n >= 22: x["end"] = sh(x["end"])
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
tl["params"]["v4"] = f"오더54: 3장 #21(n22) 소리 = 5강 나레이션 수정본 0.9배 stereo(중간점_새음성/05_3장.wav, {G:+}dB) · 그 뒤 Δ{D}(+11프레임) · 그 외 v3 와 같음"
json.dump(tl, open(f"{L}/타임라인_v4.json", "w"), ensure_ascii=False, indent=1)
print("D", D, "T_NEW", T_NEW, "C_OUT", C_OUT, "C_SRC", C_SRC, "total", tl["total"])
for x in S[19:25]: print(x["n"], round(x["start"],3), x["voice_on"], round(x["end"],3), x["text"])
for s in tl["slides"][1:5]: print(s["slide"], s["start"], s["end"], s["voice_end"])
for a in A: 
    if 70 < a["out"] < 100: print(a)
