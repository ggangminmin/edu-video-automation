# 11강 v7 렌더(지적 #10~12·#14) = render_v6.py + ① 자막 = 타임라인_v7 subs(줄 나눔, sub_v7/ · subs_v7.txt 새로) ② 끝인사 클립 bye_freeze 에서 trim + tpad clone 정지(12강 render_v4 방식) · 페이드 시각 v6 그대로
# (아래는 v6 머리말)
# 11강 v6 렌더(오더33) = render_v5c.py 영상 부분 그대로 · slides_v5c.txt/subs_v5c.txt/mix_v5c.wav 읽기만(자막·소리·장 경계 v5c 와 같음)
#  바뀐 것 2가지만: ① 아나운서 클립 = B방식(warp_s MODE=flow, ../아나운서B/11_*_flow.mp4) ② 등장 0.5초 알파 페이드인(오프닝·클로징, 본보기 12강 시안가)
#  퇴장(끝인사 fade out 0.5)·위치(447,40 / 952,36)·크기 v5c 그대로. 타입캐스트에 없는 말 = 받아쓰기 대조 결과 없음(③ 할 것 없음)
# 실행(cwd=11강/work): python3 render_v6.py   [SEG=a,b OUT=x.mp4 → 구간만]
import json, os, subprocess
tl = json.load(open("../타임라인_v7.json"))   # v7 = v6 + subs 줄 나눔 + ending.bye_freeze
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
HF = 0.5 / FPS
FADE = float(os.environ.get("FADE", tl["anchors"][0].get("fade_in", 0.5)))
end = tl["ending"]; TOTAL = q(tl["total"])
A = {a["name"]: a for a in tl["anchors"]}
CLIP_G = os.environ.get("CLIP_G", A["인삿말"]["clip"])
CLIP_K = os.environ.get("CLIP_K", A["끝인사"]["clip"])

# ---------- 🆕v7 자막 PNG·concat (render_v5c 와 같은 글꼴·자리 · 줄만 타임라인_v7)
from PIL import Image, ImageDraw, ImageFont
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
TR, BASE = -0.78, 980; OPT = "option framerate 30000/1001\n"
os.makedirs("sub_v7", exist_ok=True)
def sub_png(n, txt):
    p = f"sub_v7/{n:03d}.png"
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = sum(F.getlength(c) for c in txt) + TR * (len(txt) - 1); x = 960 - w / 2
    for c in txt:
        d.text((x, BASE), c, font=F, fill=(33, 46, 58, 255), anchor="ls"); x += F.getlength(c) + TR
    im.save(p); return p
with open("subs_v7.txt", "w") as f:
    t = 0.0
    for x in tl["subs"]:
        st, en = q(x["start"]), q(x["end"])
        if st > t + 1e-6: f.write(f"file 'sub/blank.png'\n{OPT}duration {st - t:.6f}\n")
        f.write(f"file '{sub_png(x['n'], x['text'])}'\n{OPT}duration {en - st:.6f}\n"); t = en
    f.write(f"file 'sub/blank.png'\n{OPT}duration {TOTAL - t:.6f}\nfile 'sub/blank.png'\n{OPT}")
FREEZE = end["bye_freeze"]
s2 = next(s for s in tl["slides"] if s["slide"] == 2); s27 = next(s for s in tl["slides"] if s["slide"] == 27)
gr_out = q(s2["start"])
cl_in, cl_out = q(s27["start"]), A["끝인사"]["out"]
def KEY(t, col="0x00FE05"): return (f"chromakey={col}:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[{t}c][{t}m];"
                    f"[{t}m]alphaextract,erosion,erosion,gblur=sigma=1.2[{t}a];[{t}c][{t}a]alphamerge")
def fin(t0): return f",fade=t=in:st={max(t0 - HF, 0):.4f}:d={FADE}:alpha=1" if FADE > 0 else ""
ZB0, ZB1 = q(end["zoom_blur"][0]), q(end["zoom_blur"][1])
LOGO_OFF = q(end["logo_off"])
vf = [
 "[0:v]fps=30000/1001,format=yuv420p,setsar=1[sl]",
 f"[8:v]fps=30000/1001,{KEY('g','0x01FA04')},scale=788:1402,crop=700:1402:0:0,setpts=PTS-STARTPTS{fin(0.0)}[ag]",
 "[1:v]nullsink",
 f"[2:v]fps=30000/1001,trim=end={FREEZE - A['끝인사']['clip_t0']:.4f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=4,{KEY('k','0x01FA04')},scale=799:1421,crop=700:1421:0:0,setpts=PTS-STARTPTS+{A['끝인사']['clip_t0']}/TB{fin(cl_in)},fade=t=out:st={cl_out-0.5:.3f}:d=0.5:alpha=1[ac]",
 f"[sl][ag]overlay=x=447:y=40:eof_action=pass:enable='lt(t,{gr_out-HF})'[v0]",
 f"[v0][ac]overlay=x=952:y=36:eof_action=pass:enable='between(t,{cl_in-HF},{cl_out-HF})'[v2]",
 f"[v2][3:v]overlay=enable='between(t,{q(tl['subs'][0]['start']) - HF:.4f},{q(tl['subs'][-1]['end']) - HF:.4f})'[v3]",
 "[4:v]fps=30000/1001,format=rgba[sb]",
 "[v3][sb]overlay=eof_action=pass[v4]",
 f"[7:v]setpts=PTS-STARTPTS+{ZB0}/TB[zb]",
 f"[v4][zb]overlay=eof_action=pass:enable='between(t,{ZB0-HF},{ZB1-HF})'[v4b]",
 f"[v4b][5:v]overlay=enable='lt(t,{LOGO_OFF-HF})'[vout]",
]
OUT = os.environ.get("OUT", "../11강_v7.mp4")
seg = ["-ss", os.environ["SEG"].split(",")[0], "-t", str(float(os.environ["SEG"].split(",")[1]) - float(os.environ["SEG"].split(",")[0]))] if os.environ.get("SEG") else ["-t", str(TOTAL)]
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "slides_v5c.txt",
       "-f", "lavfi", "-i", "color=black:s=16x16:d=0.1",
       "-i", CLIP_K,
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs_v7.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix_v5c.wav",
       "-i", "zb.mp4",
       "-i", CLIP_G,
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a", *seg,
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", OUT]
print(OUT, "FADE", FADE, CLIP_G, CLIP_K)
subprocess.run(cmd, check=True)
print("ok")
