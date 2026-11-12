# (오더34 19·20강 v3 사본: 파일 이름 v4→v3 만 바꿈 · 원본 오더25)
# 오더16 7번: 렌더 mp4 의 표지(인삿말)·마지막 장(끝인사) 구간에서 6프레임씩 뽑아, 슬라이드 원본과 다른 곳(=아나운서, y<900·로고 자리 제외) ∩ 사진·글자 영역 = 0 픽셀인지
import sys, json, subprocess, numpy as np
from PIL import Image
N = int(sys.argv[1]); sys.argv = ["x", str(N)]
exec(open("07강/work/chk_v3/place16.py").read().split("def alpha")[0])
V = f"{D}/{D}_v3.mp4"; S = {s["slide"]: s for s in tl["slides"]}; bad = 0; rows = []
for k, sn in (("인삿말", 1), ("끝인사", L)):
    a = [x for x in tl["anchors"] if x["name"] == k][0]; t0 = max(S[sn]["start"], a["in"]) + 0.3; t1 = min(S[sn]["end"], a.get("out", S[sn]["end"])) - 0.6
    C = content(sn); ref = np.asarray(Image.open(f"{D}/slides/s-{sn:02d}.png").convert("RGB"), np.int16)
    for t in np.linspace(t0, t1, 6):
        f = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", V, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout, np.uint8).reshape(1080, 1920, 3).astype(np.int16)
        d = np.abs(f - ref).max(2) > 40; d[900:] = False; d[:150, 1540:] = False            # 자막바·로고 자리 빼고
        ann = d & ~C                                        # 아나운서가 빈 곳에 그려진 화소(있는지 확인용)
        ov = int((d & C).sum()); bad += ov > 300            # 압축 잡음 여유 300px
        rows.append((k, round(float(t), 2), ov, int(ann.sum())))
print(N, "걸림" if bad else "통과", rows)
json.dump(dict(result="걸림" if bad else "통과", rows=rows), open(f"{D}/검사_v3/배치16_프레임.json", "w"), ensure_ascii=False)
sys.exit(1 if bad else 0)
