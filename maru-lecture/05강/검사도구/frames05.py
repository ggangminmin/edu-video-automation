# 05강 사본(오더44 · 20강 chk_v4c/check16_frames.py): 렌더 mp4 표지·마지막 장 6프레임씩 아나운서 ∩ 사진·글자 = 0(압축 여유 300px)
import sys, json, subprocess, numpy as np
from PIL import Image
VER = sys.argv[1]; sys.argv = ["x", VER]
exec(open("05강/work/place05.py").read().split("def alpha")[0])
V = f"{D}/{D}_{VER}.mp4"; S = {s["slide"]: s for s in tl["slides"]}; bad = 0; rows = []
for k, sn in (("인삿말", 1), ("끝인사", L)):
    a = [x for x in tl["anchors"] if x["name"] == k][0]; t0 = max(S[sn]["start"], a["in"]) + 0.3; t1 = min(S[sn]["end"], a.get("out", S[sn]["end"])) - 0.6
    C = content(sn); ref = np.asarray(Image.open(f"{D}/slides/s-{sn:02d}.png").convert("RGB"), np.int16)
    for t in np.linspace(t0, t1, 6):
        f = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", V, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout, np.uint8).reshape(1080, 1920, 3).astype(np.int16)
        d = np.abs(f - ref).max(2) > 40; d[900:] = False; d[:150, 1540:] = False
        ov = int((d & C).sum()); bad += ov > 300; rows.append((k, round(float(t), 2), ov, int((d & ~C).sum())))
print(9, "걸림" if bad else "통과", rows)
json.dump(dict(result="걸림" if bad else "통과", rows=rows), open(f"{D}/검사_{VER}/배치16_프레임.json", "w"), ensure_ascii=False)
sys.exit(1 if bad else 0)
