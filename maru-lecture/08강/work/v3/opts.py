import json
exec(open("plan_v3.py").read().split("plans = []")[0])
for g in groups:
    if not bad(g): continue
    w=" ".join(s[i]["text"] for i in g).split(); full=" ".join(w); part=s[g[0]].get("part")
    print(f"\n{g} {len(full)}자 | {full}")
    for c in range(1,len(w)):
        a=" ".join(w[:c]); b=" ".join(w[c:]); la,lb_=L(a),L(b)
        if len(a)>35 or len(b)>35: continue
        r=lb.reason(a,b,part); print(f"   {c:2d} {len(a)}/{len(b)} {min(la,lb_)/max(la,lb_):.2f} {'✗' if r[0] else '✓'} …{w[c-1]} / {w[c]}  ({r[1][:20]})")
