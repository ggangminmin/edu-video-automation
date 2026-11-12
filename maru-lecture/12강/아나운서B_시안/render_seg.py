# 오더32 12강 아나운서 B방식 + 등장 시안 구간 렌더 = render_v4.py 영상 부분 그대로(슬라이드/자막 concat·mix_v4.wav 는 v4 것 읽기만) · 아나운서 클립 = B(flow) · 등장 페이드만 바꿈
# 실행(cwd=12강/work): FADE=<초|0> GROW=<0|1> SEG=a,b OUT=<mp4> python3 ../아나운서B_시안/render_seg.py
#  FADE = 등장 알파 페이드인 길이(0 = v4 처럼 툭) · GROW=1 → 등장 동안 크기 98→100%(아래 가운데 기준, 위치·최종 크기 v4 그대로)
import json, os, subprocess
B = "../아나운서B_시안"
tl = json.load(open("../타임라인_v4.json")); LAST = tl["slides"][-1]["slide"]
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
HF = 0.5 / FPS
end = tl["ending"]
A = {a["name"]: a for a in tl["anchors"]}
A["인삿말"]["clip"] = os.environ.get("CLIP_G", f"{B}/12_인삿말_flow.mp4")
A["끝인사"]["clip"] = os.environ.get("CLIP_K", f"{B}/12_끝인사_flow.mp4")
FADE = float(os.environ.get("FADE", "0")); GROW = os.environ.get("GROW", "0") == "1"
s2 = next(s for s in tl["slides"] if s["slide"] == 2); sL = next(s for s in tl["slides"] if s["slide"] == LAST)
gr_out = q(s2["start"])
cl_in, cl_out = q(sL["start"]), A["끝인사"]["out"]
def KEY(t, col="0x00FE05"): return (f"chromakey={col}:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[{t}c][{t}m];"
                    f"[{t}m]alphaextract,erosion,erosion,gblur=sigma=1.2[{t}a];[{t}c][{t}a]alphamerge")
FREEZE = end.get("bye_freeze", 879.40)
ZB0, ZB1 = q(end["zoom_blur"][0]), q(end["zoom_blur"][1])
LOGO_OFF = q(end["logo_off"])
def fin(t0): return f",fade=t=in:st={max(t0 - HF, 0):.4f}:d={FADE}:alpha=1" if FADE > 0 else ""
GD = FADE if FADE > 0 else 0.5
def grow(t0): return (f",scale=w='trunc(iw*(0.98+0.02*min(max((t-{max(t0 - HF, 0):.4f})/{GD},0),1))/2)*2':h=-2:eval=frame" if GROW else "")
gx, gy = A['인삿말'].get('x', 934), A['인삿말'].get('y', 40)
kx, ky = A['끝인사'].get('x', 952), A['끝인사'].get('y', 36)
GH, KH = 1402, 1421   # 아나운서 레이어 높이(crop 뒤) — 아래 가운데 기준: y = y0 + (H0 - h)
def pos(x, y, H0):
    return f"x={x}:y={y}" if not GROW else f"x='{x}+(700-w)/2':y='{y}+({H0}-h)':eval=frame"

vf = [
 "[0:v]fps=30000/1001,format=yuv420p,setsar=1[sl]",
 f"[8:v]fps=30000/1001,{KEY('g','0x01FA04')},scale=788:1402,crop=700:1402:0:0,setpts=PTS-STARTPTS{fin(0.0)}{grow(0.0)}[ag]",
 "[1:v]nullsink",
 f"[2:v]fps=30000/1001,trim=end={FREEZE - A['끝인사']['clip_t0']:.4f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=4,{KEY('k','0x01FA04')},scale=799:1421,crop=700:1421:0:0,setpts=PTS-STARTPTS+{A['끝인사']['clip_t0']}/TB{fin(cl_in)}{grow(cl_in)},fade=t=out:st={cl_out-0.5:.3f}:d=0.5:alpha=1[ac]",
 f"[sl][ag]overlay={pos(gx, gy, GH)}:eof_action=pass:enable='lt(t,{gr_out-HF})'[v0]",
 f"[v0][ac]overlay={pos(kx, ky, KH)}:eof_action=pass:enable='between(t,{cl_in-HF},{cl_out-HF})'[v2]",
 f"[v2][sbt]overlay=enable='between(t,{q(tl['subs'][0]['start'])-HF},{q(tl['subs'][-1]['end'])-HF})'[v3]",
 "[4:v]fps=30000/1001,format=rgba[sb]",
 "[3:v]fps=30000/1001[sbt]",
 "[v3][sb]overlay=eof_action=pass[v4]",
 f"[7:v]setpts=PTS-STARTPTS+{ZB0}/TB[zb]",
 f"[v4][zb]overlay=eof_action=pass:enable='between(t,{ZB0-HF},{ZB1-HF})'[v4b]",
 f"[v4b][5:v]overlay=enable='lt(t,{LOGO_OFF-HF})'[vout]",
]
a, b = map(float, os.environ["SEG"].split(","))
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "slides_v4.txt",
       "-f", "lavfi", "-i", "color=black:s=16x16:d=0.1",
       "-i", A["끝인사"]["clip"],
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs_v4.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix_v4.wav",
       "-i", "zb.mp4",
       "-i", A["인삿말"]["clip"],
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a", "-ss", str(a), "-t", str(b - a),
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", os.environ["OUT"]]
print(os.environ["OUT"], "FADE", FADE, "GROW", GROW)
subprocess.run(cmd, check=True)
print("ok")
