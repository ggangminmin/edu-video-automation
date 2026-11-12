"""screen_cfg.py — 검수기 02~05 공통: 프로젝트 화면 설정(자막바 위치 · 색) 읽기.
설정 = `--screen <json>` 또는 환경변수 QA_SCREEN. 없으면 멈춘다(국가데이터처 숫자를 몰래 쓰지 않는다).
양식 `minstack/검수기/화면설정_양식.json` · 예시 `화면설정_예시_국가데이터처.json` · 재는 도구 `minstack/도구/자막바_재기.py`."""
import sys, os, json
from fractions import Fraction

NEED = ['fps', 'subbar', 'text_area', 'bar_fill', 'bar_fill_tol', 'text_dark_max', 'border', 'border_tol', 'border_line', 'border_check', 'sheet_crop']
HOW = ('화면 설정이 없다 — 자막바 위치를 먼저 재라.\n'
       '  1) python3 minstack/도구/자막바_재기.py <영상.mp4> <자막 떠 있는 초> <초> … --out <폴더>\n'
       '     → 확인 그림(상자 그린 것)을 눈으로 보고 화면설정.json 초안을 고친다\n'
       '  2) 검수기에 --screen <화면설정.json> 을 붙이거나 export QA_SCREEN=<화면설정.json>\n'
       '  (국가데이터처 숫자 = minstack/검수기/화면설정_예시_국가데이터처.json)')


def load(argv=None):
    """argv 에서 --screen <json> 을 빼고(위치 인자 번호가 그대로 맞게) 설정을 돌려준다."""
    argv = sys.argv if argv is None else argv
    p = None
    if '--screen' in argv:
        i = argv.index('--screen'); p = argv[i + 1]; del argv[i:i + 2]
    p = p or os.environ.get('QA_SCREEN')
    if not p:
        sys.exit(HOW)
    p = os.path.expanduser(p)
    if not os.path.exists(p):
        sys.exit(f'화면 설정 파일이 없다: {p}\n' + HOW)
    S = json.load(open(p, encoding='utf-8'))
    miss = [k for k in NEED if k not in S]
    if miss:
        sys.exit(f'화면 설정 {p} 에 칸이 빠졌다: {", ".join(miss)} (양식 = 화면설정_양식.json)')
    S['fps'] = float(Fraction(str(S['fps'])))
    S['_path'] = p
    return S


def rgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def crop(b):
    """{'x','y','w','h'} → ffmpeg crop=w:h:x:y"""
    return f"crop={b['w']}:{b['h']}:{b['x']}:{b['y']}"
