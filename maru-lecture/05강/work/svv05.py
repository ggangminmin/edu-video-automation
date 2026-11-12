# 05강 메모 문장 ↔ 0.9배 녹음 받아쓰기(mlx · cpp) 대조: 문장 구간 = 이 문장 시작(SON) ~ 다음 문장 시작 → 글자 맞춤 비율(숫자 표기 정규화)
import sys, json, re, difflib; sys.argv = ["make_tl05.py", "dry"]
src = open("make_tl05.py").read().split("# ---------- 줄 나눔")[0]
exec(compile(src, "part", "exec"))
NUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5"}
def nz(s):
    s = re.sub(r"(일|이|삼|사|오) 번", lambda m: NUM[m.group(1)] + "번", s)
    return re.sub(r"[^가-힣0-9]", "", s)
M = [tuple(x) for x in json.load(open("mlxwords.json"))]
def seg(words, a, b): return " ".join(w for s_, e_, w in words if a - 0.05 <= (s_ + e_) / 2 < b).strip()
rows = []
for si, (s, toks) in enumerate(SENTS):
    a = SON[si] - 0.6; b = SON[si + 1] - 0.1 if si + 1 < len(SENTS) else DUR
    memo = " ".join(toks); hm, hc = seg(M, a, b), seg(cpp, a, b)
    rm = difflib.SequenceMatcher(None, nz(memo), nz(hm)).ratio(); rc = difflib.SequenceMatcher(None, nz(memo), nz(hc)).ratio()
    rows.append(dict(si=si, slide=s, memo=memo, mlx=hm, cpp=hc, r_mlx=round(rm, 3), r_cpp=round(rc, 3)))
json.dump(rows, open("svv05.json", "w"), ensure_ascii=False, indent=0)
low = [r for r in rows if max(r["r_mlx"], r["r_cpp"]) < 0.93]
print("문장", len(rows), "· 0.93 밑", len(low))
for r in low: print(f"[{r['slide']}] {max(r['r_mlx'],r['r_cpp']):.2f}\n  메모 {r['memo']}\n  mlx  {r['mlx']}\n  cpp  {r['cpp']}")
