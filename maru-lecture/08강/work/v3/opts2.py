import json
exec(open("plan_v3.py").read().split("plans = []")[0])
for g in groups:
    if not bad(g): continue
    w=" ".join(s[i]["text"] for i in g).split(); full=" ".join(w); part=s[g[0]].get("part")
    print(f"\n{g} 공백포함{len(full)} | {full}")
    for c in range(1,len(w)):
        a=" ".join(w[:c]); b=" ".join(w[c:]); la,lb_=L(a),L(b)
        r=lb.reason(a,b,part); m_=min(la,lb_); bal = m_>=10 and not (m_/max(la,lb_)<0.45 and m_<16)
        if not bal: continue
        print(f"   {c:2d} 길이{len(a)}/{len(b)} 글자{la}/{lb_} {'✗LB' if r[0] else 'lb✓'} {'>35' if max(len(a),len(b))>35 else ''} …{w[c-1]} / {w[c]}")
