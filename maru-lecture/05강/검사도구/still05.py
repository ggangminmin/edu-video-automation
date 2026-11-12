# 05강 사본(오더44)
# (오더34 19·20강 v4c 사본: 파일 이름 v4→v4c 만 바꿈 · 원본 오더25)
# scene_sub_check ④(등장 첫 15프레임 정지) 를 실제 아나운서 자리에서 같은 잣대로: 회색 · 420x840 영역을 210x420 로 · 프레임 차분 평균 < 0.1 연속 최대
#  (검사기는 영역을 x1130~1550 에 고정 → 표지 아나운서를 옮기면(오더16) 빈 슬라이드를 재서 정지 15 로 나옴)
import sys, json, subprocess, numpy as np
N = "05"; VER = sys.argv[1]; tl = json.load(open(f"{N}강/타임라인_{VER}.json")); V = f"{N}강/{N}강_{VER}.mp4"; FPS = 30000 / 1001
res = {}
for a in tl["anchors"]:
    w = 788 if a["name"] == "인삿말" else 799; cx = a["x"] + int(w * 0.51)          # 몸 가운데 ≈ 캔버스 51%
    x0 = max(0, cx - 210); f0 = int(round(a["in"] * FPS))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{f0 / FPS:.4f}", "-i", V, "-frames:v", "17", "-vf", f"format=gray,crop=420:840:{x0}:60,scale=210:420",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 420, 210).astype(np.int16); d = np.abs(np.diff(f, axis=0)).mean((1, 2))[:16]
    r = m = 0
    for v in d[1:16]: r = r + 1 if v < 0.1 else 0; m = max(m, r)
    res[a["name"]] = dict(x=a["x"], crop_x=x0, still=m, diffs=[round(float(v), 2) for v in d[1:16]])
print(N, {k: (v["x"], v["still"]) for k, v in res.items()})
json.dump(res, open(f"{N}강/검사_{VER}/정지16.json", "w"), ensure_ascii=False)
