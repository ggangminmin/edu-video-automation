# 출력 시각 구간의 깨끗한 음성(타임라인 audio 표대로) 음량 곡선 20ms + 그 구간 자막
import sys, json, numpy as np, librosa
N, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
tl = json.load(open(f"{N}강/타임라인_v2.json"))
for a in tl["audio"]:
    src = f"{N}강/" + (a["src"] if a.get("src") else "work/v090.wav")
    a0, a1 = a["out"], a["out"] + a["src_to"] - a["src_from"]
    if a1 < t0 or a0 > t1: continue
    s0 = a["src_from"] + max(0, t0 - a0); y, _ = librosa.load(src, sr=16000, offset=s0, duration=min(t1, a1) - max(t0, a0))
    db = 20 * np.log10(np.sqrt(librosa.util.frame(np.pad(y, (0, 320)), frame_length=320, hop_length=320) ** 2).mean(0) + 1e-7)
    base = max(t0, a0)
    print(f"slide {a['slide']} src {src.split('/')[-1]} @{s0:.2f}")
    print(" ".join(f"{base + i * 0.02:.2f}:{d:.0f}" for i, d in enumerate(db)))
for x in tl["subs"]:
    if x["end"] > t0 and x["start"] < t1: print("SUB", x["n"], round(x["start"], 3), round(x["voice_on"], 3), x["text"])
