import json,re,subprocess,difflib,bisect,sys
tl=json.load(open("tl_v1.json"))
GT={12:50.900,17:68.170,32:127.169,41:163.912,50:195.903,52:203.553,97:364.143,104:385.687,107:395.354,120:446.216,133:496.541,146:540.468,158:586.369,162:598.144,165:610.434,167:616.311,196:723.698,198:729.254,204:750.264,215:789.761}
off={s["slide"]:s.get("src_offset",0) for s in tl["slides"]}
subs={x["n"]:x for x in tl["subs"]}
gt_src={n:t-off[subs[n]["slide"]] for n,t in GT.items()}
def norm(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]",c)]
lines=[x["text"] for x in tl["subs"]]
sch=[];sl=[]
for i,t in enumerate(lines):
    for c in norm(t): sch.append(c); sl.append(i)
def char_times(words):
    tch=[];tt=[]
    for a,b,w in words:
        cs=norm(w)
        for k,c in enumerate(cs): tch.append(c); tt.append(a+(b-a)*k/max(1,len(cs)))
    sm=difflib.SequenceMatcher(None,sch,tch,autojunk=False); st=[None]*len(sch)
    for a,b,n in sm.get_matching_blocks():
        for k in range(n): st[a+k]=tt[b+k]
    idx=[i for i,v in enumerate(st) if v is not None]
    for i in range(len(st)):
        if st[i] is None:
            j=bisect.bisect(idx,i); lo=idx[j-1] if j>0 else idx[0]; hi=idx[j] if j<len(idx) else idx[-1]
            st[i]=st[lo] if hi==lo else st[lo]+(st[hi]-st[lo])*(i-lo)/(hi-lo)
    first={}
    for i,l in enumerate(sl): first.setdefault(l,st[i])
    return [first[i] for i in range(len(lines))]
mlx=[(a,b,w) for a,b,w in json.load(open("mlxwords.json"))]
cpp=[(w["offsets"]["from"]/1000,w["offsets"]["to"]/1000,w["text"]) for w in json.load(open("wfull.json"))["transcription"]]
Tm=char_times(mlx); Tc=char_times(cpp)
json.dump({"mlx":Tm,"cpp":Tc},open("linetimes.json","w"))
v1={n:subs[n]["voice_on"]-off[subs[n]["slide"]] for n in GT}
print("line  gt    v1err  mlxerr cpperr")
for n in GT:
    g=gt_src[n]; print(n, round(g,2), round(v1[n]-g,3), round(Tm[n-1]-g,3), round(Tc[n-1]-g,3))
