# 오더23: 최신 타임라인_v3.json(fix23_tl) 위에 자막 시작 고침(delta = 새 말 시작 − 옛 말 시작, 줄 글로 대조)을 모아 적용 → 새 판 타임라인
# 실행: python3 오더23/apply_deltas.py NN 출력이름 fix_subs_a.json [fix_subs_b.json ...] [--line n:기준타임라인:검사json]
import sys, json
FPS = 30000 / 1001; q = lambda t: round(t * FPS) / FPS
N, OUT = sys.argv[1:3]; D = f"{N}강"; fixes = {}
args = sys.argv[3:]
for a in args:
    if a.startswith("--line"): continue
for i, a in enumerate(args):
    if a == "--line":
        n, base, chk = args[i + 1].split(":"); n = int(n)
        bt = {x["n"]: x for x in json.load(open(f"{D}/{base}"))["subs"]}; r = {s["n"]: s for s in json.load(open(chk))["sync"]}
        fixes[bt[n]["text"]] = dict(d=r[n]["voice_t"] - bt[n]["voice_on"], src=f"{chk} n{n}")
    elif not a.startswith("--") and (i == 0 or args[i - 1] != "--line"):
        for k, f in json.load(open(a))["fix"].items(): fixes[f["text"]] = dict(d=f["new_voice"] - f["old_voice"], src=a)
tl = json.load(open(f"{D}/타임라인_v3.json")); L = tl["subs"]; done = []
for i, x in enumerate(L):
    if x["text"] in fixes:
        f = fixes[x["text"]]; vt = x["voice_on"] + f["d"]; st = q(vt - 0.09)
        assert i > 0 and L[i - 1]["slide"] == x["slide"] and st > L[i - 1]["start"], x
        x["start"] = st; x["voice_on"] = round(vt, 3); x["how"] = "scene_sub 고침(" + OUT + ")"; L[i - 1]["end"] = st; done.append((x["n"], round(f["d"], 3), f["src"]))
assert len(done) == len(fixes), (len(done), len(fixes))
tl["params"]["deltas_" + OUT] = done
json.dump(tl, open(f"{D}/{OUT}", "w"), ensure_ascii=False, indent=1)
print(N, OUT, "고친 줄", len(done), done)
