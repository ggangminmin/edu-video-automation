# 11강 v1 렌더 — 타임라인.json 기준. 슬라이드/자막 = concat 이미지열, 아나운서 2개, 자막바·로고 상시, 엔딩
import json, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = "../../.."
tl = json.load(open("../타임라인.json"))
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS                  # 프레임 격자에 맞춤

# ---------- 자막 PNG (Freesentation-7Bold 58, #212E3A, 자간 -0.78px, 가운데 x960, 잉크 y935~983)
F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
TR, BASE = -0.78, 980
os.makedirs("sub", exist_ok=True)
def sub_png(n, txt):
    p = f"sub/{n:03d}.png"
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
subprocess.run(["python3", "ending.py"], check=True)   # v2: card.png + zb.mp4 (00강 엔딩 재현)

# ---------- 슬라이드 concat (표지~27 + 엔딩 카드 + 검정)
Image.new("RGB", (1920, 1080), (0, 0, 0)).save("black.png")
end = tl["ending"]
with open("slides.txt", "w") as f:
    for s in tl["slides"]:
        e = end['zoom_blur'][1] if s['slide'] == 27 else s['end']
        f.write(f"file '../slides/s-{s['slide']:02d}.png'\nduration {q(e) - q(s['start']):.6f}\n")
    f.write(f"file 'card.png'\nduration {q(end['black'][0]) - q(end['zoom_blur'][1]):.6f}\n")
    f.write(f"file 'black.png'\nduration {q(end['black'][1]) - q(end['black'][0]):.6f}\nfile 'black.png'\n")
# 자막 concat (슬라이드 사이·표지·엔딩 = 빈칸)
with open("subs.txt", "w") as f:
    t = 0.0
    for x in tl["subs"]:
        st, en = q(x["start"]), q(x["end"])
        if st > t + 1e-6: f.write(f"file 'sub/blank.png'\nduration {st - t:.6f}\n")
        f.write(f"file '{sub_png(x['n'], x['text'])}'\nduration {en - st:.6f}\n"); t = en
    f.write(f"file 'sub/blank.png'\nduration {q(tl['total']) - t:.6f}\nfile 'sub/blank.png'\n")

# ---------- 오디오: 슬라이드별 원본(0.9배) 조각을 출력 시각에 놓기
TOTAL = q(tl["total"])
parts = []; fc = []
for i, a in enumerate(tl["audio"]):
    fc.append(f"[0:a]atrim={a['src_from']}:{a['src_to']},asetpts=PTS-STARTPTS,adelay={int(round(a['out']*1000))}:all=1[v{i}]")
    parts.append(f"[v{i}]")
VOICE_GAIN = float(os.environ.get("VOICE_GAIN", "-1.2"))
fc.append(f"{''.join(parts)}amix=inputs={len(parts)}:normalize=0:duration=longest,apad,atrim=0:{TOTAL},volume={VOICE_GAIN}dB[vo]")
fade_st = TOTAL - 5.836
fc.append(f"[1:a]adelay=21:all=1,volume=-20dB,afade=t=out:st={fade_st:.3f}:d=5.836,atrim=0:{TOTAL}[bg]")
fc.append("[vo][bg]amix=inputs=2:normalize=0:duration=first,aformat=sample_rates=48000:channel_layouts=stereo[aout]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "v090.wav", "-stream_loop", "-1", "-i", f"{R}/BGM/Approxima.mp3",
                "-filter_complex", ";".join(fc), "-map", "[aout]", "-t", str(TOTAL), "-c:a", "pcm_s16le", "mix.wav"], check=True)

# ---------- 영상
s2 = next(s for s in tl["slides"] if s["slide"] == 2); s27 = next(s for s in tl["slides"] if s["slide"] == 27)
op_in, op_out = q(s2["start"]), q(s2["end"])
op_off = s2["src_offset"]                      # 출력 t = 원본 t + off → 하이젠 오프닝(원본 0초부터)은 off 에 시작
cl_off = s27["src_offset"] + 773.1             # 하이젠 클로징 = 원본 773.1초부터(파형 상관 0.978 실측)
cl_in, cl_out = q(s27["start"]), q(cl_off + 17.24)
# 지적#1(v2 키잉): 디스필 강화 + 알파 2px(원본 기준) 안쪽으로 줄임(erosion×2 ≈ 화면 1.5px) + 가장자리 흐림 σ1.2(≈화면 0.9px)
def KEY(t): return (f"chromakey=0x00FE05:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,split[{t}c][{t}m];"
                    f"[{t}m]alphaextract,erosion,erosion,gblur=sigma=1.2[{t}a];[{t}c][{t}a]alphamerge")
ZB0, ZB1 = q(end["zoom_blur"][0]), q(end["zoom_blur"][1])
LOGO_OFF = q(end["logo_off"])

vf = [
 "[0:v]fps=30000/1001,format=yuv420p,setsar=1[sl]",
 f"[1:v]fps=30000/1001,{KEY('o')},scale=788:1402,setpts=PTS-STARTPTS+{op_off}/TB[ao]",
 f"[2:v]fps=30000/1001,{KEY('k')},scale=799:1421,tpad=start_mode=clone:start_duration=2,setpts=PTS-STARTPTS+{cl_off-2}/TB,fade=t=out:st={cl_out-0.5:.3f}:d=0.5:alpha=1[ac]",
 f"[sl][ao]overlay=x=934:y=40:eof_action=pass:enable='between(t,{op_in},{op_out-0.001})'[v1]",
 f"[v1][ac]overlay=x=952:y=36:eof_action=pass:enable='between(t,{cl_in},{cl_out})'[v2]",
 f"[v2][3:v]overlay=enable='between(t,{q(tl['subs'][0]['start'])},{q(tl['subs'][-1]['end'])})'[v3]",
 "[4:v]fps=30000/1001,format=rgba[sb]",
 "[v3][sb]overlay=eof_action=pass[v4]",
 # 엔딩 줌 블러 근사: 전환 구간에 방사형 확대 + 흐림 (00강 0.67초)
 f"[7:v]setpts=PTS-STARTPTS+{ZB0}/TB[zb]",
 f"[v4][zb]overlay=eof_action=pass:enable='between(t,{ZB0},{ZB1})'[v4b]",
 f"[v4b][5:v]overlay=enable='lt(t,{LOGO_OFF})'[vout]",
]
cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "concat", "-safe", "0", "-i", "slides.txt",
       "-i", f"{R}/_작업/시연/hg_raw.mp4",
       "-i", f"{R}/_작업/아나운서/hg11_close.mp4",
       "-loop", "1", "-i", "bar.png",
       "-f", "concat", "-safe", "0", "-i", "subs.txt",
       "-loop", "1", "-i", "logo_layer.png",
       "-i", "mix.wav",
       "-i", "zb.mp4",
       "-filter_complex", ";".join(vf), "-map", "[vout]", "-map", "6:a", "-t", str(TOTAL),
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001",
       "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", "../11강_v2.mp4"]
if os.environ.get("PREVIEW"):
    a, b = os.environ["PREVIEW"].split(","); cmd[cmd.index("-t") + 1] = b
    cmd[-1] = f"preview_{a}.mp4"
print(" ".join(cmd[-3:]))
subprocess.run(cmd, check=True)
print("ok")
