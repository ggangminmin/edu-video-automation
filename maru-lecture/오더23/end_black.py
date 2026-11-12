# 오더24 끝 검정 검사: NN강_v3b.mp4 마지막 0.9초 안 프레임 3장 밝기(평균) ≤ 2 · 길이 = 타임라인 total(±1프레임) · 마지막 PTS 역행 없음
import sys, json, subprocess, numpy as np
N = sys.argv[1]; V = f"{N}강/{N}강_v3b.mp4"; T = json.load(open(f"{N}강/타임라인_v3b.json"))["total"]
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", V], capture_output=True, text=True).stdout)
br = []
for t in (d - 0.8, d - 0.5, d - 0.15):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", V, "-frames:v", "1", "-vf", "scale=192:108", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    br.append(round(float(np.frombuffer(r, np.uint8).mean()), 1) if r else None)
pts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "packet=pts_time", "-of", "csv=p=0", V], capture_output=True, text=True).stdout.split()
pts = [float(x) for x in pts if x]; back = sum(1 for a, b in zip(pts, pts[1:]) if b < a - 1)   # 디코드 순서 B프레임 소폭 역행은 무시, 1초 넘게 역행만
ok = all(b is not None and b <= 2 for b in br) and abs(d - T) <= 1.5 / 29.97 + 0.05 and back == 0
print(f"{N}강 v3b 끝 밝기 {br} · 길이 {d:.3f} / 타임라인 {T} · 마지막 PTS {max(pts):.3f} · 큰 역행 {back} → {'통과' if ok else '걸림'}")
sys.exit(0 if ok else 1)
