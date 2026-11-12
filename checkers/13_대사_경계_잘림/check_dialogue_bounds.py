#!/usr/bin/env python3
"""13 대사 경계 잘림 — 소리 클립의 시작·끝·페이드가 말(목소리) 한가운데를 자르는지 숫자로 잡는다.
2026-10-26 마키 티저: 「대사 뚝뚝 끊긴다」(v02) → 고친 v03 도 「다 중간에 잘린다」(같은 실수 두 번째) → 검사기로.
입력 events.json = [{"label","voice"(그 클립 원본의 목소리 분리 wav),"src_in","src_out","tl","fi","fo"(초),
                    "speech":[말시작src, 말끝src] (대사 클립만, 선택)}]
판정(목소리 트랙 10ms 음량):
  ① 페이드 구간 + 경계 바깥 30ms 안의 목소리가 그 클립 목소리 피크 -30dB 이상 → 잘림(FAIL). 단 페이드 ≥ 8프레임이면 「의도한 페이드」(WARN, 사람이 확인).
  ② speech 가 페이드 안쪽에 온전히 들어가는지(여유 20ms).
  ③ 대사 클립끼리 타임라인에서 말이 겹치거나 0.1초 안으로 붙으면 FAIL.
사용: python3 check_dialogue_bounds.py events.json [--fps 24] [--out report.md]   → 종료코드 0 = 통과
목소리 분리: demucs --two-stems=vocals -n htdemucs (설치 ~/.local/share/meomuru-audio-env/bin/demucs)
"""
import json, sys, subprocess, argparse, numpy as np
_C = {}
def venv(p):
    if p not in _C:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-af', 'highpass=f=90', '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
        x = np.frombuffer(r, np.float32); h = 160; n = len(x) // h
        _C[p] = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-7)
    return _C[p]
def mx(e, a, b):
    i0, i1 = max(0, int(np.floor(a * 100))), min(len(e), int(np.ceil(b * 100)) + 1)
    return float(e[i0:i1].max()) if i1 > i0 else -140.0
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('events'); ap.add_argument('--fps', type=float, default=24); ap.add_argument('--out')
    ap.add_argument('--drop', type=float, default=30); a = ap.parse_args()
    ev = json.load(open(a.events)); rows = []; fails = 0; warns = 0
    for x in ev:
        si, so = x['src_in'], x['src_out']; fi, fo = x['fi'] / a.fps, x['fo'] / a.fps
        if not x.get('voice'): rows.append((x['label'], 'PASS', '목소리 없는 트랙(효과음 분리본) — 검사 제외')); continue
        e = venv(x['voice']); gpk = float(np.percentile(e, 99.5))
        pk = mx(e, si, so); lim = pk - a.drop; probs = []
        if pk < -60 or pk < gpk - 35: rows.append((x['label'], 'PASS', f'목소리 거의 없음(원본 목소리 피크 대비 {pk - gpk:+.0f}dB)')); continue
        hi = mx(e, si - .03, si + max(fi, .02)); ho = mx(e, so - max(fo, .02), so + .03)
        for nm, v, f in (('시작', hi, x['fi']), ('끝', ho, x['fo'])):
            if v >= lim:
                if f >= 8: probs.append(('WARN', f'{nm} 긴 페이드({f}f) 중 목소리 {v - pk:+.0f}dB — 의도한 사라짐인지 귀로'))
                else: probs.append(('FAIL', f'{nm} 잘림: 목소리 {v - pk:+.0f}dB (기준 -{a.drop:.0f}dB)'))
        if x.get('speech'):
            s0, s1 = x['speech']
            if s0 < si + fi + .02: probs.append(('FAIL', f'말 시작({s0:.2f})이 페이드인 안/앞'))
            if s1 > so - fo - .02: probs.append(('FAIL', f'말 끝({s1:.2f})이 페이드아웃 안/뒤'))
        st = 'FAIL' if any(p[0] == 'FAIL' for p in probs) else 'WARN' if probs else 'PASS'
        fails += st == 'FAIL'; warns += st == 'WARN'
        rows.append((x['label'], st, ' / '.join(p[1] for p in probs) or f'경계 목소리 시작{hi - pk:+.0f}dB 끝{ho - pk:+.0f}dB'))
    sp = sorted([(x['tl'] + x['speech'][0] - x['src_in'], x['tl'] + x['speech'][1] - x['src_in'], x['label']) for x in ev if x.get('speech')])
    for (a0, a1, l0), (b0, b1, l1) in zip(sp, sp[1:]):
        if b0 < a1 + .1: fails += 1; rows.append((f'{l0} ↔ {l1}', 'FAIL', f'말 겹침/붙음: {a1:.2f}s 끝 → {b0:.2f}s 시작'))
    rep = ['| 클립 | 판정 | 내용 |', '|---|---|---|'] + [f'| {l} | {s} | {m} |' for l, s, m in rows]
    rep.append(f'\n**FAIL {fails} · WARN {warns} · 클립 {len(ev)}**')
    txt = '\n'.join(rep); print(txt)
    if a.out: open(a.out, 'w').write(txt)
    sys.exit(1 if fails else 0)
if __name__ == '__main__': main()
