# 09강 v7b (오더52 · cx 돌려보냄 11/9: 새 문장 출력 −2.3 LU) = 타임라인_v7 에서 새 조각 게인만 −3.3 → −0.7dB
#  원인: render09 aformat mono 가 스테레오 v090 을 +3.01dB(L+R) 로 만듦 · 새 조각은 모노라 그대로 → v7 측정(채널 평균)이 3dB 어긋남
#  −0.7 = 렌더 경로 그대로 잰 값(work/v7/est.py): 옛 v090 문장 LUFS −22.1 / 새 −21.9(+0.2) · 5ms 발화칸 RMS −0.39 · 피크 −1.63dBFS(렌더 VOICE_GAIN −1.2 앞)
import json, os, subprocess
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); W = f"{L}/work"; G = -0.7; NEW_LEN = 3.520
OUT = f"{L}/../중간점_새음성/09_2장b.wav"
assert not os.path.exists(OUT) or os.environ.get("REDO")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/v7/new_090.wav", "-af",
                f"atrim=0:{NEW_LEN},asetpts=PTS-STARTPTS,volume={G}dB,afade=t=in:st=0:d=0.005,afade=t=out:st={NEW_LEN - 0.015}:d=0.015",
                "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", OUT], check=True)
tl = json.load(open(f"{L}/타임라인_v7.json"))
for a in tl["audio"]:
    if a.get("src") == "../중간점_새음성/09_2장.wav":
        a["src"] = "../중간점_새음성/09_2장b.wav"; a["note"] = f"오더52 v7b 새 음성(9강 음성 수정본 0.9배 · {G}dB · 렌더 mono 경로로 맞춤)"
tl["params"]["v7b"] = f"cx 돌려보냄(출력 −2.3 LU): 새 조각 게인 −3.3 → {G}dB(../중간점_새음성/09_2장b.wav) · 그 외 v7 와 같음"
json.dump(tl, open(f"{L}/타임라인_v7b.json", "w"), ensure_ascii=False, indent=1)
print("ok", sum(1 for a in tl["audio"] if a.get("src", "").endswith("09_2장b.wav")))
