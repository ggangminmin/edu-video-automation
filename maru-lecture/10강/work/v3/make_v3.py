# 10강 v3(오더51 토막 자막): 타임라인_v2 → 타임라인_v3초안. 글자·소리 그대로, 나눔 자리만.
#  MERGE = 두 장 → 한 장(첫 장 시작 · 둘째 장 끝) · SPLIT = 새 나눔(둘째 장 시작 = 첫 어절 실소리 −0.09, 실소리 = 깨끗한 음성 5ms RMS −50dB 30ms 상승 · onset10 과 같은 정의)
import json, re, numpy as np, subprocess
tl = json.load(open("../타임라인_v2.json")); S = tl["subs"]
MERGE = [5, 61, 80, 103, 129]
SPLIT = {30: "현장 양생은 여기서 자재가 시공할 공간의 온도와", 52: "설치된 구역은 후속 작업의 오염과 충격을 막도록",
         54: "보양 테이프를 마루 표면에 직접 붙여도 되는지는", 65: "나중에 보수할 때 사용할 수 있는지는 상태와",
         86: "설치 뒤에는 보양 상태와 사용 가능 조건을", 124: "보관 계획에는 장소뿐 아니라 확인 시점과",
         137: "설치된 제품 정보도 함께 남겨", 141: "반입부터 인계까지 제품 라벨과", 174: "양생을 거치면 수축·팽창이 시공 전에",
         224: "11강에서는 패턴 기준선과"}
SR, H = 16000, 80; FR = SR / H
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
ASR = {None: [(a, w) for a, b, w in json.load(open("mlxwords.json"))],
       "work/greet_a9_090.wav": [(a, w) for w, a, b in json.load(open("greet_a9_090_words.json"))["words"]],
       "work/bye_tc_090.wav": [(a, w) for w, a, b in json.load(open("bye_tc_090_words.json"))["words"]]}
def words_out(t0, t1):
    out = []
    for seg in tl["audio"]:
        o0 = seg["out"]; o1 = o0 + seg["src_to"] - seg["src_from"]
        if o1 < t0 or o0 > t1: continue
        for a, w in ASR[seg.get("src")]:
            if seg["src_from"] - 0.05 <= a < seg["src_to"]:
                to = o0 + (max(a, seg["src_from"]) - seg["src_from"])
                if t0 <= to <= t1: out.append((to, w.strip()))
    return sorted(out)
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
def pauses(a, b, TH=-50, GAP=6):
    i0, i1 = int(a * FR), int(b * FR); r = []; j = i0
    while j < i1:
        if db[j] < TH:
            k = j
            while k < i1 and db[k] < TH: k += 1
            if k - j >= GAP:
                m = k
                while m < len(db) - 6 and not all(db[m:m + 6] > TH): m += 1
                r.append((round(j / FR, 3), round(m / FR, 3), k - j))
            j = k
        else: j += 1
    return r
# 실소리 손값(v3/probe.json · probe2 받아쓰기 자르기로 확인: [t-0.9,t] 끝 = 앞 장 끝 어절 · [t,t+1.2] 첫 어절 = 새 장 첫 어절)
ON = {30: 131.79, 52: 222.655, 54: 229.35, 65: 269.14, 86: 355.37, 124: 503.43, 137: 556.495, 141: 571.355, 174: 719.30, 224: 925.105}
new = []; rep = []; i = 0
while i < len(S):
    x = S[i]
    if i in MERGE:
        y = S[i + 1]; m = dict(x); m["text"] = x["text"] + " " + y["text"]; m["end"] = y["end"]; m["v3"] = f"한 장 합침(v2 #{i}+#{i+1})"
        new.append(m); rep.append(("합침", i, x["start"], x["text"] + " / " + y["text"], m["text"], None)); i += 2; continue
    if i in SPLIT:
        y = S[i + 1]; full = x["text"] + " " + y["text"]; a = SPLIT[i]; assert full.startswith(a + " "), i; b = full[len(a) + 1:]
        fw = kn(b.split()[0])[:2]
        ws = words_out(x["start"], y["end"])
        cand = [t for t, w in ws if kn(w).startswith(fw) or kn(w).startswith({"11": "십일"}.get(fw, fw))]
        # 첫 장 글자 비율로 예상 시각 → 가장 가까운 후보
        exp = x["start"] + (y["end"] - x["start"]) * len(a) / len(full)
        ref = min(cand, key=lambda t: abs(t - exp)) if cand else exp
        ps = [p for p in pauses(ref - 0.35, ref + 0.35)]
        on = ON[i]
        rep.append(("나눔", i, x["start"], x["text"] + " / " + y["text"], a + " / " + b, dict(ref=round(ref, 3), exp=round(exp, 3), pauses=ps, onset=on, words=[(round(t, 2), w) for t, w in ws if abs(t - ref) < 1.5])))
        ns = (on - 0.09) if on else None
        x2 = dict(x); x2["text"] = a; y2 = dict(y); y2["text"] = b
        if ns: x2["end"] = ns; y2["start"] = ns; y2["voice_on"] = round(on, 3); y2["how_on"] = "실소리(쉼) −0.09 · v3 토막"
        y2["v3"] = f"다시 나눔(v2 #{i}/#{i+1})"; x2["v3"] = y2["v3"]
        new += [x2, y2]; i += 2; continue
    new.append(x); i += 1
tl["subs"] = new
tl["params"]["v3"] = "오더51 토막 자막: 합침 5 · 다시 나눔 10(둘째 장 시작 = 실소리 −0.09) · 소리·장·아나운서 v2 그대로"
json.dump(tl, open("../타임라인_v3초안.json", "w"), ensure_ascii=False, indent=1)
json.dump(rep, open("v3/rep.json", "w"), ensure_ascii=False, indent=1)
for r in rep: print(r[0], r[1], round(r[2], 2), "|", r[4], "|", r[5] and {k: r[5][k] for k in ("ref", "exp", "onset", "pauses")}, "\n    ", r[5] and r[5]["words"])
