import sys,re
sys.path.insert(0,'검수/검사기'); from line_break_check import reason
from PIL import Image, ImageFont
import numpy as np
F=ImageFont.truetype('/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf',58)
def W(t): return round(sum(F.getlength(c) for c in t)-0.78*(len(t)-1))
a=np.array(Image.open('10강/work/bar.png').convert('RGB')).astype(int); row=a[958]; 
print('bar row958 non-bg cols', np.where(np.abs(row-row[0]).sum(1)>30)[0][[0,-1]] if (np.abs(row-row[0]).sum(1)>30).any() else None)
L=lambda t:len(t.replace(' ',''))
S=[l.strip() for l in open(sys.argv[1]) if l.strip()]
for s in S:
    w=s.replace(' / ',' ').split(' ')
    full=' '.join(w); print(f"\n== {len(full)}자 w{W(full)} {full}")
    for i in range(1,len(w)):
        a_,b_=' '.join(w[:i]),' '.join(w[i:]); la,lb=L(a_),L(b_)
        bad,why=reason(a_,b_)
        ok = min(la,lb)>=10 and min(la,lb)/max(la,lb)>=0.45 and len(a_)<=35 and len(b_)<=35
        if ok: print(f"  {'LB✗' if bad else 'OK '} {la}/{lb} | {a_} / {b_}  ({why})")
