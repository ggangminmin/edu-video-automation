# 줄 나눔 후보 자리마다 실제 쉼(5ms −40dB 연속 최장) — 07강 담당 줄 나눔 근거
import json,re,difflib,bisect,sys,numpy as np
sys.path.insert(0,"../../검수/검사기"); from line_break_check import reason
def norm(s): return [c for c in s if re.match(r"[가-힣0-9A-Za-z]", c)]
notes=json.load(open("../notes_clean.json"))
sents=[]
for si,p in enumerate(notes,1):
    for para in p:
        for s in re.split(r"(?<=[.?])\s+", para.strip()):
            s=s.strip()
            if s.endswith("."): s=s[:-1]
            if s: sents.append((si,s))
sch,owner=[],[]
for k,(si,s) in enumerate(sents):
    for i,c in enumerate(s):
        if re.match(r"[가-힣0-9A-Za-z]",c): sch.append(c); owner.append((k,i))
mlx=json.load(open("mlxwords.json"))
tch,tt=[],[]
for a,b,w in mlx:
    cs=norm(w)
    for j,c in enumerate(cs): tch.append(c); tt.append(a+(b-a)*j/max(1,len(cs)))
sm=difflib.SequenceMatcher(None,sch,tch,autojunk=False); st=[None]*len(sch)
for a,b,n in sm.get_matching_blocks():
    for j in range(n): st[a+j]=tt[b+j]
pos={o:i for i,o in enumerate(owner)}
DB=np.load("rmsdb.npy"); H=0.005
def pause(t):
    i0,i1=int((t-0.6)/H),int((t+0.3)/H); best=0;run=0
    for v in DB[max(0,i0):i1]:
        run=run+1 if v<-40 else 0; best=max(best,run)
    return best*H
want=set(sys.argv[1:])
for k,(si,s) in enumerate(sents):
    if len(s)<=35 and not any(w in s for w in want): continue
    print(f"## {si}장 ({len(s)}) {s}")
    for i,ch in enumerate(s):
        if ch!=" ": continue
        L,R=s[:i],s[i+1:]
        if len(L)<5 or len(R)<5: continue
        # 다음 글자 시각
        j=i+1
        while (k,j) not in pos: j+=1
        t=st[pos[(k,j)]]
        p=pause(t) if t else -1
        v,why=reason(L,R)
        if p>=0.05 or not v: print(f"   {p:.2f}s {'위반' if v else 'ok  '} {len(L):2d}/{len(R):2d} …{L[-10:]} / {R[:10]}…")
