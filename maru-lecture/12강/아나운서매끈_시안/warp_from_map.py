# 오더30: 시안 지도(map_*.json)로 끝인사 클립 다시 뽑기 — 11강 warp_clip.py 의 프레임 고르기 그대로(지도만 바꿈)
import sys, json, subprocess, numpy as np
mp, out = sys.argv[1:3]; d = json.load(open(mp)); B = "../인삿말/12_끝인사_090.mp4"
m = np.array(d["map"]); tau, cl = m[:, 0], m[:, 1]; cs, ce = d["clip_speech"]; ts, te = d["target_speech"]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", B], capture_output=True, text=True).stdout)
spk = te - ts; FPS = 30000 / 1001
def c_of_u(u):
    if u < cs: return u
    if u < cs + spk: return cs + float(np.interp(u - cs, tau, cl))
    return ce + (u - cs - spk)
W, H = 1080, 1920; FS = W * H * 3
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", B, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=FS)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30000/1001", "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
cur, frame, used = -1, None, []
for k in range(int(round(d["out_dur"] * FPS))):
    want = int(c_of_u(k / FPS) * 22.5 + 1e-6)
    while cur < want:
        b = dec.stdout.read(FS)
        if len(b) < FS: break
        frame = b; cur += 1
    used.append(cur); enc.stdin.write(frame)
enc.stdin.close(); enc.wait(); dec.kill()
u = np.diff(used); print("frames", len(used), "건너뜀(2칸↑)", int((u >= 2).sum()), "멈춤", int((u == 0).sum()))
