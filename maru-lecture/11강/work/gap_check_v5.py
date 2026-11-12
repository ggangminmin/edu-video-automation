# 규칙 7 검사(오더 19-7): 타임라인 audio 표대로 깐 깨끗한 음성에서 실측
#  ① 문장 끝(메모 . ?) 뒤 쉼 ≥1.5  ② 문장 안 쉼 = v4 와 같음(±10ms)  ③ 페이지 넘김 말끝→다음 말 1.8(±1프레임) · 말끝→컷 1.71 · 컷→말 0.09
#  쉼 = 그 줄 말 시작 직전 −40dB 무음(≥0.04초) 중 가장 긴 것(줄 말 시작 −0.35~+0.12 안에서 끝나는 것)
import json, re, subprocess, sys, numpy as np
SR = 48000
def voice(tlp):
    tl = json.load(open(tlp)); T = tl["total"]
    src = {}
    v = np.zeros(int((T + 1) * SR), np.float32)
    for a in tl["audio"]:
        p = "../" + a["src"] if a.get("src") else "v090.wav"
        if p not in src: src[p] = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
        seg = src[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
        i0 = int(round(a["out"] * SR)); v[i0:i0 + len(seg)] += seg[:len(v) - i0]
    return tl, v
def sils(v):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], input=v.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
def gaps(tl, S):
    r = {}
    for s in tl["slides"]:
        if not 2 <= s["slide"] <= 26: continue
        ls = [x for x in tl["subs"] if x["slide"] == s["slide"]]
        for x in ls[1:]:
            c = [(u, w) for u, w in S if x["voice_on"] - 0.35 <= w <= x["voice_on"] + 0.12]
            r[x["src_n"]] = round(max(w - u for u, w in c), 3) if c else None
    return r
tl5, v5 = voice("../타임라인_v5.json"); tl4, v4 = voice("../타임라인_v4.json")
S5, S4 = sils(v5), sils(v4); g5, g4 = gaps(tl5, S5), gaps(tl4, S4)
st = {x["src_n"]: x.get("sent_start") for x in tl5["subs"] if x.get("src_n")}
sent = [g5[n] for n in g5 if st.get(n)]; inner = [(n, g4[n], g5[n]) for n in g5 if not st.get(n)]
bad_s = [n for n in g5 if st.get(n) and (g5[n] is None or g5[n] < 1.5)]
bad_i = [(n, a, b) for n, a, b in inner if (a is None) != (b is None) or (a is not None and abs(a - b) > 0.01)]   # 둘 다 None = 쉼 없이 이어짐(같음)
turns = []
SL = {s["slide"]: s for s in tl5["slides"]}
for k in range(2, 27):
    a, b = SL[k], SL[k + 1]
    if a["quiz_wait"] or a["self_check_wait"]: continue
    # 실측 말 끝 = 컷 앞 마지막 무음 시작 · 실측 말 시작 = 컷 뒤 첫 무음 끝
    end = max(u for u, w in S5 if u < b["start"] and w >= b["start"] - 0.02)
    on = min(w for u, w in S5 if w > b["start"] - 0.02)
    turns.append((k, round(b["start"] - end, 3), round(on - b["start"], 3), round(on - end, 3)))
res = dict(문장끝_쉼=dict(개수=len(sent), 최소=min(sent), 중앙=float(np.median(sent)), 최대=max(sent), 미달=bad_s),
           문장안_쉼=dict(개수=len(inner), v4와_다름=bad_i), 넘김=turns,
           넘김_합=dict(최소=min(t[3] for t in turns), 최대=max(t[3] for t in turns)),
           확인문제_스스로=[(s["slide"], s["gap_after_voice"]) for s in tl5["slides"] if s.get("quiz_wait") or s.get("self_check_wait")])
ok = not bad_s and not bad_i and all(1.8 - 0.034 <= t[3] <= 1.8 + 0.034 for t in turns)
res["판정"] = "통과" if ok else "걸림"
json.dump(res, open("../../검수/검사기/v5_문장텀.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False)[:1500])
