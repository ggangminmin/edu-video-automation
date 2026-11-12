# 지적 #8 — 팀장 하이젠 클립(인삿말·끝인사)의 생성 소리를 버리고, 타입캐스트 0.9배 소리에 영상을 맞춘다.
#  클립 자체 소리(입 모양을 만든 소리)와 타입캐스트 소리를 MFCC DTW 로 정렬 → 타입캐스트 시각 τ 마다 보여줄 클립 시각 c(τ)
#  → 클립 프레임을 c(u) 순서로 다시 뽑아 29.97fps 영상(그린 그대로)으로 굽는다. 소리는 넣지 않음(render 가 타입캐스트를 깜).
#  앞 idle(클립 0~cs)은 그대로, 말 구간만 늘이고 줄임, 끝 자세(클립 ce~끝)는 그대로.
# 실행: python3 warp_clip.py <clip.mp4> <clip.wav> <target.wav> <out.mp4> <out.json>
import sys, json, subprocess, numpy as np, librosa
clip_mp4, clip_wav, tgt_wav, out_mp4, out_json = sys.argv[1:6]
SR, HOP = 16000, 160                     # 10ms
FPS_OUT = 30000 / 1001
def load(p): return librosa.load(p, sr=SR, mono=True)[0]
def span(y, db=-40):                     # 말 시작·끝(−40dB, 10ms 창)
    fr = librosa.util.frame(np.pad(y, (0, HOP)), frame_length=HOP, hop_length=HOP)
    d = 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7); on = np.where(d > db)[0]
    return on[0] * HOP / SR, (on[-1] + 1) * HOP / SR
yc, yt = load(clip_wav), load(tgt_wav)
cs, ce = span(yc); ts, te = span(yt)
def feat(y, a, b):
    s = y[int(a * SR):int(b * SR)]
    m = librosa.feature.mfcc(y=s, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=512)[1:]
    m = (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
    e = librosa.feature.rms(y=s, hop_length=HOP, frame_length=512)[0]
    e = 20 * np.log10(e + 1e-6); e = (e - e.mean()) / (e.std() + 1e-6)
    return np.vstack([m, 3 * e])         # 쉼(소리 크기)도 맞추게 에너지 가중
Fc, Ft = feat(yc, cs, ce), feat(yt, ts, te)
D, wp = librosa.sequence.dtw(X=Ft, Y=Fc, metric="euclidean", step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0], [1, 2], [2, 1]]),
                             weights_add=np.array([0, 1, 1, 1, 1]))
wp = wp[::-1]
nt = Ft.shape[1]
cmap = np.zeros(nt)
for i in range(nt):
    cmap[i] = wp[wp[:, 0] == i, 1].mean() if (wp[:, 0] == i).any() else np.nan
cmap = np.interp(np.arange(nt), np.where(~np.isnan(cmap))[0], cmap[~np.isnan(cmap)])
# 부드럽게: 0.15초 이동평균 → 단조 · 기울기 0.4~2.5 로 자름(입이 튀지 않게)
k = 15; sm = np.convolve(np.pad(cmap, (k, k), mode="edge"), np.ones(k) / k, "same")[k:-k]
sm[0] = 0; sm[-1] = Fc.shape[1] - 1
for i in range(1, nt): sm[i] = min(max(sm[i], sm[i - 1] + 0.4), sm[i - 1] + 2.5)
sm = sm * (Fc.shape[1] - 1) / sm[-1]      # 끝을 클립 말 끝에 맞춤
tau = np.arange(nt) * HOP / SR             # 타깃 말 구간 안 시각
cl = sm * HOP / SR                         # 클립 말 구간 안 시각
# 쉼 경계 고정점(선택): "클립초:타깃초,…" (둘 다 파일 안 절대 초, silencedetect 쉼 시작·끝 짝) → DTW 지도를 그 점에 정확히 지나가게 보정
if len(sys.argv) > 6 and sys.argv[6]:
    an = [tuple(map(float, p.split(":"))) for p in sys.argv[6].split(",")]
    at = np.array([0.0] + [t - ts for c, t in an] + [tau[-1]]); ac = np.array([0.0] + [c - cs for c, t in an] + [cl[-1]])
    cur = np.interp(at, tau, cl); dl = ac - cur                   # 고정점마다 어긋남
    groups = []                                                     # 고정점 무리(서로 0.8초 안) → 무리 앞뒤 0.4초에서 보정 0, 무리 안은 선형 · 멀리 있는 DTW 정렬은 그대로
    for a_, d_ in zip(at[1:-1], dl[1:-1]):
        if groups and a_ - groups[-1][-1][0] <= 0.8: groups[-1].append((a_, d_))
        else: groups.append([(a_, d_)])
    qx, qy = [], []
    for g in groups:
        qx += [g[0][0] - 0.4] + [a_ for a_, _ in g] + [g[-1][0] + 0.4]; qy += [0.0] + [d_ for _, d_ in g] + [0.0]
    o_ = np.argsort(qx, kind="stable"); cl = cl + np.interp(tau, np.array(qx)[o_], np.array(qy)[o_], left=0, right=0)
    for i in range(1, nt): cl[i] = max(cl[i], cl[i - 1] + 0.001)
# 출력 시각 u: [0,cs) idle 그대로 → [cs, cs+(te-ts)) 말 → 끝 자세(클립 ce~끝)
clip_dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip_mp4], capture_output=True, text=True).stdout)
spk = te - ts; tail = clip_dur - ce
Dout = cs + spk + tail
def c_of_u(u):
    if u < cs: return u
    if u < cs + spk: return cs + float(np.interp(u - cs, tau, cl))
    return ce + (u - cs - spk)
# 정렬 품질: 타깃 소리 크기 포락선 vs 클립 소리 포락선을 c(u)로 옮긴 것 → 상관 · 최대상관 어긋남
def env(y):
    fr = librosa.util.frame(np.pad(y, (0, HOP)), frame_length=HOP, hop_length=HOP); return np.sqrt((fr ** 2).mean(0))
ec, et = env(yc), env(yt)
us = np.arange(0, spk, 0.01)
w = np.array([ec[min(len(ec) - 1, int(c_of_u(cs + u) * 100))] for u in us])
t = np.array([et[min(len(et) - 1, int((ts + u) * 100))] for u in us])
L = 30; xc = [np.corrcoef(w[L:-L], np.roll(t, s)[L:-L])[0, 1] for s in range(-L, L + 1)]
lag = (int(np.argmax(xc)) - L) * 10
# 영상 다시 뽑기 (클립 22.5fps → 출력 29.97, 순차 디코드 · 램 작게)
W_, H_ = 1080, 1920; FS = W_ * H_ * 3
cfps = 22.5
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", clip_mp4, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=FS)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}", "-r", "30000/1001", "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", out_mp4], stdin=subprocess.PIPE)
cur = -1; frame = None; nout = int(round(Dout * FPS_OUT)); used = []
for k in range(nout):
    want = int(c_of_u(k / FPS_OUT) * cfps + 1e-6)
    while cur < want:
        b = dec.stdout.read(FS)
        if len(b) < FS: break
        frame = b; cur += 1
    used.append(cur); enc.stdin.write(frame)
enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.kill()
slope = np.diff(cl) / np.diff(tau)
info = dict(clip=clip_mp4, target=tgt_wav, clip_speech=[round(cs, 3), round(ce, 3)], target_speech=[round(ts, 3), round(te, 3)],
            out_dur=round(Dout, 3), out_frames=nout, target_at_out=round(cs - ts, 4),
            speed_min=round(float(slope.min()), 2), speed_max=round(float(slope.max()), 2),
            env_corr=round(float(max(xc)), 3), env_corr_lag_ms=lag, raw_vs_unwarped_corr=round(float(np.corrcoef(
                np.array([ec[min(len(ec) - 1, int((cs + u) * 100))] for u in us])[L:-L], t[L:-L])[0, 1]), 3),
            map=[[round(float(a), 3), round(float(b), 3)] for a, b in zip(tau, cl)])
json.dump(info, open(out_json, "w"), ensure_ascii=False, indent=1)
print({k: v for k, v in info.items() if k != "map"})
