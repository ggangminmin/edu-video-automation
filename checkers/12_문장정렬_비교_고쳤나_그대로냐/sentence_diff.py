# 검수기 12 — 문장 정렬 비교: 판 길이 · 화면 구성이 바뀐 판에서도 문장마다 앞·새 짝을 맞춰 「바뀌었나」를 잰다.
# 사용: python3 sentence_diff.py 앞판.mp4 새판.mp4 [--ledger 지적장부.md] [--stt-old a.json --stt-new b.json] --out 폴더
# 결과: <out>/report.md · pairs.json(앞→새 시각 대응표) · cmp/NNN.jpg(앞|새 비교 그림, 바뀐 칸 빨간 상자)
# 원본은 읽기만 한다. 중간 파일(stt · wav · 프레임)은 out 안에 두고 있으면 다시 쓰지 않는다(resume-safe).
import argparse, json, os, re, subprocess, difflib, wave, math
import numpy as np, cv2

WHISPER_MODEL = os.path.expanduser('~/.cache/whisper-cpp/ggml-large-v3-turbo.bin')
POS = (0.2, 0.5, 0.8)          # 문장 안에서 뽑는 자리(앞 · 가운데 · 뒤)
W, H = 640, 360                # 비교 해상도
TILE = 40                      # 칸 크기(640 기준)
DX, DY = 160, 40               # 칸이 옮겨 갔어도 찾는 폭(640 기준 = 1920 에서 ±480 · ±120 px)
TEX_STD = 6.0                  # 이보다 밋밋한 칸은 안 센다
FOUND = 0.80                   # 이 상관 이상이면 「같은 그림 있음」
SCREEN_CHG = 0.10              # 못 찾은 칸 비율이 이보다 크면 화면 바뀜(큼)
SCREEN_SMALL = 0.04            # 세 자리 모두 이 이상이면 화면 바뀜(작음: 글자 한 줄 · 입 · 아이콘). 지나가는 움직임과 가르려고 세 자리 다
AUDIO_SAME = 0.75              # 문장 소리 스펙트럼 상관이 이보다 낮으면 소리 바뀜
TEXT_SAME = 0.90               # 받아쓰기 글자 일치율(이상 = 말 같음)

def run(cmd): subprocess.run(cmd, check=True)

def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', p]).decode().strip())

def wav16(src, dst):
    if not os.path.exists(dst):
        run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '16000', dst])
    return dst

def stt(src, out, tag):
    js = f'{out}/stt/{tag}.json'
    if not os.path.exists(js):
        run(['whisper-cli', '-m', WHISPER_MODEL, '-l', 'ko', '-oj', '-of', js[:-5], '-f', f'{out}/stt/{tag}.wav'])
    return js

def load_stt(js):
    t = json.load(open(js))['transcription']
    return [dict(s=x['offsets']['from'] / 1000, e=x['offsets']['to'] / 1000, text=x['text'].strip()) for x in t]

norm = lambda s: re.sub(r'[^가-힣A-Za-z0-9]', '', s)
ratio = lambda a, b: difflib.SequenceMatcher(None, norm(a), norm(b), autojunk=False).ratio()

def chars(S):
    """받아쓰기 → 글자 한 줄 + 글자마다 시각(문장 안에서 고르게 나눔)."""
    txt, tim = [], []
    for s in S:
        t = norm(s['text'])
        for k, ch in enumerate(t):
            txt.append(ch); tim.append(s['s'] + (s['e'] - s['s']) * (k + 0.5) / len(t))
    return ''.join(txt), tim

def align(O, N):
    """글자 단위로 두 판 받아쓰기를 맞춘 뒤 새판 문장을 한 단위로 앞판 시각을 붙인다.
    (쉼을 넣으면 받아쓰기가 문장을 다르게 끊으므로 문장끼리 맞추면 같은 말도 「바뀜」이 된다.)"""
    to, tmo = chars(O); tn, tmn = chars(N)
    sm = difflib.SequenceMatcher(None, to, tn, autojunk=False)
    n2o = {}
    for b in sm.get_matching_blocks():
        for k in range(b.size): n2o[b.b + k] = b.a + k
    rows, used, pos = [], set(), 0
    starts = []
    for s in N:
        L = len(norm(s['text'])); starts.append((pos, pos + L)); pos += L
    ostarts, pos = [], 0
    for s in O:
        L = len(norm(s['text'])); ostarts.append((pos, pos + L)); pos += L
    for j, (a, b) in enumerate(starts):
        m = [n2o[k] for k in range(a, b) if k in n2o]
        if not m:
            rows.append((None, N[j])); continue
        lo, hi = min(m), max(m)
        used.update(range(lo, hi + 1))
        o = dict(s=tmo[lo] - (tmo[min(lo + 1, len(tmo) - 1)] - tmo[lo]) / 2, e=tmo[hi] + (tmo[hi] - tmo[max(hi - 1, 0)]) / 2,
                 text=''.join(to[lo:hi + 1]))
        # 문장 경계를 쓰는 쪽이 정확하면 그 값을 쓴다(앞판 문장과 통째로 같은 경우)
        for i, (oa, ob) in enumerate(ostarts):
            if oa == lo and ob == hi + 1: o = dict(O[i]); break
            if oa == lo: o['s'] = O[i]['s']
            if ob == hi + 1: o['e'] = O[i]['e']
        o['ratio'] = len(m) / max(b - a, hi - lo + 1)
        rows.append((o, N[j]))
    # 앞판에만 있는 글자 덩어리(빠진 말)
    for i, (oa, ob) in enumerate(ostarts):
        if ob > oa and sum(k in used for k in range(oa, ob)) / (ob - oa) < 0.3:
            rows.append((O[i], None))
    keys = [p[1]['s'] if p[1] else _new_at(rows, p[0]) for p in rows]
    return [p for _, p in sorted(zip(keys, rows), key=lambda kp: kp[0])]

def _new_at(rows, o):
    """앞판에만 있는 문장을 새판 순서 안 제자리에 놓기 위한 정렬 값."""
    prev = [p[1]['s'] for p in rows if p[0] and p[1] and p[0]['s'] <= o['s']]
    return (max(prev) if prev else 0) + 0.001

def frames(src, times, cache, tag):
    """필요한 시각의 프레임만 640x360 으로 뽑아 jpg 로 둔다(있으면 건너뜀). 한 번 순서대로 훑는다."""
    os.makedirs(cache, exist_ok=True)
    cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
    want = sorted({int(round(t * fps)) for t in times})
    path = lambda f: f'{cache}/{tag}_{f:06d}.jpg'
    todo = [f for f in want if not os.path.exists(path(f))]
    if todo:
        i, k = 0, 0
        while k < len(todo):
            if todo[k] - i > 240:  # 멀면 건너뛰기(키프레임 탐색)
                cap.set(cv2.CAP_PROP_POS_FRAMES, todo[k] - 48); i = todo[k] - 48
            ok = cap.grab()
            if not ok: break
            if i == todo[k]:
                _, im = cap.retrieve()
                cv2.imwrite(path(i), cv2.resize(im, (W, H), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 95])
                k += 1
                while k < len(todo) and todo[k] <= i: k += 1
            i += 1
    cap.release()
    return lambda t: path(int(round(t * fps)))

def missing_tiles(a, b):
    """a 의 무늬 있는 칸마다 b 에서 (옮겨 갔어도) 찾는다. 못 찾은 칸 목록과 무늬 칸 수."""
    miss, n = [], 0
    for y in range(0, H - TILE + 1, TILE):
        for x in range(0, W - TILE + 1, TILE):
            t = a[y:y + TILE, x:x + TILE]
            if t.std() < TEX_STD: continue
            n += 1
            x0, y0 = max(0, x - DX), max(0, y - DY)
            win = b[y0:min(H, y + TILE + DY), x0:min(W, x + TILE + DX)]
            if cv2.matchTemplate(win, t, cv2.TM_CCOEFF_NORMED).max() < FOUND: miss.append((x, y))
    return miss, n

def screen_cmp(pa, pb):
    A, B = cv2.imread(pa), cv2.imread(pb)
    ga, gb = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    inplace = float(np.abs(cv2.blur(ga, (5, 5)).astype(int) - cv2.blur(gb, (5, 5)).astype(int)).mean())
    ma, na = missing_tiles(ga, gb); mb, nb = missing_tiles(gb, ga)
    chg = max(len(ma) / max(na, 1), len(mb) / max(nb, 1))
    return dict(inplace=round(inplace, 2), content=round(chg, 3)), A, B, ma, mb

def spec(x):
    """10ms 간격 로그 스펙트럼(0.1~4kHz, 배음이 갈리게 31Hz 해상도 2칸씩 묶음)과 프레임 세기."""
    if len(x) < 1600: return None, None
    fr = np.lib.stride_tricks.sliding_window_view(x, 512)[::160] * np.hanning(512)
    M = np.abs(np.fft.rfft(fr, axis=1))[:, 4:128]
    S = np.log(M.reshape(len(M), 62, 2).mean(2) + 1e-4)
    return S, np.log(M.sum(1) + 1e-6)

CH = 40   # 소리 조각 0.4초
def audio_corr(wa, wb, o, n):
    """앞판 문장을 0.4초 조각으로 잘라, 새판 문장(앞뒤 0.5초 여유) 안 제자리 근처(±0.6초)에서 가장 닮은 곳을 찾는다.
    같은 녹음이면(늘이거나 쉼을 넣어도) 조각마다 0.8 이상, 다시 만든 소리면 낮다. 조각 상관의 가운데값."""
    pad = 0.5
    a = wa[int(o['s'] * 16000):int(o['e'] * 16000)]
    b0 = max(0.0, n['s'] - pad); b = wb[int(b0 * 16000):int((n['e'] + pad) * 16000)]
    Sa, Ea = spec(a); Sb, _ = spec(b)
    if Sa is None or Sb is None or len(Sb) < CH + 1: return None
    loud = Ea > np.percentile(Ea, 40)
    out = []
    for c in range(0, len(Sa) - CH + 1, CH):
        if loud[c:c + CH].mean() < 0.5: continue
        t = Sa[c:c + CH].ravel(); t = (t - t.mean()) / (t.std() + 1e-9)
        exp = int(pad * 100 + c / max(len(Sa), 1) * (len(Sb) - 2 * pad * 100))
        lo, hi = max(0, exp - 60), min(len(Sb) - CH, exp + 60)
        if hi < lo: continue
        W_ = np.lib.stride_tricks.sliding_window_view(Sb, (CH, Sb.shape[1]))[lo:hi + 1, 0].reshape(hi - lo + 1, -1)
        W_ = (W_ - W_.mean(1, keepdims=True)) / (W_.std(1, keepdims=True) + 1e-9)
        out.append(float((W_ @ t).max() / len(t)))
    return round(float(np.median(out)), 3) if out else None

def readwav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

fmt = lambda t: '-' if t is None else f'{int(t // 60)}:{t % 60:04.1f}'

def secs(t):
    m = re.match(r'^\s*(\d+):(\d{2})(?:\.(\d))?\s*$', t or '')
    return int(m[1]) * 60 + int(m[2]) + (int(m[3]) / 10 if m[3] else 0) if m else None

def ranges(t):
    return [(secs(a), secs(b)) for a, b in re.findall(r'(\d+:\d{2}(?:\.\d)?)\s*~\s*(\d+:\d{2}(?:\.\d)?)', t or '')]

def read_ledger(p):
    rows, head = [], None
    for line in open(p, encoding='utf-8'):
        if not line.startswith('|'): head = None if not line.strip() else head; continue
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if set(''.join(c)) <= set('-: '): continue
        if c[0] == '#' and any('시각' in x for x in c): head = c; continue
        if head and len(c) == len(head): rows.append(dict(zip(head, c)))
    return rows

def old2new(pairs, t):
    """앞판 시각 → 새판 시각(짝 지은 문장 시작점 사이를 곧게 이음)."""
    pts = [(p['old_s'], p['new_s']) for p in pairs if p['old_s'] is not None and p['new_s'] is not None]
    xs, ys = [a for a, _ in pts], [b for _, b in pts]
    return float(np.interp(t, xs, ys, left=ys[0] - (xs[0] - t), right=ys[-1] + (t - xs[-1])))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old'); ap.add_argument('new')
    ap.add_argument('--ledger'); ap.add_argument('--stt-old'); ap.add_argument('--stt-new')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(os.path.expanduser(a.out)); os.makedirs(f'{out}/stt', exist_ok=True); os.makedirs(f'{out}/cmp', exist_ok=True)
    wo, wn = wav16(a.old, f'{out}/stt/old.wav'), wav16(a.new, f'{out}/stt/new.wav')
    so = a.stt_old or stt(a.old, out, 'old'); sn = a.stt_new or stt(a.new, out, 'new')
    O, N = load_stt(so), load_stt(sn)
    raw = align(O, N)
    do, dn = dur(a.old), dur(a.new)
    tO = [o['s'] + p * (o['e'] - o['s']) for o, n in raw if o and n for p in POS]
    tN = [n['s'] + p * (n['e'] - n['s']) for o, n in raw if o and n for p in POS]
    fo = frames(a.old, tO, f'{out}/frames', 'old'); fn = frames(a.new, tN, f'{out}/frames', 'new')
    WA, WB = readwav(wo), readwav(wn)
    pairs = []
    for k, (o, n) in enumerate(raw):
        p = dict(i=k, old_s=o and o['s'], old_e=o and o['e'], new_s=n and n['s'], new_e=n and n['e'],
                 text_old=o and o['text'], text_new=n and n['text'])
        if not (o and n):
            p.update(text='빠짐' if o else '추가', changed=True); pairs.append(p); continue
        r = o['ratio'] if 'ratio' in o else ratio(o['text'], n['text'])
        p['text_ratio'] = round(r, 3); p['text'] = '같음' if r >= TEXT_SAME else '바뀜'
        sc, worst = [], None
        for q in POS:
            ta, tb = o['s'] + q * (o['e'] - o['s']), n['s'] + q * (n['e'] - n['s'])
            m, A, B, ma, mb = screen_cmp(fo(ta), fn(tb))
            sc.append(m)
            if q == 0.5 or (worst and m['content'] > worst[0]['content']) or worst is None:
                if q == 0.5 or m['content'] > SCREEN_CHG * 2: worst = (m, A, B, ma, mb, ta, tb)
        p['screen'] = [s['content'] for s in sc]; p['inplace'] = [s['inplace'] for s in sc]
        p['screen_max'] = max(p['screen'])
        p['screen_chg'] = p['screen_max'] > SCREEN_CHG or min(p['screen']) >= SCREEN_SMALL
        p['screen_level'] = '큼' if p['screen_max'] > SCREEN_CHG else '작음' if p['screen_chg'] else '-'
        p['layout_moved'] = max(p['inplace']) > 6 and not p['screen_chg']
        p['audio'] = audio_corr(WA, WB, o, n)
        p['audio_chg'] = p['audio'] is not None and p['audio'] < AUDIO_SAME
        p['tempo'] = round((n['e'] - n['s']) / max(o['e'] - o['s'], 0.01), 3)
        p['changed'] = p['text'] == '바뀜' or p['screen_chg'] or p['audio_chg']
        # 비교 그림: 앞|새, 다른 판에서 못 찾은 칸 = 빨간 상자
        m, A, B, ma, mb, ta, tb = worst
        A, B = A.copy(), B.copy()
        for x, y in ma: cv2.rectangle(A, (x, y), (x + TILE - 1, y + TILE - 1), (0, 0, 255), 2)
        for x, y in mb: cv2.rectangle(B, (x, y), (x + TILE - 1, y + TILE - 1), (0, 0, 255), 2)
        bar = np.full((28, W * 2 + 8, 3), 255, np.uint8)
        cv2.putText(bar, f'#{k} old {fmt(ta)} | new {fmt(tb)}  screen {m["content"]:.2f}  audio {p["audio"]}  text {r:.2f}',
                    (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 200) if p['changed'] else (0, 0, 0), 1)
        img = np.vstack([bar, np.hstack([A, np.full((H, 8, 3), 255, np.uint8), B])])
        p['img'] = f'cmp/{k:03d}.jpg'; cv2.imwrite(f'{out}/{p["img"]}', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        pairs.append(p)
    both = [p for p in pairs if p['old_s'] is not None and p['new_s'] is not None]
    tempos = [p['tempo'] for p in both]
    gaps = []  # 문장 사이 쉼 변화(새 - 앞)
    for x, y in zip(both, both[1:]):
        gaps.append((y['new_s'] - x['new_e']) - (y['old_s'] - x['old_e']))
    summ = dict(old_len=round(do, 1), new_len=round(dn, 1), len_diff=round(dn - do, 1),
                sent_old=len(O), sent_new=len(N), pairs=len(both),
                text_chg=sum(p['text'] != '같음' for p in pairs), screen_chg=sum(p.get('screen_chg', False) for p in both),
                layout_moved=sum(p.get('layout_moved', False) for p in both),
                audio_chg=sum(p.get('audio_chg', False) for p in both), changed=sum(p['changed'] for p in pairs),
                tempo_median=round(float(np.median(tempos)), 3) if tempos else None,
                slowed=sum(t > 1.03 for t in tempos), sped=sum(t < 0.97 for t in tempos),
                gap_added=round(float(np.sum([g for g in gaps if g > 0])), 1), gap_cut=round(float(np.sum([g for g in gaps if g < 0])), 1))
    # 장부
    led = []
    if a.ledger:
        rows = read_ledger(a.ledger)
        for r in rows:
            num = r.get('#'); t = secs(r.get('시각', '')); given = secs(r.get('새판 시각', ''))
            grp = next((v for k, v in r.items() if k.startswith('묶음')), '')
            rg = [x for x in ranges(next((v for k, v in r.items() if '범위' in k), '')) if None not in x]
            item = dict(num=num, old=r.get('시각', ''), group=grp, given_new=r.get('새판 시각', ''))
            if t is None:
                whole = '전편' in r.get('시각', '')
                item.update(verdict='시각 못 맞춤', why='전편 지적 — 맨 위 「전편」 숫자로 본다' if whole else '시각 없음(미확인)')
                led.append(item); continue
            lo, hi = t - 1.0, t + 6.0                     # 지적 시각 = 그 장면 시작 → 뒤 6초까지
            for a0, b0 in rg:
                if a0 - 1 <= t <= b0 + 1: lo, hi = min(lo, a0), max(hi, b0)
            hit = [p for p in pairs if p['old_s'] is not None and p['old_s'] < hi and p['old_e'] > lo]
            item['new'] = fmt(old2new(pairs, t)); item['old_range'] = f'{fmt(lo)}~{fmt(hi)}'
            if given is not None: item['new_vs_given'] = round(old2new(pairs, t) - given, 1)
            if not hit:
                item.update(verdict='시각 못 맞춤', why='그 시각에 짝 지은 문장 없음'); led.append(item); continue
            ch = [p for p in hit if p['changed']]
            tempo_grp = any(w in grp for w in ('쉼', '템포', '속도'))
            what = []
            if any(p.get('screen_chg') for p in hit): what.append(f'화면 {sum(bool(p.get("screen_chg")) for p in hit)}/{len(hit)}문장')
            if any(p.get('text') != '같음' for p in hit): what.append('말')
            if any(p.get('audio_chg') for p in hit): what.append('소리')
            tp = [p['tempo'] for p in hit if p.get('tempo')]
            if tempo_grp and tp and (max(tp) > 1.03 or min(tp) < 0.97): what.append(f'길이 ×{min(tp):.2f}~{max(tp):.2f}')
            item['pairs'] = [p['i'] for p in hit]; item['imgs'] = [p.get('img') for p in hit if p.get('img')]
            if ch or what:
                item.update(verdict='바뀜', why=' · '.join(what))
            else:
                item.update(verdict='안 바뀜 ❌', why=f'{len(hit)}문장 화면 최대 {max(p.get("screen_max", 0) for p in hit):.2f} · 말 같음 · 소리 같음')
            led.append(item)
        covered = set(i for x in led for i in x.get('pairs', []))
        outside = [p for p in pairs if p['changed'] and p['i'] not in covered]
    else:
        outside = []
    json.dump(dict(summary=summ, pairs=pairs, ledger=led, outside=[p['i'] for p in outside],
                   thresholds=dict(SCREEN_CHG=SCREEN_CHG, SCREEN_SMALL=SCREEN_SMALL, AUDIO_SAME=AUDIO_SAME, TEXT_SAME=TEXT_SAME, FOUND=FOUND)),
              open(f'{out}/pairs.json', 'w'), ensure_ascii=False, indent=1)
    write_report(out, a, summ, pairs, led, outside)
    print(json.dumps(summ, ensure_ascii=False))
    if led:
        from collections import Counter
        print('장부', dict(Counter(x['verdict'] for x in led)), '지적 밖 후보', len(outside))

def write_report(out, a, s, pairs, led, outside):
    L = [f'# 문장 정렬 비교 — {os.path.basename(a.old)} → {os.path.basename(a.new)}', '',
         f'- 길이 {s["old_len"]}초 → {s["new_len"]}초 ({s["len_diff"]:+}초) · 받아쓰기 문장 {s["sent_old"]} → {s["sent_new"]} · 짝 {s["pairs"]}',
         f'- **바뀐 문장 {s["changed"]}** = 말 바뀜/빠짐/추가 {s["text_chg"]} · 화면 바뀜 {s["screen_chg"]} · 소리 바뀜 {s["audio_chg"]}',
         f'- 전편: 화면 「자리만 옮김」(내용 같음, 제자리 차 큼) {s["layout_moved"]}문장 · 문장 길이 비 가운데값 ×{s["tempo_median"]} (느려짐 {s["slowed"]} · 빨라짐 {s["sped"]}) · 문장 사이 쉼 늘림 합 {s["gap_added"]}초 · 줄임 합 {s["gap_cut"]}초',
         '- 화면 = 다른 판에서 (옮겨 갔어도) 못 찾은 칸 비율, 문장의 20% · 50% · 80% 자리 세 장 중 최대. 비교 그림의 빨간 상자 = 못 찾은 칸.', '']
    if led:
        from collections import Counter
        c = Counter(x['verdict'] for x in led)
        L += ['## 장부 판정', '', f'- ' + ' · '.join(f'{k} {v}' for k, v in c.items()) + f' · 지적 밖 후보 {len(outside)}문장', '',
              '| # | 앞 시각 | 새판 시각(계산) | 장부 새판 시각 | 판정 | 무엇이 | 비교 그림 |', '|---|---|---|---|---|---|---|']
        for x in led:
            L.append(f'| {x["num"]} | {x["old"]} | {x.get("new", "-")} | {x["given_new"]} | {x["verdict"]} | {x["why"]} | {" ".join(x.get("imgs", [])[:3])} |')
        L += ['', '## 지적 밖 후보(장부 시각 밖에서 바뀐 문장)', '', '| 짝 | 앞 | 새 | 말 | 화면 | 소리 | 문장 | 그림 |', '|---|---|---|---|---|---|---|---|']
        for p in outside:
            L.append(f'| {p["i"]} | {fmt(p["old_s"])} | {fmt(p["new_s"])} | {p["text"]} | {p.get("screen_max", "-")} | {p.get("audio", "-")} | {(p["text_new"] or p["text_old"])[:40]} | {p.get("img", "")} |')
        L.append('')
    L += ['## 문장 짝 표', '', '| 짝 | 앞 시각 | 새 시각 | 말 | 화면(20/50/80%) | 제자리 차 | 소리 상관 | 길이 비 | 판정 | 문장 | 그림 |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for p in pairs:
        L.append(f'| {p["i"]} | {fmt(p["old_s"])} | {fmt(p["new_s"])} | {p["text"]} | {"/".join(f"{v:.2f}" for v in p.get("screen", []))} {p.get("screen_level", "")} | '
                 f'{max(p["inplace"]) if p.get("inplace") else "-"} | {p.get("audio", "-")} | {p.get("tempo", "-")} | {"바뀜" if p["changed"] else "같음"} | '
                 f'{(p["text_new"] or p["text_old"])[:36]} | {p.get("img", "")} |')
    open(f'{out}/report.md', 'w').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    main()
