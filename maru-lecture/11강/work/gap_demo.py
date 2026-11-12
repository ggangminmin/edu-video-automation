# 오더 17 문장 텀 시안: 11강 3~4번 슬라이드(+5번 첫 1초) 3판 — A 지금 · B 문장 사이 최소 1.3 / 넘김 1.6 · C 1.5 / 1.8
#  문장 끝 쉼(−40dB ≥0.5초)이 목표보다 짧으면 쉼 가운데에 무음을 넣어 목표로(긴 건 그대로) · 쉼표 쉼(<0.5)은 그대로
#  넘김 = 말 끝 → 컷 (목표 − 0.09) · 컷 → 말 0.09 · 자막 = 말 0.09초 앞 · 장면 첫 줄 = 컷 프레임 · 빈 바 0
# 실행: python3 gap_demo.py A|B|C   (mini 타임라인 + 영상 gap_X.mp4)   /  python3 gap_demo.py total  (강 전체 길이 증가 계산)
import json, sys, subprocess, re, os, numpy as np
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
V = {"A": (None, None), "B": (1.3, 1.6), "C": (1.5, 1.8)}
tl = json.load(open("../타임라인_v4.json"))
LEAD = 0.09
def sils(a, b, d=0.5):
    o = subprocess.run(["ffmpeg", "-ss", str(a), "-t", str(b - a), "-i", "v090.wav", "-af", f"silencedetect=n=-40dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    s = [float(x) + a for x in re.findall(r"silence_start: ([0-9.]+)", o)]; e = [float(x) + a for x in re.findall(r"silence_end: ([0-9.]+)", o)]
    return [(x, y) for x, y in zip(s, e) if a + 0.05 < x and y < b - 0.05]       # 슬라이드 조각 안쪽 쉼만(앞뒤 끝 쉼 제외)
S = {s["slide"]: s for s in tl["slides"]}; AU = {a["slide"]: a for a in tl["audio"] if not a.get("src")}

def plan(slides, ver):
    Ts, Tp = V[ver]
    out = dict(slides=[], subs=[], audio=[], pauses=[], turns=[])
    cut = 0.0; pieces = []                                             # (src_from, src_to, out)
    for k, s in enumerate(slides):
        a = AU[s]; off = S[s]["src_offset"]
        lines = [x for x in tl["subs"] if x["slide"] == s]
        v0 = lines[0]["voice_on"] - off                                # 이 장면 첫 말(원본초)
        vend = S[s]["voice_end"] - off
        ins = []                                                       # (원본 위치, 넣을 초)
        for (x, y) in sils(a["src_from"], a["src_to"]):
            if y <= v0 or x >= vend: continue
            g = y - x; add = max(0.0, Ts - g) if Ts else 0.0
            ins.append(((x + y) / 2, add)); out["pauses"].append(round(g + add, 3))
        start = cut; o = start + LEAD - v0                              # 출력 = 원본 + o + (앞에서 넣은 무음)
        def mp(t): return t + o + sum(d for p, d in ins if p <= t)   # 넣은 자리에서 시작하는 조각은 그 무음 뒤에
        prev = max(a["src_from"], v0 - 0.05)
        for p, d in ins + [(a["src_to"], 0.0)]:
            pieces.append((prev, p, mp(prev))); prev = p
        for j, x in enumerate(lines):
            on = mp(x["voice_on"] - off)
            out["subs"].append(dict(slide=s, start=start if j == 0 else q(on - LEAD), voice_on=round(on, 3), text=x["text"], src_n=x.get("src_n")))
        gap = (Tp - LEAD) if Tp else (S[s]["end"] - S[s]["voice_end"])
        end = q(mp(vend) + gap)
        out["turns"].append(round(end - mp(vend) + LEAD, 3))
        out["slides"].append(dict(slide=s, start=start, end=end, voice_end=round(mp(vend), 3)))
        cut = end
    return out, pieces, cut

if sys.argv[1] == "total":                                           # 강 전체(2~26번 본문) 늘어나는 길이
    body = [s for s in sorted(S) if 2 <= s <= 26]
    for ver in "BC":
        Ts, Tp = V[ver]; add_s = add_p = 0.0; n = 0
        for s in body:
            a = AU[s]; off = S[s]["src_offset"]; v0 = [x for x in tl["subs"] if x["slide"] == s][0]["voice_on"] - off; vend = S[s]["voice_end"] - off
            for x, y in sils(a["src_from"], a["src_to"]):
                if v0 < y and x < vend and y - x < Ts: add_s += Ts - (y - x); n += 1
            cur = S[s]["end"] - S[s]["voice_end"] + LEAD
            if not S[s].get("quiz_wait") and not S[s].get("self_check_wait") and s != 26: add_p += max(0, Tp - cur)
        print(ver, f"문장 쉼 {n}곳 +{add_s:.1f}초 · 넘김 +{add_p:.1f}초 · 합 +{add_s + add_p:.1f}초 = +{(add_s + add_p) / 60:.2f}분")
    sys.exit()

ver = sys.argv[1]; SL = [3, 4]
p, pieces, T = plan(SL, ver)
TAIL = 1.2                                                            # 5번 장면 첫 1.2초(넘김 보이게)
s5 = S[5]; a5 = AU[5]; o5 = T + LEAD - ([x for x in tl["subs"] if x["slide"] == 5][0]["voice_on"] - s5["src_offset"])
pieces.append((a5["src_from"], a5["src_from"] + 2.0, a5["src_from"] + o5))
first5 = [x for x in tl["subs"] if x["slide"] == 5][0]
p["subs"].append(dict(slide=5, start=T, voice_on=round(T + LEAD, 3), text=first5["text"]))
p["slides"].append(dict(slide=5, start=T, end=q(T + TAIL)))
TOT = q(T + TAIL)
for i, x in enumerate(p["subs"]):
    x["n"] = i + 1; x["end"] = p["subs"][i + 1]["start"] if i + 1 < len(p["subs"]) else TOT
os.makedirs("gap", exist_ok=True)
# 소리: 조각 이어붙이기 → gap/voice_X.wav (48k 모노)
SR = 48000
src = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", "v090.wav", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout, np.int16)
voice = np.zeros(int((TOT + 1) * SR), np.int32)
for a, b, o in pieces:
    seg = src[int(a * SR):int(b * SR)]; i0 = int(round(o * SR)); i1 = min(len(voice), i0 + len(seg))
    if i0 < 0: seg = seg[-i0:]; i0 = 0
    voice[i0:i1] += seg[:i1 - i0]
voice = np.clip(voice[:int(TOT * SR)], -32768, 32767).astype(np.int16)
vw = f"gap/voice_{ver}.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", vw], input=voice.tobytes(), check=True)
if os.environ.get("VOICE_ONLY"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vw, "-c:a", "aac", "-b:a", "192k", f"../문장텀_{ver}.m4a"], check=True)
    o_ = subprocess.run(["ffmpeg", "-i", vw, "-af", "silencedetect=n=-40dB:d=0.5", "-f", "null", "-"], capture_output=True, text=True).stderr
    ss_ = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o_)]; se_ = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o_)]
    g = [round(e - b, 2) for b, e in zip(ss_, se_) if b > 0.2]
    print(ver, f"{TOT:.1f}초", "쉼(≥0.5초, 실측)", g); sys.exit()
p["audio"] = [dict(slide=0, out=0.0, src_from=0.0, src_to=round(TOT, 3), src=f"work/{vw}")]
p["ending"] = {"zoom_blur": [TOT, TOT]}; p["total"] = TOT; p["anchors"] = [dict(name="없음", **{"in": 0.0})]
json.dump(p, open(f"gap/tl_{ver}.json", "w"), ensure_ascii=False, indent=1)
# 영상: 슬라이드·자막 concat + 자막바 + 로고 + BGM −20dB(본편과 같은 자리에서 시작)
with open(f"gap/sl_{ver}.txt", "w") as f:
    for s in p["slides"]: f.write(f"file '../../slides/s-{s['slide']:02d}.png'\nduration {q(s['end']) - q(s['start']):.6f}\n")
    f.write(f"file '../../slides/s-05.png'\n")
with open(f"gap/sub_{ver}.txt", "w") as f:
    for x in p["subs"]:
        n0 = [y for y in tl["subs"] if y["text"] == x["text"] and y["slide"] == x["slide"]][0]["n"]
        f.write(f"file '../sub_v3/{n0:03d}.png'\nduration {q(x['end']) - q(x['start']):.6f}\n")
    f.write(f"file '../sub_v3/{n0:03d}.png'\n")
bg0 = S[3]["start"]
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"gap/sl_{ver}.txt", "-f", "concat", "-safe", "0", "-i", f"gap/sub_{ver}.txt",
       "-loop", "1", "-i", "bar.png", "-loop", "1", "-i", "logo_layer.png", "-i", vw, "-stream_loop", "-1", "-ss", f"{bg0 - 0.021:.3f}", "-i", "../../../BGM/Approxima.mp3",
       "-filter_complex", "[0:v]fps=30000/1001,format=yuv420p[s];[s][2:v]overlay[a];[a][1:v]overlay[b];[b][3:v]overlay[v];"
       "[4:a]aformat=sample_rates=48000:channel_layouts=mono,volume=-1.2dB[vo];[5:a]volume=-20dB[bg];[vo][bg]amix=inputs=2:normalize=0:duration=first,aformat=channel_layouts=stereo[ao]",
       "-map", "[v]", "-map", "[ao]", "-t", f"{TOT:.3f}", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30000/1001", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart",
       f"../문장텀_{ver}.mp4"]
subprocess.run(cmd, check=True)
o_ = subprocess.run(["ffmpeg", "-i", vw, "-af", "silencedetect=n=-40dB:d=0.5", "-f", "null", "-"], capture_output=True, text=True).stderr   # 실측(만든 소리에서)
ss_ = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o_)]; se_ = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o_)]
cuts_ = [x["start"] for x in p["slides"][1:]]
p["pauses"] = [round(e - b_, 3) for b_, e in zip(ss_, se_) if b_ > 0.2 and e < TOT - 0.3 and not any(b_ - 2 < c < e + 0.2 for c in cuts_)]
ps = np.array(p["pauses"]); print(ver, f"길이 {TOT:.2f}초 · 문장 사이 쉼 {len(ps)}곳 최소 {ps.min():.2f} 중앙 {np.median(ps):.2f} · 넘김(말끝→다음 말) {p['turns']}")
json.dump(dict(dur=round(TOT, 2), n=len(ps), min=round(float(ps.min()), 2), median=round(float(np.median(ps)), 2), turns=p["turns"]), open(f"gap/stat_{ver}.json", "w"))
