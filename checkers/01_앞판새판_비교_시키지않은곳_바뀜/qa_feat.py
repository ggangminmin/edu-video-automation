# -*- coding: utf-8 -*-
"""검수 공용 — 영상·소리를 0.1초 단위 특징으로 읽는다. 읽기 전용(원본을 고치지 않는다).

영상 : 10fps · 192x108 회색조(맞추기는 64x36 축소). 화면을 세 칸으로 나눠 따로 본다.
       full(전체) · sub(아래 자막바 22%) · body(자막바 위)
소리 : 16kHz 모노 · 0.1초 창 · 24밴드 로그 에너지(dB) + RMS(dBFS)
특징은 out 폴더에 npz 로 캐시한다(같은 파일·같은 크기면 재사용).
"""
import hashlib, json, os, subprocess
from pathlib import Path
import numpy as np

FPS = 10
W, H = 192, 108          # 저장 해상도(자막 띄어쓰기 한 칸도 보이게)
SW, SH = 64, 36          # 맞추기용 축소
SR = 16000
HOP = SR // FPS
SUB_FRAC = 0.22                      # 아래 22% = 자막바 (화면 설정이 없을 때 기본값)
BLK_SUB = 12                         # qa_diff 의 칸 크기(BLK)와 같다 — 자막바 갈래는 이 칸 단위로 잘린다


def sub_frac(screen=None):
    """자막바 갈래 비율. 화면 설정(--screen 또는 환경변수 QA_SCREEN)에 subbar 가 있으면 그 위 가장자리부터 아래 끝까지를
    BLK_SUB 칸 단위로 올림해 자막바 전체가 갈래 안에 들게 한다. 설정이 없으면 SUB_FRAC(0.22) 그대로.
    국가데이터처(1920x1080 · 바 y933) → 24/108 = 0.222 → 0.22 와 같은 줄 수(회귀 같음, 10/19)."""
    p = screen or os.environ.get('QA_SCREEN')
    if not p:
        return SUB_FRAC, None
    S = json.load(open(os.path.expanduser(p), encoding='utf-8'))
    b, fh = S.get('subbar'), (S.get('frame') or {}).get('h')
    if not b or not fh:
        return SUB_FRAC, p
    rows = -(-(fh - b['y']) * H // (fh * BLK_SUB)) * BLK_SUB
    return min(rows, H - BLK_SUB) / H, p


def probe_dur(p):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'json', str(p)], capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)['format']['duration'])


def _key(p):
    st = os.stat(p)
    return hashlib.md5(f'{Path(p).resolve()}|{st.st_size}|{int(st.st_mtime)}|v3'.encode()).hexdigest()[:12]


def video_frames(p):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(p), '-an', '-vf',
           f'fps={FPS},scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).copy()


def audio_samples(p):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(p), '-vn', '-ac', '1', '-ar', str(SR),
           '-f', 's16le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def audio_bands(a, n_bands=24):
    n = len(a) // HOP
    fr = a[:n * HOP].reshape(n, HOP)
    rms = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
    win = np.hanning(HOP).astype(np.float32)
    spec = np.abs(np.fft.rfft(fr * win, axis=1)) ** 2
    edges = np.unique(np.geomspace(2, spec.shape[1] - 1, n_bands + 1).astype(int))
    bands = np.stack([spec[:, edges[i]:edges[i + 1]].sum(axis=1) for i in range(len(edges) - 1)], 1)
    return 10 * np.log10(bands + 1e-10), rms


def load(p, cache_dir):
    cache_dir = Path(cache_dir); cache_dir.mkdir(parents=True, exist_ok=True)
    c = cache_dir / f'feat_{_key(p)}.npz'
    if c.exists():
        z = np.load(c)
        return {k: z[k] for k in z.files}
    v = video_frames(p)
    a = audio_samples(p)
    bands, rms = audio_bands(a)
    d = {'v': v, 'bands': bands, 'rms': rms}
    np.savez_compressed(c, **d)
    return d


def tc(t):
    t = max(0.0, float(t))
    return f'{int(t // 60)}:{t % 60:04.1f}'


def parse_tc(s):
    """'15:41' · '15:41.5' · '941.5' → 초"""
    s = s.strip()
    if ':' in s:
        m, x = s.split(':', 1)
        return int(m) * 60 + float(x)
    return float(s)
