# 14강 v6 타임라인 = 타임라인_v5b + 오더36: 16·18·22장 중간점 문장 소리를 새 소리(_작업/중간점_새음성/14_NN장.wav, p1T)로 갈아끼움
#  - 옛 문장 말 구간(v090 5ms RMS > -45dB, 30ms 이상) 을 잘라 내고 그 자리에 새 wav 를 놓음: 새 말 시작 = 옛 말 시작(앞 쉼 그대로)
#  - 새 말 끝 → 다음 말 = 옛 쉼 그대로(뒤 전부 delta = 새 말 길이 − 옛 말 길이 만큼 밀고 당김)
#  - 이음매 = 쉼 안 · 새 wav 앞 5ms / 끝 10ms 페이드(p1T) + 잘린 v090 조각 끝·앞 10ms 페이드(afade 키)
#  - 자막: 그 문장 두 줄 글자·나눔 그대로 · 1줄 시작 = 새 말 시작 −0.09 · 2줄 시작 = SPLIT2(새 wav 안 2줄 첫 어절 시작, 받아쓰기+newline_onset 로 확인) −0.09
import json, sys, numpy as np, soundfile as sf
NEW = "../중간점_새음성"            # 14강 폴더 기준(render 는 "../"+src)
tl = json.load(open("../타임라인_v5b.json"))
y, sr = sf.read("v090.wav"); y = y.mean(1) if y.ndim > 1 else y
H = int(0.005 * sr)
def env(sig, a, b):
    s = sig[int(a * sr):int(b * sr)]; n = len(s) // H
    return 20 * np.log10(np.sqrt((s[:n * H].reshape(n, H) ** 2).mean(1)) + 1e-9)
def bounds(e, t0=0.0, th=-45, run=6):   # 30ms 이상 이어진 소리의 처음·끝
    on = e > th; idx = [i for i in range(len(e) - run) if on[i:i + run].all()]
    first = idx[0]; last = idx[-1] + run
    return t0 + first * 0.005, t0 + last * 0.005
# 장: (그 문장 1줄 자막 n, 새 wav, 2줄 첫 어절 새 wav 안 시각)
SPLIT2 = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"16": 2.86, "18": 2.99, "22": 3.635}
JOBS = [("16", 168, "14_16장.wav"), ("18", 180, "14_18장.wav"), ("22", 203, "14_22장.wav")]
au = tl["audio"]; subs = tl["subs"]
plan = []
for sl, n1, wav in JOBS:
    s1 = next(s for s in subs if s["n"] == n1); s2 = next(s for s in subs if s["n"] == n1 + 1)
    i = max(k for k, a in enumerate(au) if a["out"] <= s1["voice_on"] and not a.get("src")); a = au[i]
    off = a["out"] - a["src_from"]
    on, end = bounds(env(y, a["src_from"], a["src_to"]), a["src_from"])
    z, zsr = sf.read(f"../{NEW}/{wav}"); assert zsr == sr
    zon, zend = bounds(env(z, 0, len(z) / sr))
    old_len, new_len = end - on, zend - zon; raw = new_len - old_len
    FPS = 30000 / 1001; import math; delta = math.ceil(raw * FPS - 1e-9) / FPS   # p1T: Δ 프레임 격자 · 남는 것 = 뒤 쉼 늘림
    plan.append(dict(slide=sl, i=i, n1=n1, off=off, src_on=on, src_end=end, out_on=on + off, out_end=end + off,
                     wav=wav, zlen=len(z) / sr, zon=zon, zend=zend, old_len=old_len, new_len=new_len, raw=raw, pad=delta - raw, delta=delta, split2=SPLIT2[sl]))
# 뒤에서부터 끼워야 앞 시각이 안 흔들림 → 앞에서부터 하되 누적 shift 로 계산
shift_pts = [(p["out_end"], p["delta"]) for p in plan]
def sh(t):  # 원래(v5b) 출력 시각 t → v6 시각
    return t + sum(d for te, d in shift_pts if t >= te - 1e-6)
new_audio = []
for k, a in enumerate(au):
    p = next((p for p in plan if p["i"] == k), None)
    if not p:
        b = dict(a); b["out"] = sh(a["out"]); new_audio.append(b); continue
    # ① 앞 쉼(옛 조각 처음 ~ 새 wav 시작 자리)
    cut0 = p["src_on"] - p["zon"]                # 새 wav 를 놓는 v090 자리(새 말 시작 = 옛 말 시작)
    new_audio.append(dict(slide=a["slide"], out=sh(a["out"]), src_from=a["src_from"], src_to=round(cut0, 4), afade_out=0.01, note="v6 앞 쉼"))
    # ② 새 소리
    new_audio.append(dict(slide=a["slide"], out=round(sh(a["out"]) + (cut0 - a["src_from"]), 4), src_from=0.0, src_to=round(p["zlen"], 4),
                          src=f"{NEW}/{p['wav']}", gain=1.0, note="v6 오더36 새 중간점 소리"))
    # ③ 뒤 쉼(옛 말 끝 ~ 조각 끝) — 새 말 끝 바로 뒤에 이어 붙임(옛 말끝→다음 말 쉼 유지)
    t_new_end = sh(a["out"]) + (cut0 - a["src_from"]) + p["zend"]   # 새 말 끝 출력 시각 (= out_end + delta, 앞 장 shift 포함)
    rest0 = p["src_end"]
    new_audio.append(dict(slide=a["slide"], out=round(t_new_end + (p["zlen"] - p["zend"]) + p["pad"], 4), src_from=round(rest0 + (p["zlen"] - p["zend"]), 4),
                          src_to=a["src_to"], afade_in=0.01, note="v6 뒤 쉼"))
    p["new_out_on"] = sh(a["out"]) + (cut0 - a["src_from"]) + p["zon"]; p["new_out_end"] = t_new_end
    p["wav_out"] = sh(a["out"]) + (cut0 - a["src_from"])
tl["audio"] = new_audio
for s in tl["slides"]:
    for key in ("start", "end", "voice_start", "voice_end"):
        if key in s: s[key] = sh(s[key])
for s in subs:
    p = next((p for p in plan if s["n"] in (p["n1"], p["n1"] + 1)), None)
    if p and s["n"] == p["n1"]:
        s["voice_on"] = round(p["new_out_on"], 4); s["start"] = round(p["new_out_on"] - 0.09, 4)
        s["end"] = round(p["wav_out"] + p["split2"] - 0.09, 4); s["v6"] = "오더36 새 소리"
    elif p:
        s["voice_on"] = round(p["wav_out"] + p["split2"], 4); s["start"] = round(p["wav_out"] + p["split2"] - 0.09, 4)
        s["end"] = sh(s["end"]); s["v6"] = "오더36 새 소리"
    else:
        for key in ("start", "voice_on", "end"): s[key] = sh(s[key])
for a in tl["anchors"]:
    for key in ("in", "clip_t0", "out"):
        if key in a and a["in"] > 1: a[key] = sh(a[key])
E = tl["ending"]
for key in ("zoom_blur", "card", "black"): E[key] = [sh(v) for v in E[key]]
E["logo_off"] = sh(E["logo_off"]); E["bye_freeze"] = sh(E["bye_freeze"])
tl["total"] = sh(tl["total"])
tl["params"]["v6"] = "오더36: 16·18·22장 중간점 문장 = 새 타입캐스트(중간점 나레이션.wav 0.9배, p1T 자름) · 앞 쉼·뒤 쉼 그대로 · 뒤 밀기 = 문장 길이 차"
tl["v6_plan"] = [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items()} for p in plan]
json.dump(tl, open("../타임라인_v6.json", "w"), ensure_ascii=False, indent=1)
for p in tl["v6_plan"]: print(p)
print("total", tl["total"], "누적 delta", sum(p["delta"] for p in plan))
