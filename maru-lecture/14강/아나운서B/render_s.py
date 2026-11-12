# 14강 클로징 B(flow) 시안 — 13강 render_s.py 복사 구간 렌더 = render_v3b.py 영상 부분만(소리 mix_v3b.wav · 슬라이드/자막 concat 은 v3b 것 그대로 읽기만) · 아나운서 클립만 바꿈
# 실행(cwd=13강/work): CLIP_G=<인삿말 클립> CLIP_K=<끝인사 클립> SEG=a,b OUT=<mp4> python3 ../아나운서시안/render_s.py
import json, os, subprocess
tl = json.load(open("../타임라인_v3.json")); LAST = tl["slides"][-1]["slide"]
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
HF = 0.5 / FPS
end = tl["ending"]; TOTAL = q(tl["total"])
for a in tl["anchors"]:
    if a["name"] == "인삿말" and os.environ.get("CLIP_G"): a["clip"] = os.environ["CLIP_G"]
    if a["name"] == "끝인사" and os.environ.get("CLIP_K"): a["clip"] = os.environ["CLIP_K"]
# ---------- 영상 (v3: 인삿말 · 오프닝 idle · 클로징 idle — 등장 순간부터 움직임)
A = {a["name"]: a for a in tl["anchors"]}
s2 = next(s for s in tl["slides"] if s["slide"] == 2); s27 = next(s for s in tl["slides"] if s["slide"] == LAST)
gr_out = q(s2["start"])
cl_in, cl_out = q(s27["start"]), A["끝인사"]["out"]
def KEY(t, col="0x00FE05"): return (f"chromakey={col}:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[{t}c][{t}m];"
                    f"[{t}m]alphaextract,erosion,erosion,gblur=sigma=1.2[{t}a];[{t}c][{t}a]alphamerge")
ZB0, ZB1 = q(end["zoom_blur"][0]), q(end["zoom_blur"][1])
LOGO_OFF = q(end["logo_off"])

vf = [
 "[0:v]fps=30000/1001,format=yuv420p,setsar=1[sl]",
 f"[8:v]fps=30000/1001,{KEY('g','0x01FA04')},scale=788:1402,crop=700:1402:0:0,setpts=PTS-STARTPTS[ag]",
 "[1:v]nullsink",
 f"[2:v]fps=30000/1001,{KEY('k','0x01FA04')},scale=799:1421,crop=700:1421:0:0,setpts=PTS-STARTPTS+{A['끝인사']['clip_t0']}/TB,fade=t=out:st={cl_out-0.5:.3f}:d=0.5:alpha=1[ac]",
 f"[sl][ag]overlay=x={A['인삿말'].get('x', 934)}:y={A['인삿말'].get('y', 40)}:eof_action=pass:enable='lt(t,{gr_out-HF})'[v0]",
 f"[v0][ac]overlay=x={A['끝인사'].get('x', 952)}:y={A['끝인사'].get('y', 36)}:eof_action=pass:enable='between(t,{cl_in-HF},{cl_out-HF})'[v2]",
 f"[v2][sbt]overlay=enable='between(t,{q(tl['subs'][0]['start'])-HF},{q(tl['subs'][-1]['end'])-HF})'[v3]",
 "[4:v]fps=30000/1001,format=rgba[sb]",
 "[3:v]fps=30000/1001[sbt]",   # 🆕오더13: 자막 열도 슬라이드처럼 프레임 맞춤(경계 1프레임 남음·빈 바 1프레임 방지)
 "[v3][sb]overlay=eof_action=pass[v4]",
 f"[7:v]setpts=PTS-STARTPTS+{ZB0}/TB[zb]",
 f"[v4][zb]overlay=eof_action=pass:enable='between(t,{ZB0-HF},{ZB1-HF})'[v4b]",
 f"[v4b][5:v]overlay=enable='lt(t,{LOGO_OFF-HF})'[vout]",
]
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "slides_v3b.txt",
       "-f", "lavfi", "-i", "color=black:s=16x16:d=0.1",
       "-i", A["끝인사"]["clip"],
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs_v3b.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix_v3b.wav",
       "-i", "zb.mp4",
       "-i", A["인삿말"]["clip"],
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a",
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "../13강_v3b.mp4"]
a, b = map(float, os.environ["SEG"].split(","))
cmd[-1] = os.environ["OUT"]; cmd[cmd.index("-c:v"):cmd.index("-c:v")] = ["-ss", str(a), "-t", str(b - a)]
print(" ".join(cmd[-3:]))
subprocess.run(cmd, check=True)
print("ok")
