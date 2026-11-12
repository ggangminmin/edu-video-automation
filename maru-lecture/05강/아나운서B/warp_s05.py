# 05강 사본(오더44 · 20강 warp_s1920.py 그대로)
# 19·20강 사본(오더34 · 18강 p1V warp_s18.py + DRYJSON: 영상 없이 지도 json 만 써서 anchor_sync_check 로 값 고르기)
# 18강 사본(p1V 11/3 · ONSETPAIR 추가, 나머지 오더09_공용/warp_s.py 그대로) — 13강 아나운서 매끈 시안(민석 11/3 「클로징 싱크 안 맞음 · 자연스럽게」) — 오더09 warp_clip2.py 를 바탕으로 속도 곡선만 바꿈.
#  옛판(warp2): DTW → 0.15초 이동평균 → 10ms 마다 기울기 0.4~2.5 로 자름 → 자른 자리마다 속도가 꺾여 「틱틱」.
#  새판: DTW 지도를 가우시안으로 크게 부드럽게(SIGMA초) → 소리 시작점(입 벌리는 순간)에서 원래 DTW 와의 어긋남이 TOL 넘는 곳만 고정점으로 당김
#        → 속도를 다시 한 번 부드럽게 · 한도 SMIN~SMAX(꺾임 없이 넘친 만큼 주변에 나눔).
#  MODE=blend: 앞뒤 프레임 섞기(옛판과 같음) · MODE=flow: 원본을 광학흐름(minterpolate mci)으로 4배 촘촘히 만든 뒤 가장 가까운 프레임.
# 실행: python3 warp_s.py <clip.mp4> <clip.wav> <target.wav> <out.mp4> <out.json>   (env SIGMA TOL SMIN SMAX MODE)
import sys, os, json, subprocess, numpy as np, librosa
from scipy.ndimage import gaussian_filter1d
clip_mp4, clip_wav, tgt_wav, out_mp4, out_json = sys.argv[1:6]
SIGMA = float(os.environ.get("SIGMA", "0.35")); TOL = float(os.environ.get("TOL", "0.05"))
SMIN = float(os.environ.get("SMIN", "0.6")); SMAX = float(os.environ.get("SMAX", "1.7")); MODE = os.environ.get("MODE", "blend")
SR, HOP = 16000, 160
FPS_OUT = 30000 / 1001
def load(p): return librosa.load(p, sr=SR, mono=True)[0]
def db(y):
    fr = librosa.util.frame(np.pad(y, (0, HOP)), frame_length=HOP, hop_length=HOP)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7)
def span(y, d=-40):
    on = np.where(db(y) > d)[0]; return on[0] * HOP / SR, (on[-1] + 1) * HOP / SR
yc, yt = load(clip_wav), load(tgt_wav)
cs, ce = span(yc); ts, te = span(yt)
def feat(y, a, b):
    s = y[int(a * SR):int(b * SR)]
    m = librosa.feature.mfcc(y=s, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=512)[1:]
    m = (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
    e = librosa.feature.rms(y=s, hop_length=HOP, frame_length=512)[0]
    e = 20 * np.log10(e + 1e-6); e = (e - e.mean()) / (e.std() + 1e-6)
    return np.vstack([m, 3 * e])
Fc, Ft = feat(yc, cs, ce), feat(yt, ts, te)
_, wp = librosa.sequence.dtw(X=Ft, Y=Fc, metric="euclidean", step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0], [1, 2], [2, 1]]),
                             weights_add=np.array([0, 1, 1, 1, 1]))
wp = wp[::-1]; nt, nc = Ft.shape[1], Fc.shape[1]
raw = np.full(nt, np.nan)
for i in range(nt):
    s = wp[:, 0] == i
    if s.any(): raw[i] = wp[s, 1].mean()
raw = np.interp(np.arange(nt), np.where(~np.isnan(raw))[0], raw[~np.isnan(raw)]) * HOP / SR   # 초(클립 말 구간 안)
tau = np.arange(nt) * HOP / SR; T, C = tau[-1], (nc - 1) * HOP / SR
# 🆕 단어 짝 보정: 클립·타깃 받아쓰기 단어 시작(쉼 안 → 쉼 끝)을 글자로 짝지어, DTW 가 0.06초 넘게 어긋난 단어 자리만 DTW 지도를 끌어당김(13강 끝인사 「견적」 0.156)
import re, difflib
def wstarts(wav, y):
    j = wav.replace(".wav", "_words.json")
    if not os.path.exists(j): return []
    d_ = db(y); out = []
    for w, a, b in json.load(open(j))["words"]:
        t = re.sub(r"[^가-힣0-9]", "", w)
        if not t: continue
        i, k = int(a * 100), min(len(d_), int(b * 100))
        while i < k and d_[i] < -40: i += 1
        out.append((t, i / 100))
    return out
WP = []
if os.environ.get("WORDPAIR", "1") == "1":
    Cw, Tw = wstarts(clip_wav, yc), wstarts(tgt_wav, yt)
    for a, b, n in difflib.SequenceMatcher(None, [w[0] for w in Cw], [w[0] for w in Tw]).get_matching_blocks():
        for k in range(n):
            c_t, t_t = Cw[a + k][1], Tw[b + k][1]
            if cs <= c_t <= ce and ts <= t_t <= te: WP.append((t_t - ts, c_t - cs))
    fixw = [(t, c) for t, c in WP if abs(np.interp(t, tau, raw) - c) > 0.06]   # 이 단어들은 DTW 대신 받아쓰기 짝을 정답으로
    print("단어짝", len(WP), "DTW 대신 짝", [(round(t, 2), round(c, 2)) for t, c in fixw], file=sys.stderr)
else: fixw = []
def truth(t):
    for a_, c_ in fixw:
        if abs(a_ - t) < 0.015: return c_
    return float(np.interp(t, tau, raw))

# 타깃 소리 시작점(쉼 ≥0.08초 뒤) — 입이 맞아야 하는 곳
def onsets(y, a, b):
    d = db(y); out = []; run = 0
    for i in range(int(a * 100), min(len(d), int(b * 100))):
        if d[i] < -40: run += 1
        else:
            if run >= 8: out.append(i / 100 - a)
            run = 0
    return np.array(out)
on_t = onsets(yt, ts, te)
# 🆕18강 p1V: ONSETPAIR=1 — 쉼 뒤 말 시작점(onsetcheck 와 같은 정의)도 클립 쪽 가장 가까운 쉼 뒤 시작점과 짝지어 정답으로(DTW 가 쉼 시작을 0.13초 어긋낸 18강 인삿말 7.99)
if os.environ.get("ONSETPAIR") == "1":
    _co = onsets(yc, cs, ce); _grp = {}
    for _t in onsets(yt, ts, te):
        if _t < 0.05: continue
        _c = float(np.interp(_t, tau, raw)); _k = int(np.argmin(np.abs(_co - _c))) if len(_co) else None
        if _k is not None and abs(_co[_k] - _c) <= float(os.environ.get("OPWIN", "0.3")): _grp.setdefault(_k, []).append(float(_t))
    for _k, _ts in _grp.items():          # 타깃 시작점 여럿이 클립 시작점 하나에 걸리면 그 가운데로(양쪽 오차 반씩)
        _m = float(np.mean(_ts))
        for _t in _ts: fixw.append((_t, float(_co[_k]) + (_t - _m)))
    print("쉼짝", [(round(t, 2), round(c, 2)) for t, c in fixw], file=sys.stderr)
_wj = tgt_wav.replace(".wav", "_words.json")      # 단어 시작점도 입이 맞아야 하는 곳(받아쓰기 캐시 · 쉼 안에 찍힌 시작은 쉼 끝으로)
if os.environ.get("WORDS", "1") == "1" and os.path.exists(_wj):
    _d = db(yt); _ws = []
    for w in json.load(open(_wj))["words"]:
        i = int(w[1] * 100)
        while i < len(_d) - 1 and _d[i] < -40 and i < int(w[2] * 100): i += 1
        _ws.append(i / 100 - ts)
    on_t = np.array(sorted(set(np.round(np.concatenate([on_t, [t for t in _ws if 0 < t < te - ts]]), 2))))

if os.environ.get("PINS"):   # 🆕오더34: 소리 실측으로 정한 짝 「타깃초:클립초,…」(파일 절대 시각) — 자동 짝이 못 잡는 자리만
    _pp = [tuple(map(float, x.split(":"))) for x in os.environ["PINS"].split(",")]
    for _t, _c in _pp:
        fixw[:] = [f for f in fixw if abs(f[0] - (_t - ts)) > 0.05]; fixw.append((_t - ts, _c - cs))
    on_t = np.array(sorted(set(np.round(np.concatenate([on_t, [t - ts for t, c in _pp]]), 2))))
    print("PINS", _pp, file=sys.stderr)
def shape(cl):
    """기울기를 SMIN~SMAX 안으로(넘친 만큼 부드럽게 흩음) · 끝점 0,C 고정"""
    for _ in range(60):
        sp = np.gradient(cl, tau)
        spc = np.clip(sp, SMIN, SMAX)
        if np.abs(sp - spc).max() < 1e-3: break
        spc = gaussian_filter1d(spc, 5)
        cl = np.concatenate([[0], np.cumsum((spc[1:] + spc[:-1]) / 2 * np.diff(tau))]); cl *= C / cl[-1]
    return cl
def smooth(target_pts):
    """target_pts: [(τ, 원하는 c)] 를 지나가는 매끈한 곡선 = 원래 DTW 를 크게 부드럽게 + 고정점 보정(부드러운 범프)"""
    cl = gaussian_filter1d(raw, SIGMA * 100, mode="nearest"); cl = cl - cl[0]; cl *= C / cl[-1]
    for _ in range(8):
        if target_pts:
            x = np.array([p[0] for p in target_pts]); y = np.array([p[1] for p in target_pts])
            d = y - np.interp(x, tau, cl)
            corr = np.zeros(nt)
            for xi, di in zip(x, d): corr += di * np.exp(-0.5 * ((tau - xi) / max(0.12, SIGMA * 0.6)) ** 2)
            cl = cl + corr
        cl[0], cl[-1] = 0, C
        cl = shape(cl)
    return cl
pts = []
cl = smooth(pts)
for it in range(6):          # 시작점 어긋남 > TOL 인 곳만 고정점 추가
    dev = np.interp(on_t, tau, cl) - np.array([truth(t) for t in on_t])
    bad = [(t, truth(t)) for t, d in zip(on_t, dev) if abs(d) > TOL and all(abs(t - p[0]) > 0.05 for p in pts)]
    if not bad: break
    pts += bad; cl = smooth(pts)
dev = np.interp(on_t, tau, cl) - np.array([truth(t) for t in on_t])
sp = np.gradient(cl, tau)

if os.environ.get("DRYJSON"):
    json.dump(dict(mode=MODE, sigma=SIGMA, tol=TOL, smin=SMIN, smax=SMAX, clip=clip_mp4, target=tgt_wav, clip_speech=[round(cs, 3), round(ce, 3)], target_speech=[round(ts, 3), round(te, 3)],
                   map=[[round(float(a), 3), round(float(b), 3)] for a, b in zip(tau, cl)]), open(out_json, "w"), ensure_ascii=False); sys.exit()
if os.environ.get("DRY"):
    print(dict(sigma=SIGMA, smin=round(float(sp.min()),2), smax=round(float(sp.max()),2), jerk=round(float(np.abs(np.diff(sp)).max()*100),2), nfix=len(pts), dev_max=round(float(np.abs(dev).max()),3), dev_med=round(float(np.median(np.abs(dev))),3))); sys.exit()
clip_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip_mp4], capture_output=True, text=True).stdout)
spk = te - ts; Dout = cs + spk + (clip_dur - ce)
def c_of_u(u):
    if u < cs: return u
    if u < cs + spk: return cs + float(np.interp(u - cs, tau, cl))
    return ce + (u - cs - spk)

W_, H_ = 1080, 1920; FS = W_ * H_ * 3
rf = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", clip_mp4], capture_output=True, text=True).stdout.strip()
src_fps = eval(rf); VF = []
if abs(src_fps - 30000 / 1001) < 0.01: VF = ["decimate=cycle=4"]; cfps = src_fps * 3 / 4   # 13강 클립 = 22.5 내용 + 4프레임마다 중복
else: cfps = src_fps
if MODE == "flow":
    VF.append(f"minterpolate=fps={cfps * 4:.4f}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"); cfps *= 4
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", clip_mp4, *(["-vf", ",".join(VF)] if VF else []), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=FS)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}", "-r", "30000/1001", "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", out_mp4], stdin=subprocess.PIPE)
cur = -1; fa = fb = None; nout = int(round(Dout * FPS_OUT)); used = []
def nxt():
    b = dec.stdout.read(FS)
    return np.frombuffer(b, np.uint8).reshape(H_, W_, 3) if len(b) == FS else None
for k in range(nout):
    pos = c_of_u(k / FPS_OUT) * cfps
    if MODE == "flow": pos = round(pos)
    want = int(pos + 1e-6); fr = pos - want
    while cur < want + 1:
        f = nxt()
        if f is None: break
        fa, fb = fb, f; cur += 1
    A_, B_ = (fa, fb) if cur == want + 1 and fa is not None else (fb, fb)
    out = A_ if fr < 0.02 or B_ is A_ else (A_.astype(np.float32) * (1 - fr) + B_.astype(np.float32) * fr + 0.5).astype(np.uint8)
    used.append(round(pos, 2)); enc.stdin.write(out.tobytes())
enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.kill()
info = dict(mode=MODE, sigma=SIGMA, tol=TOL, smin=SMIN, smax=SMAX, clip=clip_mp4, src_fps=round(src_fps, 4), used_fps=round(cfps, 4), target=tgt_wav,
            clip_speech=[round(cs, 3), round(ce, 3)], target_speech=[round(ts, 3), round(te, 3)], out_dur=round(Dout, 3), out_frames=nout,
            target_at_out=round(cs - ts, 4), speed_min=round(float(sp.min()), 2), speed_max=round(float(sp.max()), 2),
            speed_jerk_max=round(float(np.abs(np.diff(sp)).max() * 100), 2), n_onsets=len(on_t), n_fix=len(pts),
            onset_dev_vs_dtw_max=round(float(np.abs(dev).max()), 3), onset_dev_median=round(float(np.median(np.abs(dev))), 3),
            map=[[round(float(a), 3), round(float(b), 3)] for a, b in zip(tau, cl)])
json.dump(info, open(out_json, "w"), ensure_ascii=False, indent=1)
print({k: v for k, v in info.items() if k != "map"})
