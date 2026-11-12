# 15강 v3 렌더 = render_v2.py 복사 · 바뀐 것 = 타임라인 v3(오더21 규칙7 문장 텀·12강 33번 뺌)·파일 이름만
# 15강 v2 렌더(🆕오더18: 11강 v4 처럼 아나운서 캔버스 오른쪽 잔상 crop 700 · 오더09 · 15강 render_v1.py 복사) — 타임라인_v2: #8 인삿말·끝인사 소리 = 타입캐스트 · 클립 = *_warp.mp4 · 스스로 떠올리기 3초 · BGM 강별 곡(이어 붙임·실측 게인) · 슬라이드 = slides/ 원본(규칙9). 실행은 heavy_run.sh render python3 render_v2.py — 11강 v3 렌더(render.py v2 복사·수정) · v1 렌더 — 타임라인.json 기준. 슬라이드/자막 = concat 이미지열, 아나운서 2개, 자막바·로고 상시, 엔딩
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "../../.."
tl = json.load(open("../타임라인_v3.json"))   # 15강 v2
LAST = tl["slides"][-1]["slide"]
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS                  # 프레임 격자에 맞춤
HF = 0.5 / FPS; CS = float(os.environ.get("CS", "0")) / FPS   # CS = 이어 붙인 슬라이드·자막 열 경계 당김(실측으로 정함) · 🆕오더13 p9 반려: 경계를 프레임 사이(반 칸 앞)에 둬 컷·등장·자막이 같은 프레임으로 반올림되게(14강 끝인사 1프레임 먼저 나옴)

# ---------- 자막 PNG (Freesentation-7Bold 58, #212E3A, 자간 -0.78px, 가운데 x960, 잉크 y935~983)
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
TR, BASE = -0.78, 980
os.makedirs("sub_v3", exist_ok=True)
def sub_png(n, txt):
    p = f"sub_v3/{n:03d}.png"
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = sum(F.getlength(c) for c in txt) + TR * (len(txt) - 1); x = 960 - w / 2
    for c in txt:
        d.text((x, BASE), c, font=F, fill=(33, 46, 58, 255), anchor="ls"); x += F.getlength(c) + TR
    im.save(p); return p
Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)).save("sub_v3/blank.png")

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
if not (os.path.exists("zb.mp4") and os.path.exists("card.png")): subprocess.run(["python3", "ending.py"], check=True)   # 마지막 장 줌블러·카드(있으면 재사용)

# ---------- 슬라이드 concat (표지~27 + 엔딩 카드 + 검정)
Image.new("RGB", (1920, 1080), (0, 0, 0)).save("black.png")
end = tl["ending"]
with open("slides_v3.txt", "w") as f:
    for s in tl["slides"]:
        e = end['zoom_blur'][1] if s['slide'] == LAST else s['end']
        f.write(f"file '../slides/s-{s['slide']:02d}.png'\noption framerate 30000/1001\nduration {q(e) - q(s['start']) - (CS if s is tl['slides'][0] else 0):.6f}\n")
    f.write(f"file 'card.png'\noption framerate 30000/1001\nduration {q(end['black'][0]) - q(end['zoom_blur'][1]):.6f}\n")
    f.write(f"file 'black.png'\noption framerate 30000/1001\nduration {q(end['black'][1]) - q(end['black'][0]):.6f}\nfile 'black.png'\n")
# 자막 concat (슬라이드 사이·표지·엔딩 = 빈칸)
with open("subs_v3.txt", "w") as f:
    t = 0.0
    for x in tl["subs"]:
        st, en = q(x["start"]), q(x["end"])
        if st > t + 1e-6: f.write(f"file 'sub_v3/blank.png'\noption framerate 30000/1001\nduration {st - t - (CS if t == 0.0 else 0):.6f}\n")
        f.write(f"file '{sub_png(x['n'], x['text'])}'\noption framerate 30000/1001\nduration {en - st:.6f}\n"); t = en
    f.write(f"file 'sub_v3/blank.png'\noption framerate 30000/1001\nduration {q(tl['total']) - t:.6f}\nfile 'sub_v3/blank.png'\n")

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
# BGM(규칙10): 강별 곡을 강 길이만큼 이어 붙임(이음매 crossfade 초) · 게인 = 실측(곡 LUFS → 음성 LUFS −20) + VOICE_GAIN(음성과 같이 움직여 −20 유지)
BG = tl["bgm"]; nb = BG["loops"]
chain = "".join(f"[{len(srcs) + j}:a]aformat=sample_rates=48000:channel_layouts=stereo[b{j}];" for j in range(nb))
cur = "b0"
for j in range(1, nb):
    chain += f"[{cur}][b{j}]acrossfade=d={BG['crossfade']}:c1=tri:c2=tri[x{j}];"; cur = f"x{j}"
fc.append(chain + f"[{cur}]adelay=21:all=1,volume={BG['gain_db'] + VOICE_GAIN:.2f}dB,afade=t=out:st={fade_st:.3f}:d={BG['fade_out']},atrim=0:{TOTAL}[bg]")
fc.append("[vo][bg]amix=inputs=2:normalize=0:duration=first,aformat=sample_rates=48000:channel_layouts=stereo[aout]")
ins = sum([["-i", p] for p in srcs], [])
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, *sum([["-i", f"{R}/{tl['bgm']['file']}"] for _ in range(tl["bgm"]["loops"])], []),
                "-filter_complex", ";".join(fc), "-map", "[aout]", "-t", str(TOTAL), "-c:a", "pcm_s16le", "mix_v3.wav"], check=True)

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
       "-f", "concat", "-safe", "0", "-i", "slides_v3.txt",
       "-f", "lavfi", "-i", "color=black:s=16x16:d=0.1",
       "-i", A["끝인사"]["clip"],
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs_v3.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix_v3.wav",
       "-i", "zb.mp4",
       "-i", A["인삿말"]["clip"],
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a", "-t", str(TOTAL),
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "../15강_v3.mp4"]
if os.environ.get("PREVIEW"):
    a, b = os.environ["PREVIEW"].split(","); cmd[cmd.index("-t") + 1] = b
    cmd[-1] = f"preview_{a}.mp4"
print(" ".join(cmd[-3:]))
subprocess.run(cmd, check=True)
print("ok")
