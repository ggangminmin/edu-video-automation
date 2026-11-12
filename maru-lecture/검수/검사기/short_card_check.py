#!/usr/bin/env python3
"""short_card_check — 한 문장을 여러 자막 카드로 나눴을 때 너무 짧은 토막 카드(바가 비어 보임).
민석 11/9 「공장에서는」「설치된 구역은」「확인해야 합니다」(10강) · 앞서 지적 #30(18강 「소매와 끈, 장신구,」) → 두 번째라 검사기.
기준: 같은 문장(문장시작~다음 문장시작 전, 같은 장)의 카드가 2장 이상일 때
  ① 공백 뺀 글자 < MIN(기본 10 — 🆕11/9 민석 본보기 「…되는지는 / 별도로 확인해야 합니다」 10자 = 통과) 인 카드 = 걸림
  ② 짧은 쪽/긴 쪽 글자 비 < 0.45 이고 짧은 쪽 < 16 = 걸림(한쪽으로 쏠린 나눔)
  🆕11/9 인삿말·끝인사 자막도 봄(민석 「11강에서는」 끝인사) · 한 카드짜리 문장(「첫 번째 문제입니다」 등)은 안 봄.
고칠 때: 문장을 가운데 가까운 자연스러운 자리(연결어미·쉼표 뒤)에서 고르게 나누거나, 35자 안이면 한 장으로 합친다. line_break_check 도 같이 통과해야 함.
사용: python3 검수/검사기/short_card_check.py NN강/타임라인_vN.json [--min 12]   종료 1 = 걸림
"""
import json,sys,argparse
ap=argparse.ArgumentParser();ap.add_argument('tl');ap.add_argument('--min',type=int,default=10);a=ap.parse_args()
s=json.load(open(a.tl))['subs']
def L(t): return len(t.replace(' ',''))
groups=[];cur=[]
for i,x in enumerate(s):
    pt=x.get('part');ppt=s[cur[-1]].get('part') if cur else None
    endprev = bool(cur) and s[cur[-1]]['text'].rstrip().endswith(('다','요','죠','까','니다','세요','.','?'))
    start = (x.get('how')=='문장시작') or x.get('sent_start') is True or not cur or x['slide']!=s[cur[-1]]['slide'] or pt!=ppt or (pt is not None and endprev)
    if start and cur: groups.append(cur); cur=[]
    cur.append(i)
if cur: groups.append(cur)
bad=[]
for g in groups:
    if len(g)<2: continue
    ls=[L(s[i]['text']) for i in g]
    for k,i in enumerate(g):
        why=None
        if ls[k]<a.min: why=f'짧음 {ls[k]}자'
        elif ls[k]/max(ls)<0.45 and ls[k]<16: why=f'쏠림 {ls[k]}/{max(ls)}'
        if why:
            m,sec=divmod(s[i]['start'],60)
            bad.append((i,f"{int(m)}:{sec:05.2f}",s[i]['slide'],why,' / '.join(s[j]['text'] for j in g)))
for b in bad: print(f"걸림 #{b[0]} {b[1]} {b[2]}장 {b[3]} | {b[4]}")
print(f"합계 {len(bad)} (문장 {len(groups)})")
sys.exit(1 if bad else 0)
