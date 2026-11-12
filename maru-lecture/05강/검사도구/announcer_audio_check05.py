# 05강 사본(오더44): 강 폴더 = 두 자리(05강) · 인삿말 정답 = 강의인삿말/audio_8_* 그대로(검사기 규칙)
#!/usr/bin/env python3
"""아나운서 구간 소리 검사기 (지적 #8 · 지금_규칙 6·18)

잡는 것: 표지 인삿말 · 마지막 장 끝인사 구간에 **하이젠 클립 생성 소리**가 깔리면 걸린다.
  ① 이름: 타임라인 audio src 에 `_인삿말_090` · `_끝인사_090`(하이젠 클립 wav)이 있으면 실패.
     src 없이 clip 만 적힌 항목(소리 출처 모름)도 실패.
  ② 내용: src 소리의 포락선이 정답 소리와 상관 ≥ 0.95 여야 통과.
     인삿말 정답 = 강의인삿말/audio_(강−1) 0.9배 · 끝인사 정답 = 그 강 타입캐스트 0.9배(NN강/work/v090.wav) 안 어딘가.
  ③ (--mp4) 렌더된 mp4 의 그 구간 소리 ↔ 정답 소리 포락선 상관 ≥ 0.95 (BGM −20dB 섞여도 통과선 위).

사용: (_작업 에서) lockf -k .heavy.lock python3 검수/검사기/announcer_audio_check.py NN강/타임라인_v1.json [--mp4 NN강/NN강_v1.mp4]
종료코드 0 = 통과 · 1 = 걸림. 결과 표는 화면 + ~/Movies/video_qa/announcer_audio_check/<강>_<타임라인>.txt
"""
import sys, os, re, json, glob, subprocess, argparse
import numpy as np

SR = 16000; HOP = 0.02; TH = 0.95
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))   # 프로젝트 루트
WORK = os.path.join(ROOT, '_작업')
OUT = os.path.expanduser('~/Movies/video_qa/announcer_audio_check'); os.makedirs(OUT, exist_ok=True)

def decode(path, ss=None, t=None, af=None):
    cmd = ['ffmpeg', '-nostdin', '-loglevel', 'error']
    if ss is not None: cmd += ['-ss', f'{ss:.3f}']
    if t is not None: cmd += ['-t', f'{t:.3f}']
    cmd += ['-i', path, '-vn', '-ac', '1', '-ar', str(SR)]
    if af: cmd += ['-af', af]
    cmd += ['-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)

def env(x):
    n = int(SR * HOP); m = len(x) // n
    return np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1) + 1e-12)

def ncorr(a, b):
    a = a - a.mean(); b = b - b.mean(); d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0

def best_match(short, long_, lag=None):
    """long_ 안에서 short 와 가장 닮은 자리 (상관, 시작 프레임). lag 주면 ±lag 프레임만."""
    L = len(short); best = (-1.0, 0)
    rng = range(0, max(1, len(long_) - L + 1)) if lag is None else range(max(0, lag[0]), min(len(long_) - L, lag[1]) + 1)
    for i in rng:
        c = ncorr(short, long_[i:i + L])
        if c > best[0]: best = (c, i)
    return best

def resolve(src, tl_dir):
    for base in (tl_dir, WORK, ROOT):
        p = os.path.join(base, src)
        if os.path.exists(p): return p
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('timeline'); ap.add_argument('--mp4'); a = ap.parse_args()
    tl_path = os.path.abspath(a.timeline); tl_dir = os.path.dirname(tl_path)
    m = re.search(r'(\d+)강', tl_path); lec = int(m.group(1))
    tl = json.load(open(tl_path)); audio = tl.get('audio', [])
    last_slide = max(s['slide'] for s in tl['slides'])
    rows, fail = [], 0
    greet_ref = glob.glob(os.path.join(ROOT, '강의인삿말', f'audio_{lec - 1}_*'))
    v090 = os.path.join(WORK, f'{lec:02d}강', 'work', 'v090.wav')

    clips = [x for x in audio if x.get('src') or x.get('clip')]
    if not clips:
        rows.append(('-', '아나운서 클립 소리 항목 없음(본문 타입캐스트만)', '-', '통과'))
    for x in clips:
        kind = '인삿말' if x['slide'] == 1 else ('끝인사' if x['slide'] == last_slide else f'{x["slide"]}번')
        src = x.get('src')
        if not src:
            rows.append((kind, f'clip={x.get("clip")} · src 없음(소리 출처 모름)', '-', '실패')); fail += 1; continue
        if re.search(r'_(인삿말|끝인사)_090', os.path.basename(src)):
            rows.append((kind, f'{src} = 하이젠 클립 소리', '-', '실패')); fail += 1; continue
        p = resolve(src, tl_dir)
        if not p:
            rows.append((kind, f'{src} 파일 없음', '-', '실패')); fail += 1; continue
        s = env(decode(p, x.get('src_from', 0), x.get('src_to', 0) - x.get('src_from', 0) or None))
        if kind == '인삿말':
            if not greet_ref: rows.append((kind, '강의인삿말 원본 못 찾음', '-', '실패')); fail += 1; continue
            ref = env(decode(greet_ref[0], af='atempo=0.9'))
            # 짧은 쪽을 긴 쪽 안에서 찾는다
            c, i = best_match(s, ref) if len(s) <= len(ref) else best_match(ref, s)
            refname = os.path.basename(greet_ref[0])[:10] + '… ×0.9'
        elif '중간점_새음성' in src:   # 🆕11/3 오더36: 새 중간점 나레이션 조각 → 정답 = 중간점_새음성/중간점_090.wav(민석 새 타입캐스트 0.9배) 안 어딘가 · 옛판 announcer_audio_check_v2.py
            kind += '(새 나레이션)'; c, i, o_, NP = -1, 0, 0.0, ''
            for np_ in sorted(glob.glob(os.path.join(WORK, '중간점_새음성', '*_090.wav'))):   # 🆕11/4 오더38: 14강_수정_090.wav(지직 문장 새 나레이션)도 후보 · 옛판 announcer_audio_check_v3.py · 🆕오더37: 민석 새 나레이션 0.9배 원본 여러 개(12·14강 중간점_090 · 19강_중간점_090) 중 가장 맞는 것
                for o in (0.0, 0.005, 0.01, 0.015):   # 🆕11/3 14강 p1J: 자른 시작(6.69·13.31)이 20ms 칸 반 칸 → 0.935 → 정답을 5ms 씩 어긋나게 디코드해 가장 높은 값
                    r_ = env(decode(np_, o))
                    cc, ii = best_match(s, r_) if len(r_) >= len(s) else (-1, 0)   # 조각보다 짧은 원본은 후보 아님
                    if cc > c: c, i, o_, NP = cc, ii, o, np_
            refname = f'{os.path.basename(NP)[:-4]} @{i * HOP + o_:.3f}초'
        else:
            ref = env(decode(v090)); c, i = best_match(s, ref); refname = f'{lec}강 v090 @{i * HOP:.2f}초'
        ok = c >= TH; fail += (not ok)
        rows.append((kind, f'{src} ↔ {refname}', f'{c:.3f}', '통과' if ok else '실패'))
        if a.mp4 and ok:
            dur = len(s) * HOP
            # 🆕11/2 오검출 고침: 디코드 시작을 out 과 20ms 칸이 맞게(out−0.5, 0 밑이면 out % HOP) — max(0,…) 로 자르면 out<0.5 강(12강 인삿말 0.39)이 반 칸 어긋나 0.945
            st = x['out'] - 0.5
            if st < 0: st = x['out'] % HOP
            mix = env(decode(a.mp4, st, dur + 1.0))
            c2, _ = best_match(s, mix)
            ok2 = c2 >= TH; fail += (not ok2)
            rows.append((kind + '(mp4)', f'{os.path.basename(a.mp4)} {x["out"]:.2f}초~ ↔ {src}', f'{c2:.3f}', '통과' if ok2 else '실패'))
    head = f'# 아나운서 소리 검사 · {os.path.relpath(tl_path, WORK)} · 기준 상관 ≥ {TH}'
    lines = [head, '| 구간 | 무엇 | 상관 | 판정 |', '|---|---|---|---|'] + [f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} |' for r in rows]
    lines.append(f'\n결과: {"걸림 " + str(fail) + "건" if fail else "통과"}')
    txt = '\n'.join(lines); print(txt)
    open(os.path.join(OUT, f'{lec}강_{os.path.splitext(os.path.basename(tl_path))[0]}.txt'), 'w').write(txt + '\n')
    sys.exit(1 if fail else 0)

if __name__ == '__main__':
    main()
