# 08강 v3 토막 카드 나눔 계획(오더 51) — short_card_check 와 같은 문장 묶음 · 35자 안 = 한 장 · 넘으면 고르게(line_break 허용 · 짧은쪽≥12 · 비≥0.45)
import json, sys, itertools, importlib.util
W = "../../.."
spec = importlib.util.spec_from_file_location("lb", f"{W}/검수/검사기/line_break_check.py"); lb = importlib.util.module_from_spec(spec)
sys.argv_bak = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(lb); sys.argv = sys.argv_bak
s = json.load(open("../../타임라인_v2.json"))["subs"]
def L(t): return len(t.replace(" ", ""))
groups = []; cur = []
for i, x in enumerate(s):
    pt = x.get('part'); ppt = s[cur[-1]].get('part') if cur else None
    endprev = bool(cur) and s[cur[-1]]['text'].rstrip().endswith(('다','요','죠','까','니다','세요','.','?'))
    start = (x.get('how')=='문장시작') or x.get('sent_start') is True or not cur or x['slide']!=s[cur[-1]]['slide'] or pt!=ppt or (pt is not None and endprev)
    if start and cur: groups.append(cur); cur = []
    cur.append(i)
if cur: groups.append(cur)
def bad(g):
    if len(g) < 2: return False
    ls = [L(s[i]['text']) for i in g]
    return any(l < 10 or (l / max(ls) < 0.45 and l < 16) for l in ls)
plans = []
for g in groups:
    if not bad(g): continue
    words = " ".join(s[i]["text"] for i in g).split()
    full = " ".join(words); part = s[g[0]].get("part")
    old_cut = []; k = 0
    for i in g[:-1]: k += len(s[i]["text"].split()); old_cut.append(k)
    if len(full) <= 35:
        plans.append(dict(g=g, cards=[full], cuts=[], how="한 장 합침")); continue
    best = None
    for nc in (2, 3):
        for cuts in itertools.combinations(range(1, len(words)), nc - 1):
            parts = [" ".join(words[a:b]) for a, b in zip((0,) + cuts, cuts + (len(words),))]
            if any(len(p) > 35 for p in parts): continue
            ls = [L(p) for p in parts]
            if min(ls) < 12 or min(ls) / max(ls) < 0.45: continue
            if any(lb.reason(parts[j], parts[j + 1], part)[0] for j in range(nc - 1)): continue
            score = max(ls) - min(ls)
            if best is None or score < best[0]: best = (score, list(cuts), parts)
        if best: break
    if best: plans.append(dict(g=g, cards=best[2], cuts=best[1], old_cut=old_cut, how=f"고르게 {len(best[2])}장"))
    else: plans.append(dict(g=g, cards=None, cuts=None, how="자리 없음(손으로)", full=full))
for p in plans:
    print(p["g"], p["how"], "|", " / ".join(s[i]["text"] for i in p["g"]), "\n    →", " / ".join(p["cards"] or ["??"]), [len(c) for c in (p["cards"] or [])])
json.dump(plans, open("plan_v3.json", "w"), ensure_ascii=False, indent=1)
