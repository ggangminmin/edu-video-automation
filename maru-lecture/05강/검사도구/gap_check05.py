# 05강 사본(오더44 · 20강 chk_v4c/gap_check21.py): 깨끗한 음성(타임라인 audio 대로)에서 ① 문장 끝 쉼 ≥1.5 ② 문장 안 쉼 = v090 원음과 같음(±10ms — 앞판 v2 대신 원음 직접)
#  ③ 넘김 말끝→다음 말 1.8(±1프레임, 표지→2·문제·스스로 제외) ④ BGM −20dB(render 와 같은 사슬 ebur128)
import json, re, subprocess, sys, os, numpy as np
VER = sys.argv[1]; D = "05강"; SR = 48000; FPS = 30000 / 1001
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
tl = json.load(open(f"{D}/타임라인_{VER}.json")); T = tl["total"]; src = {}; v = np.zeros(int((T + 1) * SR), np.float32)
for a in tl["audio"]:
    p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
    if p not in src: src[p] = load(p)
    seg = src[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
    i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
v = v[:int(T * SR)]
def sils(x):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], input=x.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
S3 = sils(v); S0 = sils(load(f"{D}/work/v090.wav")); L = tl["slides"][-1]["slide"]; SL = {s["slide"]: s for s in tl["slides"]}
def gap(S, on):
    c = [(u, w) for u, w in S if on - 0.35 <= w <= on + 0.12]; return round(max(w - u for u, w in c), 3) if c else None
sent, inner = [], []
for s in tl["slides"]:
    if not 2 <= s["slide"] < L: continue
    for x in [x for x in tl["subs"] if x["slide"] == s["slide"]][1:]:
        g3 = gap(S3, x["voice_on"])
        if x.get("sent_start"): sent.append((x["n"], x["text"][:16], g3))
        else: inner.append((x["n"], x["text"][:16], gap(S0, x["v090_on"]), g3))
bad_s = [r for r in sent if r[2] is None or r[2] < 1.5]
bad_i = [r for r in inner if (r[2] is None) != (r[3] is None) or (r[2] is not None and abs(r[2] - r[3]) > 0.01)]
turns = []
for k in range(2, L):
    a, b = SL[k], SL[k + 1]
    if a.get("quiz_wait") or a.get("self_check_wait"): continue
    end = max(u for u, w in S3 if u < b["start"] and w >= b["start"] - 0.02); on = min(w for u, w in S3 if w > b["start"] - 0.02)
    turns.append((k, round(b["start"] - end, 3), round(on - b["start"], 3), round(on - end, 3)))
waits = [(s["slide"], s["wait"], s["gap_after_voice"]) for s in tl["slides"] if s.get("quiz_wait") or s.get("self_check_wait")]
ok = not bad_s and not bad_i and all(1.8 - 0.034 <= t[3] <= 1.8 + 0.034 for t in turns) and all(abs(g - (5.5 if w == "문제" else 3.0)) < 0.034 for _, w, g in waits)
res = dict(문장끝_쉼=dict(개수=len(sent), 최소=min(r[2] for r in sent), 미달=bad_s), 문장안_쉼=dict(개수=len(inner), 원음과_다름=bad_i), 넘김=turns,
           넘김_합=dict(최소=min(t[3] for t in turns), 최대=max(t[3] for t in turns)), 확인문제_스스로=waits)
mix = f"{D}/work/mix_{VER}.wav"
if os.path.exists(mix):
    BG = tl["bgm"]; nb = BG["loops"]; ch = "".join(f"[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo[b{j}];" for j in range(nb)); cur = "b0"
    for j in range(1, nb): ch += f"[{cur}][b{j}]acrossfade=d={BG['crossfade']}:c1=tri:c2=tri[x{j}];"; cur = f"x{j}"
    ch += f"[{cur}]adelay=21:all=1,volume={BG['gain_db'] - 1.2:.2f}dB,afade=t=out:st={T - 5.836:.3f}:d={BG['fade_out']},atrim=0:{T},ebur128[bg]"
    o = subprocess.run(["ffmpeg", "-v", "info", *sum([["-i", "../" + BG["file"]] for _ in range(nb)], []), "-filter_complex", ch, "-map", "[bg]", "-f", "null", "-"], capture_output=True, text=True).stderr
    lb = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", o)[-1])
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "ebur128", "-f", "null", "-"], input=(v * 10 ** (-1.2 / 20)).tobytes(), capture_output=True).stderr.decode()
    lv = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", o)[-1]); res["BGM"] = dict(음성_LUFS=lv, BGM_LUFS=lb, 차이=round(lv - lb, 2), 기준="20±1", 곡=BG["file"]); ok = ok and abs(lv - lb - 20) <= 1.0
res["판정"] = "통과" if ok else "걸림"
json.dump(res, open(f"{D}/검사_{VER}/문장텀.json", "w"), ensure_ascii=False, indent=1)
print(res["판정"], "문장끝", len(sent), "최소", res["문장끝_쉼"]["최소"], "미달", len(bad_s), "· 문장안", len(inner), "다름", len(bad_i), "· 넘김합", res["넘김_합"], "· 대기", waits, res.get("BGM"))
sys.exit(0 if ok else 1)
