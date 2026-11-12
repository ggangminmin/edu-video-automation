# 07강 v3 토막 카드 후보(오더 51) — short_card_check 묶음 · 한 장 잉크 폭 · 2장 후보(line_break 허용 · 짧은쪽≥10 · 비≥0.45)
import json, sys, importlib.util
sys.path.insert(0, "."); from ink import ink
W = "../../.."
spec = importlib.util.spec_from_file_location("lb", f"{W}/검수/검사기/line_break_check.py"); lb = importlib.util.module_from_spec(spec)
bak = sys.argv; sys.argv = ["x"]; spec.loader.exec_module(lb); sys.argv = bak
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
for g in groups:
    if len(g) < 2: continue
    ls = [L(s[i]['text']) for i in g]
    if not any(l < 10 or (l / max(ls) < 0.45 and l < 16) for l in ls): continue
    words = " ".join(s[i]["text"] for i in g).split(); full = " ".join(words); part = s[g[0]].get("part")
    print(f"\n{g} {s[g[0]]['slide']}장 part={part} | " + " / ".join(s[i]['text'] for i in g))
    print(f"   한 장 {len(full)}자 폭 {ink(full)}px")
    for c in range(1, len(words)):
        a, b = " ".join(words[:c]), " ".join(words[c:])
        r = lb.reason(a, b, part); sh = min(L(a), L(b)); ratio = sh / max(L(a), L(b))
        mark = "OK" if (not r[0] and sh >= 10 and ratio >= 0.45) else "  "
        print(f"   {mark} {'위반' if r[0] else '허용'}({r[1]}) {L(a)}/{L(b)} {ratio:.2f} 폭{ink(a)}/{ink(b)} | {a} / {b}")
