# (오더34 19·20강 v4 사본: 파일 이름 v4→v4 만 바꿈 · 원본 오더25)
# p9 보강: 아나운서 등장(마지막 장 컷)·퇴장(표지→2번 컷) 경계 ±2프레임 — 프레임마다 보이는 장(앞/뒤 슬라이드 중 가까운 쪽, 아나운서·자막바·로고 자리 빼고)과
#  아나운서 유무(아나운서 자리에서 그 장 원본과 다른 화소 > 4000)를 재서 「아나운서 있음 ⇔ 아나운서 장」인지
import sys, json, subprocess, numpy as np
from PIL import Image
N = sys.argv[1]; D = f"{N}강"; tl = json.load(open(f"{D}/타임라인_v4.json")); V = f"{D}/{D}_v4.mp4"; FPS = 30000 / 1001
S = sorted(tl["slides"], key=lambda s: s["slide"]); L = S[-1]["slide"]; A = {a["name"]: a for a in tl["anchors"]}
def png(n): return np.asarray(Image.open(f"{D}/slides/s-{n:02d}.png").convert("RGB"), np.int16)
def frame(k):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(k - 0.4) / FPS:.5f}", "-i", V, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout   # pts ≥ (k−0.4)/fps 첫 프레임 = k번
    return np.frombuffer(b, np.uint8).reshape(1080, 1920, 3).astype(np.int16)
cases = [("인삿말 퇴장(표지→2)", 1, 2, A["인삿말"], 788, S[1]["start"], 1), ("끝인사 등장(%d→%d)" % (L - 1, L), L - 1, L, A["끝인사"], 799, S[-1]["start"], L)]
bad = 0; out = []
for name, pa, pb, a, w, tcut, ann_slide in cases:
    Pa, Pb = png(pa), png(pb); x0 = a["x"]; m = np.ones((1080, 1920), bool); m[:, max(0, x0):x0 + w] = False; m[880:] = False; m[:150, 1540:] = False
    am = np.zeros((1080, 1920), bool); am[40:880, max(0, x0 + 150):x0 + w - 150] = True
    kc = int(round(tcut * FPS))
    for k in range(kc - 2, kc + 3):
        f = frame(k); da = np.abs(f - Pa).max(2)[m].mean(); db = np.abs(f - Pb).max(2)[m].mean()
        sl = pa if da < db else pb; ref = Pa if sl == pa else Pb
        ann = int((np.abs(f - ref).max(2)[am] > 40).sum()) > 4000
        ok = ann == (sl == ann_slide); bad += not ok
        out.append(dict(case=name, frame=k, t=round(k / FPS, 3), slide=int(sl), announcer=ann, ok=ok))
for o in out: print(N, o)
print(N, "경계 ±2프레임", "통과" if not bad else f"걸림 {bad}")
json.dump(out, open(f"{D}/검사_v4/경계16.json", "w"), ensure_ascii=False); sys.exit(1 if bad else 0)
