# 14강 v1 렌더 (11강 render_v3.py 복사·수정)(render.py v2 복사·수정) · v1 렌더 — 타임라인.json 기준. 슬라이드/자막 = concat 이미지열, 아나운서 2개, 자막바·로고 상시, 엔딩
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "../../.."
tl = json.load(open("../타임라인_v1.json"))   # v3
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS                  # 프레임 격자에 맞춤

# ---------- 자막 PNG (Freesentation-7Bold 58, #212E3A, 자간 -0.78px, 가운데 x960, 잉크 y935~983)
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
TR, BASE = -0.78, 980
os.makedirs("sub_v1", exist_ok=True)
def sub_png(n, txt):
    p = f"sub_v1/{n:03d}.png"
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = sum(F.getlength(c) for c in txt) + TR * (len(txt) - 1); x = 960 - w / 2
    for c in txt:
        d.text((x, BASE), c, font=F, fill=(33, 46, 58, 255), anchor="ls"); x += F.getlength(c) + TR
    im.save(p); return p
Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)).save("sub/blank.png")

# ---------- 로고(00강 x1553~1826 · y71~128: 마크 왼쪽 x1554, 글자 오른끝 x1823 에 맞춤)
L = Image.open(f"{R}/교재/대한마루협회 로고.png").convert("RGBA")
S = (1823 - 1554) / (2027 - 127)
Ls = L.resize((round(L.width * S), round(L.height * S)), Image.LANCZOS)
logo = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
sh = Image.new("RGBA", Ls.size, (0, 0, 0, 0)); sh.putalpha(Ls.getchannel("A").point(lambda v: v * 0.35))
pos = (round(1554 - 127 * S), round(72 - 185 * S))
logo.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.5)), (pos[0] + 1, pos[1] + 1)); logo.alpha_composite(Ls, pos)
logo.save("logo_layer.png")
# 엔딩 카드: #DFB690 + 가운데 로고 440x104 (x738~1178, y487~591)
subprocess.run(["python3", "ending.py"], check=True)   # 14강: 25번 슬라이드로 card.png · zb.mp4

# ---------- 슬라이드 concat (표지~27 + 엔딩 카드 + 검정)
Image.new("RGB", (1920, 1080), (0, 0, 0)).save("black.png")
end = tl["ending"]
with open("slides_v1.txt", "w") as f:
    for s in tl["slides"]:
        e = end['zoom_blur'][1] if s['slide'] == 25 else s['end']
        f.write(f"file '../slides/s-{s['slide']:02d}.png'\nduration {q(e) - q(s['start']):.6f}\n")
    f.write(f"file 'card.png'\nduration {q(end['black'][0]) - q(end['zoom_blur'][1]):.6f}\n")
    f.write(f"file 'black.png'\nduration {q(end['black'][1]) - q(end['black'][0]):.6f}\nfile 'black.png'\n")
# 자막 concat (슬라이드 사이·표지·엔딩 = 빈칸)
with open("subs_v1.txt", "w") as f:
    t = 0.0
    for x in tl["subs"]:
        st, en = q(x["start"]), q(x["end"])
        if st > t + 1e-6: f.write(f"file 'sub/blank.png'\nduration {st - t:.6f}\n")
        f.write(f"file '{sub_png(x['n'], x['text'])}'\nduration {en - st:.6f}\n"); t = en
    f.write(f"file 'sub/blank.png'\nduration {q(tl['total']) - t:.6f}\nfile 'sub/blank.png'\n")

# ---------- 오디오: 슬라이드별 원본(0.9배) 조각을 출력 시각에 놓기
TOTAL = q(tl["total"])
parts = []; fc = []; srcs = []
for a in tl["audio"]:
    p = os.path.join("..", a["src"]) if a.get("src") else "v090.wav"
    if p not in srcs: srcs.append(p)
for i, a in enumerate(tl["audio"]):
    k = srcs.index(os.path.join("..", a["src"]) if a.get("src") else "v090.wav")
    fc.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=mono,atrim={a['src_from']}:{a['src_to']},asetpts=PTS-STARTPTS,volume={a.get('gain',1.0)},adelay={int(round(a['out']*1000))}:all=1[v{i}]")
    parts.append(f"[v{i}]")
VOICE_GAIN = float(os.environ.get("VOICE_GAIN", "-1.2"))
fc.append(f"{''.join(parts)}amix=inputs={len(parts)}:normalize=0:duration=longest,apad,atrim=0:{TOTAL},volume={VOICE_GAIN}dB[vo]")
fade_st = TOTAL - 5.836
fc.append(f"[{len(srcs)}:a]adelay=21:all=1,volume=-20dB,afade=t=out:st={fade_st:.3f}:d=5.836,atrim=0:{TOTAL}[bg]")
fc.append("[vo][bg]amix=inputs=2:normalize=0:duration=first,aformat=sample_rates=48000:channel_layouts=stereo[aout]")
ins = sum([["-i", p] for p in srcs], [])
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-stream_loop", "-1", "-i", f"{R}/BGM/Approxima.mp3",
                "-filter_complex", ";".join(fc), "-map", "[aout]", "-t", str(TOTAL), "-c:a", "pcm_s16le", "mix_v1.wav"], check=True)

# ---------- 영상 (v3: 인삿말 · 오프닝 idle · 클로징 idle — 등장 순간부터 움직임)
A = {a["name"]: a for a in tl["anchors"]}
s2 = next(s for s in tl["slides"] if s["slide"] == 2); s25 = next(s for s in tl["slides"] if s["slide"] == 25)
gr_out = q(s2["start"])
cl_in, cl_out = q(s25["start"]), A["끝인사"]["out"]
def KEY(t, col="0x00FE05"): return (f"chromakey={col}:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[{t}c][{t}m];"
                    f"[{t}m]alphaextract,erosion,erosion,gblur=sigma=1.2[{t}a];[{t}c][{t}a]alphamerge")
ZB0, ZB1 = q(end["zoom_blur"][0]), q(end["zoom_blur"][1])
LOGO_OFF = q(end["logo_off"])

vf = [
 "[0:v]fps=30000/1001,format=yuv420p,setsar=1[sl]",
 f"[8:v]fps=30000/1001,{KEY('g','0x01FA04')},scale=788:1402,setpts=PTS-STARTPTS[ag]",
 "[1:v]nullsink",
 f"[2:v]fps=30000/1001,{KEY('k','0x01FA04')},scale=799:1421,setpts=PTS-STARTPTS+{A['끝인사']['clip_t0']}/TB,fade=t=out:st={cl_out-0.5:.3f}:d=0.5:alpha=1[ac]",
 f"[sl][ag]overlay=x=934:y=40:eof_action=pass:enable='lt(t,{gr_out-0.001})'[v0]",
 f"[v0][ac]overlay=x=952:y=36:eof_action=pass:enable='between(t,{cl_in},{cl_out})'[v2]",
 f"[v2][3:v]overlay=enable='between(t,{q(tl['subs'][0]['start'])},{q(tl['subs'][-1]['end'])})'[v3]",
 "[4:v]fps=30000/1001,format=rgba[sb]",
 "[v3][sb]overlay=eof_action=pass[v4]",
 f"[7:v]setpts=PTS-STARTPTS+{ZB0}/TB[zb]",
 f"[v4][zb]overlay=eof_action=pass:enable='between(t,{ZB0},{ZB1})'[v4b]",
 f"[v4b][5:v]overlay=enable='lt(t,{LOGO_OFF})'[vout]",
]
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "slides_v1.txt",
       "-f", "lavfi", "-i", "color=black:s=16x16:d=0.1",
       "-i", A["끝인사"]["clip"],
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs_v1.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix_v1.wav",
       "-i", "zb.mp4",
       "-i", A["인삿말"]["clip"],
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a", "-t", str(TOTAL),
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "../14강_v1.mp4"]
if os.environ.get("PREVIEW"):
    a, b = os.environ["PREVIEW"].split(","); cmd[cmd.index("-t") + 1] = b
    cmd[-1] = f"preview_{a}.mp4"
print(" ".join(cmd[-3:]))
subprocess.run(cmd, check=True)
print("ok")
