# -*- coding: utf-8 -*-
"""앞 판 ↔ 새 판 비교 — 「지적한 곳 말고 바뀐 데가 있나」를 기계가 찾는다. 읽기 전용.

    python3 _dev/qa/qa_diff.py 앞판.mp4 새판.mp4 --allow 10:17-10:25 --allow 13:50-14:05 --out <폴더>

- 두 판의 길이가 달라도 된다(쉼을 넣거나 뺀 판). 0.1초 단위로 같은 장면을 찾아 맞춘 뒤 비교한다.
- 바뀐 구간을 세 갈래로 나눈다: 화면(자막바 위) · 자막바 · 소리.
- --allow 는 새 판 시각. 그 범위(앞뒤 1초 여유) 밖의 변경 = 「지적 밖 변경」 → 사람이 봐야 할 목록.
- 결과: <out>/diff_report.md · diff.json · 구간마다 앞|새 프레임 비교 jpg(sheets/).
원본 영상은 읽기만 한다. 쓰는 파일은 전부 --out 아래.
"""
import argparse, json, subprocess, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa_feat import FPS, SUB_FRAC, W, H, SW, SH, load, tc, parse_tc, probe_dur, sub_frac

# 문턱 — 같은 판을 다시 인코딩했을 때의 잡음보다 충분히 위 (README 「문턱 근거」)
V_SAME = 3.0        # 64x36 축소 평균 절대차(0~255). 이 아래면 「같은 장면」(맞추기용)
B_SAME = 8.0        # 맞추기용 칸 최댓값 문턱(같은 소스면 0~2)
B_CHG = 6.0         # linemax(12px 칸 안 줄 평균차 최댓값). 이 위면 「바뀐 화면」 — 같은 소스 잡음 90%=1, 2px 테두리 변경=14
BLK = 12
A_CHG = 3.0         # 24밴드 로그에너지 평균 절대차(dB). 소리가 날 때만 본다
A_FLOOR = -50.0     # 두 판 모두 이보다 조용한 창은 소리 비교에서 뺀다(룸톤 잡음)
SEARCH = 60 * FPS   # 다시 맞출 때 앞뒤로 찾는 범위(60초)
RUN = 15            # 다시 맞출 때 연속으로 같아야 하는 창 수(1.5초)


def vdist(a, b):
    return np.abs(a - b).mean(axis=(-1, -2))


def blockmax(x, y):
    """두 장(…,h,w) 차이를 BLK 칸 평균으로 → 칸 최댓값. 글자 한 칸 바뀐 것도 잡힌다"""
    d = np.abs(x.astype(np.int16) - y.astype(np.int16))
    h, w = d.shape[-2] // BLK * BLK, d.shape[-1] // BLK * BLK
    d = d[..., :h, :w].reshape(*d.shape[:-2], h // BLK, BLK, w // BLK, BLK).mean(axis=(-3, -1))
    return d.max(axis=(-2, -1))


def linemax(x, y):
    """칸(BLK) 안 가로줄·세로줄 평균 차의 최댓값 → 칸 최댓값. 2px 테두리처럼 가는 선도 잡힌다"""
    d = np.abs(x.astype(np.int16) - y.astype(np.int16)).astype(np.float32)
    h, w = d.shape[-2] // BLK * BLK, d.shape[-1] // BLK * BLK
    d = d[..., :h, :w].reshape(*d.shape[:-2], h // BLK, BLK, w // BLK, BLK)
    return np.maximum(d.mean(axis=-1).max(axis=-2), d.mean(axis=-3).max(axis=-1)).max(axis=(-2, -1))


def align(vo, vn, VO, VN):
    """새 판 각 창 i → 앞 판 창 j (없으면 -1).
    같다 = 축소 평균차 ≤ V_SAME **그리고** 칸 최댓값 ≤ B_SAME (비슷한 다른 화면에 붙지 않게 엄격히).
    안 맞으면 오프셋을 그대로 둔다(제자리 수정). RUN 창이 연속으로 다른 오프셋에서 맞을 때만 옮긴다."""
    N, M = len(vn), len(vo)
    mp = np.full(N, -1, int)
    off, i, lost = 0, 0, 0
    same = lambda i, j: (np.abs(vn[i] - vo[j]).mean() <= V_SAME) and blockmax(VO[j], VN[i]) <= B_SAME
    while i < N:
        hit = None
        for dj in (0, 1, -1, 2, -2):
            j = i + off + dj
            if 0 <= j < M and same(i, j):
                hit = j; break
        if hit is not None:
            mp[i] = hit; off = hit - i; lost = 0; i += 1; continue
        lost += 1
        if lost >= 3 and i + RUN <= N:
            seg = vn[i:i + RUN]
            lo, hi = max(0, i + off - SEARCH), min(M - RUN, i + off + SEARCH)
            if hi > lo:
                cands = np.arange(lo, hi + 1)
                good = cands[vdist(vo[cands], seg[0]) <= V_SAME]
                for j in good[np.argsort(np.abs(good - (i + off)))]:
                    if j - i == off:
                        continue
                    if (vdist(vo[j:j + RUN], seg).max() <= V_SAME
                            and blockmax(VO[j:j + RUN], VN[i:i + RUN]).max() <= B_SAME):
                        off = j - i; lost = 0; break
                else:
                    lost = -RUN          # 못 찾았으면 RUN 창 동안 재탐색 쉬기(속도)
                if lost == 0:
                    continue
        i += 1
    return mp


def runs(mask, min_len=2, gap=5):
    """참인 창 묶음 → [(시작창, 끝창)] (gap 창 이하로 떨어진 건 하나로)"""
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return []
    out = [[idx[0], idx[0]]]
    for k in idx[1:]:
        if k - out[-1][1] <= gap:
            out[-1][1] = k
        else:
            out.append([k, k])
    return [(a, b + 1) for a, b in out if b + 1 - a >= min_len]


def frame_jpg(src, t, dst, w=480):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, t):.2f}', '-i', str(src),
                    '-frames:v', '1', '-vf', f'scale={w}:-2', str(dst)], check=True)


def sheet(old, new, t_old, t_new, dst, label):
    tmp = dst.with_suffix('')
    a, b = Path(f'{tmp}_a.jpg'), Path(f'{tmp}_b.jpg')
    frame_jpg(new, t_new, b)
    if t_old is not None:
        frame_jpg(old, t_old, a)
        fc = "[0][1]hstack"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(a), '-i', str(b), '-filter_complex', fc,
                        str(dst)], check=True)
        a.unlink(missing_ok=True)
    else:
        b.rename(dst)
    b.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old'); ap.add_argument('new')
    ap.add_argument('--allow', action='append', default=[], help='새 판 시각 범위 10:17-10:25 (여러 번)')
    ap.add_argument('--out', required=True)
    ap.add_argument('--pad', type=float, default=1.0, help='허용 구간 앞뒤 여유(초)')
    ap.add_argument('--no-sheets', action='store_true')
    ap.add_argument('--screen', default=None, help='화면설정 json(자막바 위치). 없으면 환경변수 QA_SCREEN, 그것도 없으면 아래 22%%')
    a = ap.parse_args()
    frac, scr = sub_frac(a.screen)
    print(f'자막바 갈래 = 아래 {frac * 100:.1f}% ' + (f'(화면 설정 {scr})' if scr else '(기본값 — 화면 설정 없음)'), flush=True)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    cache = out / '_cache'
    print('특징 읽는 중(처음 한 번만 몇 분)…', flush=True)
    fo, fn = load(a.old, cache), load(a.new, cache)
    VO, VN = fo['v'], fn['v']                 # 192x108 uint8
    SUB_ROWS = int(round(SH * frac)); SUBR = int(round(H * frac / BLK)) * BLK
    small = lambda V: V.reshape(len(V), SH, H // SH, SW, W // SW).mean(axis=(2, 4), dtype=np.float32)
    vo, vn = small(VO), small(VN)
    mp = align(vo[:, :-SUB_ROWS], vn[:, :-SUB_ROWS], VO[:, :-SUBR], VN[:, :-SUBR])   # 자막만 바뀐 판도 장면이 맞도록 자막바는 빼고 맞춘다
    N = len(vn)
    ok = mp >= 0
    jj = np.where(ok, mp, 0)

    # 화면: 맞춘 짝끼리 영역별 차이. 짝이 없으면(새로 생긴 장면) 전부 「바뀜」
    # 짝이 안 잡힌 창은 앞뒤 짝의 오프셋으로 ±3창 안 최솟값을 쓴다(움직이는 구간의 인코딩 잡음·한 프레임 어긋남 흡수)
    offs = np.where(ok, mp - np.arange(N), np.nan)
    idx = np.arange(N)
    if ok.any():
        offs = np.interp(idx, idx[ok], offs[ok])
    jj = np.clip(np.round(idx + offs).astype(int), 0, len(vo) - 1)
    def best(region):
        r = slice(None, -SUBR) if region == 'body' else slice(-SUBR, None)
        d = np.empty(N, np.float32)
        for k in range(N):
            lo, hi = (jj[k], jj[k] + 1) if ok[k] else (max(0, jj[k] - 3), min(len(VO), jj[k] + 4))
            d[k] = linemax(VO[lo:hi, r], VN[k, r][None]).min()
        return d
    body, sub = best('body'), best('sub')
    np.savez(out / '_cache' / 'scores.npz', body=body, sub=sub, ok=ok, mp=mp)
    # 소리: 같은 짝으로
    na = min(N, len(fn['bands']))
    bn, rn = fn['bands'][:na], fn['rms'][:na]
    jo = np.clip(jj[:na], 0, len(fo['bands']) - 1)
    bo, ro = fo['bands'][jo], fo['rms'][jo]
    loud = np.maximum(rn, ro) > A_FLOOR
    ad = np.abs(bn - bo).mean(axis=1)
    aud = np.zeros(N, bool); aud[:na] = loud & (ad > A_CHG)
    rmsd = np.zeros(N); rmsd[:na] = rn - ro

    allow = []
    for s in a.allow:
        x, y = s.split('-')
        allow.append((parse_tc(x) - a.pad, parse_tc(y) + a.pad))

    def split(t0, t1):
        """[t0,t1) 를 허용 안/밖 조각으로 나눈다 → [(a,b,allowed)]"""
        cuts = sorted({t0, t1, *[max(t0, min(t1, v)) for x, y in allow for v in (x, y)]})
        out = []
        for a_, b_ in zip(cuts, cuts[1:]):
            if b_ - a_ < 0.05:
                continue
            m = (a_ + b_) / 2
            al = any(x <= m < y for x, y in allow)
            if out and out[-1][2] == al:
                out[-1] = (out[-1][0], b_, al)
            else:
                out.append((a_, b_, al))
        return out

    items = []
    for kind, mask in (('화면', body > B_CHG), ('자막바', (sub > B_CHG) & ~(body > B_CHG)), ('소리', aud)):
        for s0, e0 in runs(mask, min_len=3):   # 0.3초 미만 깜박 차이는 버린다(1프레임 검은 화면은 qa_scan 이 잡는다)
          for t0, t1, al in split(s0 / FPS, e0 / FPS):
            s, e = int(round(t0 * FPS)), int(round(t1 * FPS))
            if e - s < 2:
                continue
            seg = slice(s, e)
            new_scene = int((~ok[seg]).sum())
            it = {'kind': kind, 't0': round(t0, 1), 't1': round(t1, 1), 'tc': f'{tc(t0)}~{tc(t1)}',
                  'allowed': al, 'new_scene_windows': new_scene}
            if kind == '소리':
                it['avg_db_change'] = round(float(ad[s:min(e, na)].mean()), 1) if s < na else None
                it['level_change_db'] = round(float(rmsd[s:min(e, na)].mean()), 1) if s < na else None
            else:
                m = mp[s:e]; m = m[m >= 0]
                it['old_tc'] = f'{tc(m[0] / FPS)}~{tc((m[-1] + 1) / FPS)}' if len(m) else '(앞 판에 없음)'
                it['old_t'] = round(float(m[0] / FPS), 1) if len(m) else None
            items.append(it)
    items.sort(key=lambda d: d['t0'])

    # 길이·이동 요약
    dur_o, dur_n = probe_dur(a.old), probe_dur(a.new)
    shift = (mp - np.arange(N))[ok] / FPS
    outside = [d for d in items if not d['allowed']]
    rep = {'old': str(a.old), 'new': str(a.new), 'dur_old': round(dur_o, 2), 'dur_new': round(dur_n, 2),
           'matched_ratio': round(float(ok.mean()), 4), 'allow': a.allow,
           'n_changes': len(items), 'n_outside': len(outside), 'items': items}
    (out / 'diff.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))

    if not a.no_sheets:
        sd = out / 'sheets'; sd.mkdir(exist_ok=True)
        for k, d in enumerate(outside[:60]):
            tm = (d['t0'] + d['t1']) / 2
            i = min(int(tm * FPS), N - 1)
            to = mp[i] / FPS if mp[i] >= 0 else d.get('old_t')
            d['sheet'] = f'sheets/{k:02d}_{d["kind"]}_{d["t0"]:.1f}.jpg'
            sheet(a.old, a.new, to, tm, out / d['sheet'], d['kind'])
        (out / 'diff.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))

    L = [f'# 판 비교 — {Path(a.old).name} → {Path(a.new).name}', '',
         f'- 길이 {tc(dur_o)} → {tc(dur_n)} (차 {dur_n - dur_o:+.1f}초) · 같은 장면으로 맞춘 비율 {ok.mean() * 100:.1f}%',
         f'- 허용(지적) 구간: {", ".join(a.allow) or "없음"} (앞뒤 {a.pad}초 여유)',
         f'- 자막바 갈래: 아래 {frac * 100:.1f}% ' + (f'(화면 설정 `{scr}`)' if scr else '(기본값 · 화면 설정 없음)'),
         f'- 바뀐 구간 {len(items)}곳 · **지적 밖 {len(outside)}곳**', '']
    if outside:
        L += ['## ⚠ 지적 밖에서 바뀐 곳 (사람이 확인)', '', '| 새 판 시각 | 갈래 | 앞 판 시각 | 정도 | 비교 |', '|---|---|---|---|---|']
        for d in outside:
            deg = (f'소리 {d.get("avg_db_change")}dB 차 · 레벨 {d.get("level_change_db"):+}dB' if d['kind'] == '소리'
                   else ('새 장면' if d.get('new_scene_windows') else '화면 차이'))
            L.append(f'| {d["tc"]} | {d["kind"]} | {d.get("old_tc", "-")} | {deg} | {d.get("sheet", "")} |')
        L.append('')
    inn = [d for d in items if d['allowed']]
    if inn:
        L += ['## 지적 구간 안 변경 (의도한 수정)', '']
        L += [f'- {d["tc"]} · {d["kind"]}' for d in inn]
    (out / 'diff_report.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:6]))
    print(f'→ {out / "diff_report.md"}')


if __name__ == '__main__':
    main()
