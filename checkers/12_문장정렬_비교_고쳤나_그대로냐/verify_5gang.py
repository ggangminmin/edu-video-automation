# 검수기 12 검산 — 5강 앞판 vs 정답판 결과(pairs.json)를 반장 실측 정답(바뀐구간_목록 Z0~Z24) · 검수 판정과 맞춰 본다.
# 사용: python3 verify_5gang.py <5강 결과 pairs.json> <같은판 결과 pairs.json> <바뀐구간_목록.md> <검수_판정.md>
import json, re, sys
from collections import Counter

res, same, zmd, judge = sys.argv[1:5]
d = json.load(open(res)); s2 = json.load(open(same))['summary']
P = d['pairs']; S = d['summary']
sec = lambda m, s: int(m) * 60 + float(s)
fmt = lambda t: f'{int(t // 60)}:{t % 60:04.1f}'

def rng(t):
    return [(sec(m[0], m[1]), sec(m[2], m[3])) for m in re.findall(r'(\d+):(\d+(?:\.\d)?)\s*~\s*(\d+):(\d+(?:\.\d)?)', t)]

def table(md, first):
    out = []
    for line in open(md, encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if line.startswith('|') and re.match(first, c[0]): out.append(c)
    return out

def why(p):
    w = []
    if p['text'] != '같음': w.append('말' if p['text'] == '바뀜' else p['text'])
    if p.get('screen_chg'): w.append('화면' + ('(작음)' if p.get('screen_level') == '작음' else ''))
    if p.get('audio_chg'): w.append('소리')
    return '+'.join(w)

def hits(a, b):
    return [p for p in P if p['changed'] and p['new_s'] is not None and p['new_s'] < b and p['new_e'] > a]

print('① Z0~Z24 잡음')
caught, rows = 0, []
for c in table(zmd, r'Z\d+$'):
    z, newt, what = c[0], c[1], c[3]
    rg = rng(newt)
    if z == 'Z0':
        n = sum(bool(p.get('screen_chg') or p.get('layout_moved')) for p in P if p.get('screen'))
        ok = n / S['pairs'] >= 0.5; ev = f'화면 바뀜·자리 옮김 {n}/{S["pairs"]}문장'
    elif z == 'Z1':
        ok = abs(S['len_diff']) > 1 and (S['slowed'] + S['sped'] >= 0.1 * S['pairs'] or S['gap_added'] > 5)
        ev = f'길이 {S["len_diff"]:+}초 · 느려짐 {S["slowed"]} 빨라짐 {S["sped"]} · 쉼 늘림 {S["gap_added"]}초'
    elif z == 'Z24':
        ts = re.findall(r'(\d+):(\d+)(?:~(\d+):(\d+))?', what)
        got = 0
        for m in ts:
            a = sec(m[0], m[1]); b = sec(m[2], m[3]) if m[2] else a
            got += bool(hits(a - 1, b + 1))
        ok = got >= len(ts) / 2; ev = f'적힌 시각 {got}/{len(ts)} 곳에 바뀐 문장'
    else:
        h = [p for a, b in rg for p in hits(a, b)]
        ok = bool(h); ev = f'{len(h)}문장 ' + ', '.join(f'{fmt(p["new_s"])}({why(p)})' for p in h[:3])
    caught += ok; rows.append((z, ok, ev))
    print(f'  {z:4} {"잡음" if ok else "놓침"}  {ev}')
print(f'  → {caught}/{len(rows)}')

print(f'② 같은 판 vs 같은 판: 바뀐 문장 {s2["changed"]} (화면 {s2["screen_chg"]} · 소리 {s2["audio_chg"]} · 말 {s2["text_chg"]})')

print('③ 장부 줄 판정 vs 검수 판정(✅=바뀌어야 · ❌=안 바뀌어야, ?는 정답 없음)')
J = {}
for c in table(judge, r'[JM]\d+[a-z]?$'):
    if len(c) >= 2 and ('✅' in c[1] or '❌' in c[1] or '?' in c[1]): J[c[0]] = '✅' if '✅' in c[1] else '❌' if '❌' in c[1] else '?'
L = {x['num']: x for x in d['ledger']}
agree = Counter(); miss = []
for k, v in J.items():
    if v == '?' or k not in L: continue
    t = L[k]['verdict']
    good = (v == '✅' and t == '바뀜') or (v == '❌' and t.startswith('안 바뀜'))
    agree[good] += 1
    if not good: miss.append(f'{k}(검수 {v} · 기계 {t}: {L[k]["why"]})')
n = agree[True] + agree[False]
print(f'  일치 {agree[True]}/{n} = {agree[True] / max(n, 1) * 100:.0f}%')
for m in miss: print('   어긋남', m)
print('  기계 판정 전체:', dict(Counter(x['verdict'] for x in d['ledger'])))

print('③-2 Z 「장부가 덮음/못 덮음」 vs 채점표(나) 검수 판정')
cov = {}
for c in table(judge, r'Z\d+$'):
    if len(c) >= 2 and '덮음' in c[1]: cov[c[0]] = '못 덮음' if '못' in c[1] else '덮음'
out = set(d['outside']); agreeZ = 0; tot = 0; diff = []
for c in table(zmd, r'Z\d+$'):
    z = c[0]
    rg = rng(c[1])
    if not rg or z not in cov: continue
    h = [p for a, b in rg for p in hits(a, b)]
    if not h: continue
    o = [p for p in h if p['i'] in out]
    mine = '못 덮음' if o else '덮음'
    tot += 1; agreeZ += mine == cov[z]
    if mine != cov[z]: diff.append(f'{z}(검수 {cov[z]} · 기계 {mine}: 지적 밖 {len(o)}/{len(h)}문장 {", ".join(fmt(p["new_s"]) for p in o[:4])})')
print(f'  시각 있는 Z {tot}곳 중 일치 {agreeZ} = {agreeZ / max(tot, 1) * 100:.0f}%')
for x in diff: print('   어긋남', x)
