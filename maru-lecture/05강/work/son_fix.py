# 문장 시작 재검: 앞 문장 마지막 어절(mlx 시작) ~ 이 문장 첫 어절(mlx 시작)+1.4 안 가장 긴 무음(−40dB ≥0.08) 끝 = 문장 시작 후보 → make_tl SON 과 비교
import sys, json; sys.argv = ["make_tl05.py", "dry"]
src = open("make_tl05.py").read().split("# ---------- 줄 나눔")[0]
exec(compile(src, "part", "exec"))
last_k = {}
for si, (s, toks) in enumerate(SENTS): last_k[si] = len(toks) - 1
out = []
for si in range(1, len(SENTS)):
    lw = tok_t[(si - 1, last_k[si - 1])][0]; fw = tok_t[(si, 0)][0]
    c = [(b - a, a, b) for a, b in SIL8 if a >= lw - 0.1 and b <= fw + 1.4]
    if not c: out.append((si, "후보없음", round(SON[si], 2))); continue
    d, a, b = max(c)
    if abs(b - SON[si]) > 0.05: out.append((si, SENTS[si][0], " ".join(SENTS[si][1])[:16], "SON", round(SON[si], 3), "→", round(b, 3), "쉼", round(d, 2)))
print(len(out))
for o in out: print(o)
json.dump({" ".join(SENTS[o[0]][1])[:14]: o[6] for o in out if len(o) > 6}, open("son_fix.json", "w"), ensure_ascii=False, indent=0)
