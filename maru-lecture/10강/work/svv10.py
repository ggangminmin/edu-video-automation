# 10강: 메모 문장마다 녹음(받아쓰기 cpp·mlx 둘 다, 강 전체)에 있나 + 글자 차이 — 음성에없는문장·녹음_PPT_차이 후보
import json, re, difflib
NOTES = json.load(open("../notes_clean.json"))
def nz(s): return re.sub(r"[^가-힣0-9a-zA-Z]", "", s)
mlx = [(a, w) for a, b, w in json.load(open("mlxwords.json"))]
cpp = [(w["offsets"]["from"] / 1000, w["text"]) for w in json.load(open("wfull.json"))["transcription"]]
def chars(ws):
    c, t = [], []
    for a, w in ws:
        for ch in nz(w): c.append(ch); t.append(a)
    return "".join(c), t
S = []
for si, paras in enumerate(NOTES, 1):
    for x in re.split(r"(?<=[.?!])\s+", " ".join(paras)):
        if nz(x): S.append((si, x))
memo = "".join(nz(x) for _, x in S); own = []
for k, (_, x) in enumerate(S): own += [k] * len(nz(x))
res = []
for name, ws in (("mlx", mlx), ("cpp", cpp)):
    asr, tt = chars(ws)
    sm = difflib.SequenceMatcher(None, memo, asr, autojunk=False)
    hit = [0] * len(memo); tm = [None] * len(memo)
    for a, b, n in sm.get_matching_blocks():
        for i in range(n): hit[a + i] = 1; tm[a + i] = tt[b + i]
    res.append((hit, tm))
out = []
for k, (si, x) in enumerate(S):
    idx = [i for i, o in enumerate(own) if o == k]
    r = [round(sum(h[i] for i in idx) / len(idx), 2) for h, _ in res]
    t0 = next((res[0][1][i] for i in idx if res[0][1][i] is not None), None)
    out.append(dict(slide=si, k=k, mlx=r[0], cpp=r[1], t=t0, sent=x))
json.dump(out, open("svv10.json", "w"), ensure_ascii=False, indent=1)
for o in sorted(out, key=lambda o: max(o["mlx"], o["cpp"]))[:25]: print(o["slide"], o["mlx"], o["cpp"], o["t"], o["sent"])
