# 오더24 끝 검정 검사: 마지막 0.9초 안 프레임 3장 평균 밝기 ≤2 · 길이 = 타임라인 total(±2프레임) · 마지막 영상 PTS 역행 없음
import sys, json, subprocess, numpy as np
mp4, tlp = sys.argv[1], sys.argv[2]; T = json.load(open(tlp))["total"]
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], capture_output=True, text=True).stdout)
pts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "packet=pts_time", "-of", "csv=p=0", "-read_intervals", f"{T-3}%", mp4], capture_output=True, text=True).stdout.split()
pts = [float(x) for x in pts if x and x != "N/A"]; back = sum(1 for a, b in zip(pts, pts[1:]) if b < a - 1.0)
br = []
for t in (T - 0.8, T - 0.45, T - 0.1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=192:108,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    br.append(round(float(np.frombuffer(raw, np.uint8).mean()), 1) if raw else None)
ok = all(b is not None and b <= 2 for b in br) and abs(d - T) <= 2 / 29.97 and back == 0 and pts and max(pts) > T - 0.2
print(f"끝검정 {'통과' if ok else '걸림'} · 밝기 {br} · 길이 {d:.3f} / 타임라인 {T} · 마지막 PTS {max(pts) if pts else None} · PTS 역행 {back}")
sys.exit(0 if ok else 1)
