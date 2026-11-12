# 줄별 첫 글자 시각(mlx-whisper 단어 / whisper.cpp 단어) — 11강 linetimes_make.py 에서 정답표(GT) 비교만 뺀 판
import json, re, difflib, bisect
def norm(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]
lines = json.load(open("lines.json"))
sch, sl = [], []
for i, t in enumerate(lines):
    for c in norm(t): sch.append(c); sl.append(i)
def char_times(words):
    tch, tt = [], []
    for a, b, w in words:
        cs = norm(w)
        for k, c in enumerate(cs): tch.append(c); tt.append(a + (b - a) * k / max(1, len(cs)))
    sm = difflib.SequenceMatcher(None, sch, tch, autojunk=False); st = [None] * len(sch)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): st[a + k] = tt[b + k]
    print("일치", sum(n for _, _, n in sm.get_matching_blocks()), "/", len(sch))
    idx = [i for i, v in enumerate(st) if v is not None]
    for i in range(len(st)):
        if st[i] is None:
            j = bisect.bisect(idx, i); lo = idx[j-1] if j > 0 else idx[0]; hi = idx[j] if j < len(idx) else idx[-1]
            st[i] = st[lo] if hi == lo else st[lo] + (st[hi] - st[lo]) * (i - lo) / (hi - lo)
    first = {}
    for i, l in enumerate(sl): first.setdefault(l, st[i])
    return [first[i] for i in range(len(lines))]
mlx = [(a, b, w) for a, b, w in json.load(open("mlxwords.json"))]
cpp = [(w["offsets"]["from"]/1000, w["offsets"]["to"]/1000, w["text"]) for w in json.load(open("wfull.json"))["transcription"]]
Tm = char_times(mlx); Tc = char_times(cpp)
json.dump({"mlx": Tm, "cpp": Tc}, open("linetimes.json", "w"))
d = [abs(a - b) for a, b in zip(Tm, Tc)]
print("줄", len(lines), "mlx-cpp 차 중앙", sorted(d)[len(d)//2], "0.3초 넘는 줄", sum(x > 0.3 for x in d))
