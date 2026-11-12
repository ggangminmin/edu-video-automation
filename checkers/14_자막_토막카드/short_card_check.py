#!/usr/bin/env python3
"""14 자막 토막 카드 — 한 문장을 여러 자막 카드로 나눴는데 한 장이 너무 짧아 자막바가 비어 보이는 것.
출처: 2026-11-09 마루시공 04~10강 민석 「공장에서는」「설치된 구역은」「11강에서는」 — 18강 #30 「소매와 끈, 장신구,」 다음 두 번째 지적.
기준(같은 문장 카드가 2장 이상일 때만):
  ① 공백 뺀 글자 < --min(기본 10) = 걸림   (민석 본보기 「…되는지는 / 별도로 확인해야 합니다」 10자 = 통과)
  ② 짧은 쪽/긴 쪽 < 0.45 이고 짧은 쪽 < 16 = 걸림(한쪽 쏠림)
  한 카드짜리 문장은 안 본다.
입력:
  · 마루시공식 타임라인 json(subs[] 에 text·start·slide, 문장시작 표시 how=='문장시작' 또는 sent_start, 선택 part)
  · .srt — 문장 경계 = 앞 카드가 다/요/죠/까/니다/세요/./?/! 로 끝남 (2줄 카드는 한 줄로 이어 봄)
사용: python3 short_card_check.py <타임라인.json | 자막.srt> [--min 10]   종료 0 = 통과 · 1 = 걸림
"""
import json,re,sys,argparse
ap=argparse.ArgumentParser();ap.add_argument('src');ap.add_argument('--min',type=int,default=10);a=ap.parse_args()
END=('다','요','죠','까','니다','세요','.','?','!')
def L(t): return len(t.replace(' ',''))
def ts(t):
    h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
if a.src.lower().endswith('.srt'):
    s=[];blocks=re.split(r'\n\s*\n',open(a.src,encoding='utf-8-sig').read().strip())
    for b in blocks:
        ln=[x for x in b.splitlines() if x.strip()]
        k=next((i for i,x in enumerate(ln) if '-->' in x),None)
        if k is None: continue
        s.append({'start':ts(ln[k].split('-->')[0].strip()),'text':' '.join(ln[k+1:]).strip(),'slide':0})
else:
    s=json.load(open(a.src,encoding='utf-8'))['subs']
groups=[];cur=[]
for x in s:
    if cur:
        p=cur[-1];pt=x.get('part');ppt=p.get('part')
        endprev=p['text'].rstrip().endswith(END)
        start=(x.get('how')=='문장시작') or x.get('sent_start') is True or x.get('slide')!=p.get('slide') or pt!=ppt or ((pt is not None or 'how' not in x) and endprev)
        if start: groups.append(cur);cur=[]
    cur.append(x)
if cur: groups.append(cur)
bad=[]
for g in groups:
    if len(g)<2: continue
    ls=[L(x['text']) for x in g]
    for k,x in enumerate(g):
        why=f'짧음 {ls[k]}자' if ls[k]<a.min else (f'쏠림 {ls[k]}/{max(ls)}' if ls[k]/max(ls)<0.45 and ls[k]<16 else None)
        if why:
            m,sec=divmod(x['start'],60)
            bad.append(f"걸림 #{s.index(x)} {int(m)}:{sec:05.2f} {why} | "+' / '.join(y['text'] for y in g))
print('\n'.join(bad));print(f"합계 {len(bad)} (문장 {len(groups)})")
sys.exit(1 if bad else 0)
