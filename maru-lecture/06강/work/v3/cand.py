# 06강 v3 후보 자리 계산: 걸린 12 문장마다 모든 어절 경계 → (앞/뒤 공백뺀 글자, line_break 판정, 쏠림) + 한 장 잉크 폭
import json,sys,importlib.util
sp=importlib.util.spec_from_file_location("lb","../../../검수/검사기/line_break_check.py");lb=importlib.util.module_from_spec(sp);sys.argv=['x'];sp.loader.exec_module(lb)
from PIL import ImageFont
F=ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf",58)
def W(t): return sum(F.getlength(c) for c in t)-0.78*(len(t)-1)
S=json.load(open("../../타임라인_v2.json"))["subs"]
G=[9,17,18,23,36,44,59,61,74,81,90,93,110,119,123,132,136,142,145,146,149,151,162,166,177,189,199,211,218,223]
# 걸린 문장 (short_card 결과 기준) 첫 줄 인덱스 → 문장 줄 모음
import subprocess,re
out=subprocess.run(["python3","../../../검수/검사기/short_card_check.py","../../타임라인_v2.json"],capture_output=True,text=True).stdout
hits=sorted(set(int(m) for m in re.findall(r"#(\d+)",out)))
def L(t): return len(t.replace(' ',''))
done=set()
for h in hits:
    # 문장 묶음 찾기: short_card 출력 줄 텍스트로
    line=[l for l in out.splitlines() if l.startswith(f"걸림 #{h} ")][0]
    full_cards=line.split(" | ",1)[1].split(" / ")
    # 첫 카드 인덱스
    i0=h
    while S[i0]["text"]!=full_cards[0]: i0-=1
    if i0 in done: continue
    done.add(i0)
    idx=list(range(i0,i0+len(full_cards)))
    full=" ".join(full_cards); ws=full.split()
    print(f"\n== #{i0} 장{S[i0]['slide']} [{len(full)}자 공백포함 · 폭 {W(full):.0f}px] {' / '.join(full_cards)}")
    for k in range(1,len(ws)):
        a=" ".join(ws[:k]); b=" ".join(ws[k:])
        bad,why=lb.reason(a,b)
        la,lb_=L(a),L(b); r=min(la,lb_)/max(la,lb_)
        flag=("OK " if not bad else "X  ")
        print(f"   {flag}{la:2d}/{lb_:2d} r{r:.2f} 폭{max(W(a),W(b)):.0f} | {a} / {b}  {'' if not bad else why}")
