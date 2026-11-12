# make_tl05.py 앞부분(정렬·줄 나눔·줄 시작)만 돌려 줄 목록 확인(warp 전)
import sys; sys.argv = ["make_tl05.py", "dry"]
src = open("make_tl05.py").read().split("# ---------- 아나운서 warp 결과")[0]
exec(compile(src, "make_tl05_part", "exec"))
import json
json.dump(dict(LINES=[{k: (v if not isinstance(v, float) else round(v, 3)) for k, v in x.items()} for x in LINES], DIS=DIS, EXC=sorted(EXC_BREAK)), open("part_lines.json", "w"), ensure_ascii=False, indent=0)
for x in LINES: print(x.get("slide"), len(x["text"]), x["text"], "|", x.get("how"), round(x["on"], 2))
# 문장 시작 점검: SON vs mlx/cpp 첫 어절 시각
bad=[]
for si,(s,toks) in enumerate(SENTS):
    tm,tc,om,oc=tok_t[(si,0)]
    d=[round(SON[si]-tm,2) if om else None, round(SON[si]-tc,2) if oc else None]
    if any(x is not None and abs(x)>0.35 for x in d): bad.append((si,s," ".join(toks)[:18],round(SON[si],2),round(tm,2),round(tc,2),om,oc))
print("문장시작 의심", len(bad))
for b in bad: print("  ",b)
