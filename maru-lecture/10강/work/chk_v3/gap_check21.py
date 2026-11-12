# 10강(오더43) 사본: 20강/work/chk_v4c — 이름 v4c→v1 · gap_check 기준판 = 타임라인_v1_텀전
# (오더34 19·20강 v4c 사본: 파일 이름 v4→v4c 만 바꿈 · 원본 오더25)
# 오더21 규칙7 검사(11강 pR gap_check_v5.py 를 12~15 용으로): 타임라인 audio 표대로 깐 깨끗한 음성에서 실측
#  ① 문장 끝(메모 . ?) 뒤 쉼 ≥1.5  ② 문장 안 쉼 = v2 와 같음(±10ms)  ③ 넘김 말끝→다음 말 1.8(±1프레임) (표지→2 제외 = v2 그대로)
#  ④ BGM: mix_v3.wav − 음성 = BGM 잔차 → LUFS 차이(음성 − BGM) ≈ 20dB (렌더 뒤 mix_v3.wav 있을 때)
# 실행(_작업): python3 오더21/gap_check21.py NN → NN강/검사_v3/문장텀.json
import json, re, subprocess, sys, os, numpy as np
N = sys.argv[1]; D = f"{N}강"; SR = 48000
def voice(tlp):
    tl = json.load(open(tlp)); T = tl["total"]; src = {}
    v = np.zeros(int((T + 1) * SR), np.float32)
    for a in tl["audio"]:
        p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
        if p not in src: src[p] = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
        seg = src[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
        i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
    return tl, v[:int(T * SR)]
def sils(v):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], input=v.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
def gaps(tl, S):
    r = {}; L = tl["slides"][-1]["slide"]
    for s in tl["slides"]:
        if not 2 <= s["slide"] < L: continue
        ls = [x for x in tl["subs"] if x["slide"] == s["slide"]]
        for x in ls[1:]:
            if x["voice_on"] > s["voice_end"]: continue
            c = [(u, w) for u, w in S if x["voice_on"] - 0.35 <= w <= x["voice_on"] + 0.12]
            r[(x["slide"], x["text"])] = round(max(w - u for u, w in c), 3) if c else None
    return r
tl3, v3 = voice(f"{D}/타임라인_v3.json"); tl2, v2 = voice(f"{D}/타임라인_v1_텀전.json")
S3, S2 = sils(v3), sils(v2); g3, g2 = gaps(tl3, S3), gaps(tl2, S2)
st = {(x["slide"], x["text"]): x.get("sent_start") for x in tl3["subs"]}
sent = [g3[k] for k in g3 if st.get(k)]
bad_s = [k for k in g3 if st.get(k) and (g3[k] is None or g3[k] < 1.5)]
# 🆕10강: 문장 안 쉼 = 원음 그대로 → 줄 나눔으로 글자 키가 바뀌어 줄 대조(v2와_다름)는 못 씀 → 장마다 소리 조각이 원음에서 끊김 없이 이어지고(src_to = 다음 src_from)
#        넣은 무음(출력 간격 − 원음 간격)이 전부 문장 끝 쉼 자리(타임라인 pauses = 메모 . ? 뒤 줄)에만 있는지로 잼
inner = []; bad_i = []
PA = {}
for p in tl3.get("pauses", []): PA.setdefault(p["slide"], []).append(p)
for s in tl3["slides"]:
    au = sorted([x for x in tl3["audio"] if x["slide"] == s["slide"] and not x.get("src")], key=lambda x: x["out"])
    for x, y in zip(au, au[1:]):
        cont = abs(x["src_to"] - y["src_from"]) < 1e-4; ins = round((y["out"] - x["out"]) - (y["src_from"] - x["src_from"]), 4)
        inner.append((s["slide"], round(x["src_to"], 3), ins))
        ok_ins = any(abs(ins - (q["after"] - q["before"])) < 0.002 for q in PA.get(s["slide"], []))
        if not cont or not ok_ins: bad_i.append(((s["slide"], round(x["src_to"], 3)), cont, ins))
k_sent = len([x for x in tl3["subs"] if x.get("sent_start")]); n_ins = len(inner)
SL = {s["slide"]: s for s in tl3["slides"]}; L = max(SL); turns = []
for k in range(2, L):
    a, b = SL[k], SL[k + 1]
    if a.get("quiz_wait") or a.get("self_check_wait") or a.get("wait") in ("문제", "스스로"): continue   # 🆕10강: wait 필드도 봄(20강 판은 확인문제 장을 넘김으로 셈 → 넘김 0.21~5.6 걸림)
    end = max(u for u, w in S3 if u < b["start"] and w >= b["start"] - 0.02)
    on = min(w for u, w in S3 if w > b["start"] - 0.02)
    turns.append((k, round(b["start"] - end, 3), round(on - b["start"], 3), round(on - end, 3)))
res = dict(문장끝_쉼=dict(개수=len(sent), 최소=min(sent), 중앙=float(np.median(sent)), 최대=max(sent), 미달=[list(k) for k in bad_s]),
           문장안_쉼=dict(조각이음=len(inner), 걸림=[[list(k), a, b] for k, a, b in bad_i], 방식="원음 연속 + 넣은 무음 = 문장 끝 쉼 자리만"), 넘김=turns,
           넘김_합=dict(최소=min(t[3] for t in turns), 최대=max(t[3] for t in turns)),
           확인문제_스스로=[(s["slide"], s["gap_after_voice"]) for s in tl3["slides"] if s.get("quiz_wait") or s.get("self_check_wait") or s.get("wait") in ("문제", "스스로")],
           뺀줄=tl3.get("dropped", []))
ok = not bad_s and not bad_i and all(1.8 - 0.034 <= t[3] <= 1.8 + 0.034 for t in turns)
mix = f"{D}/work/mix_v3.wav"
if os.path.exists(mix):                                    # BGM = render_v3 과 같은 사슬(이어 붙임·크로스페이드·게인+VOICE_GAIN·페이드)을 따로 뽑아 실측
    BG = tl3["bgm"]; TOT = round(round(tl3["total"] * FPS) / FPS, 6) if False else tl3["total"]; nb = BG["loops"]
    ch = "".join(f"[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo[b{j}];" for j in range(nb)); cur = "b0"
    for j in range(1, nb): ch += f"[{cur}][b{j}]acrossfade=d={BG['crossfade']}:c1=tri:c2=tri[x{j}];"; cur = f"x{j}"
    ch += f"[{cur}]adelay=21:all=1,volume={BG['gain_db'] - 1.2:.2f}dB,afade=t=out:st={TOT - 5.836:.3f}:d={BG['fade_out']},atrim=0:{TOT},ebur128[bg]"
    ins = sum([["-i", "../" + BG["file"]] for _ in range(nb)], [])
    o = subprocess.run(["ffmpeg", "-v", "info", *ins, "-filter_complex", ch, "-map", "[bg]", "-f", "null", "-"], capture_output=True, text=True).stderr
    lb = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", o)[-1])
    vg = v3 * 10 ** (-1.2 / 20)
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "ebur128", "-f", "null", "-"], input=vg.tobytes(), capture_output=True).stderr.decode()
    lv = float(re.findall(r"I:\s+(-?[0-9.]+) LUFS", o)[-1])
    res["BGM"] = dict(음성_LUFS=lv, BGM_LUFS=lb, 차이=round(lv - lb, 2), 기준="20±1", 곡=BG["file"], 이어붙임=nb)
    ok = ok and abs(lv - lb - 20) <= 1.0
res["판정"] = "통과" if ok else "걸림"
os.makedirs(f"{D}/검사_v3", exist_ok=True)
json.dump(res, open(f"{D}/검사_v3/문장텀.json", "w"), ensure_ascii=False, indent=1)
print(N, res["판정"], "문장끝", res["문장끝_쉼"]["개수"], "최소", res["문장끝_쉼"]["최소"], "미달", len(bad_s), "· 문장안", len(inner), "다름", len(bad_i), "· 넘김합", res["넘김_합"], res.get("BGM"))
