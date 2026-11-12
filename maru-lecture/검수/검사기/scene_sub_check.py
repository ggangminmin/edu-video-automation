# 장면·자막 동기 검사기 (오더 06 f) — 마루시공 11~20강
# 실행: ~/.venvs/tts/bin/python scene_sub_check.py --video X.mp4 --timeline 타임라인.json --voice v090.wav [--out 결과.json] [--sheet 경계.jpg]
#  ⓪ 음성 배치 검증: 타임라인 audio 표대로 깐 깨끗한 음성 ↔ 영상 소리 상호상관(조각마다 어긋남 ms)
#  ① 장면 경계: 영상에서 슬라이드 컷 프레임을 직접 찾고(왼쪽 슬라이드 영역 차분), 컷 프레임·직전 프레임의 자막이 어느 장면 대본인지
#     (자막 = 영상 자막바에서 바뀜 프레임을 직접 찾아 순서대로 대본 줄에 대응) → 옛 자막이 새 장면에 남은 프레임 수 / 새 자막이 늦은 프레임 수
#  ② 자막 시작 − 말 시작: 자막 시작 = 영상에서 잰 바뀜 프레임. 말 시작 = 깨끗한 음성에서 후보(30ms↑ 쉼 끝 · −45dB 아래 깊은 골짜기 끝 → 없으면 얕은 골짜기 = 보류)를 고르고
#     짧은 구간 받아쓰기(mlx whisper)로 「그 줄 첫 말로 시작 + 앞 1초엔 없음」 확인한 가장 이른 후보. 방법(무음경계/골짜기) 따로 집계
#  ③ 빈 바: 자막바(악센트+흰 판)는 있는데 글자 잉크가 없는 프레임
#  ④ 아나운서 등장 첫 0.5초 정지: 등장 첫 15프레임에서 인물 영역 차분<0.1 이 연속된 최대 프레임 수(25→29.97 단발 중복은 1이라 정상, 3 이상 = 정지)
# 기준: ① 남은/늦은 프레임 0 · ② 선행 0~0.16초(말보다 늦은 줄 0, 0.16 넘게 빠른 줄 0) · ③ 0 · ④ 정지 0
import argparse, json, os, re, subprocess, sys, difflib
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--video", required=True); ap.add_argument("--timeline", required=True)
ap.add_argument("--voice", required=True, help="0.9배 깨끗한 나레이션(타임라인 audio 의 src 기본값)")
ap.add_argument("--out", default=None); ap.add_argument("--sheet", default=None)
ap.add_argument("--skip-asr", action="store_true")
ap.add_argument("--anc-x", default="", help="아나운서별 움직임 검사 창 왼쪽 x, 예: 인삿말:610,끝인사:1130 (기본 1130 · #9 표지 아나운서 옮김)")
A = ap.parse_args()
FPS = 30000 / 1001
TLD = os.path.dirname(os.path.abspath(A.timeline))
tl = json.load(open(A.timeline))
subs = tl["subs"]; slides = tl["slides"]
END0 = tl["ending"]["zoom_blur"][0]

# ---------------- 프레임 스캔 (한 번 디코드: 자막바 / 왼쪽 슬라이드 / 아나운서 영역)
BW, BH, SW, SH, AW, AH = 872, 52, 250, 220, 210, 420
H_ = BH + SH + AH
vf = ("format=gray,split=3[a][b][c];"
      "[a]crop=1745:103:89:908,scale=872:52[A];"
      "[b]crop=1000:880:0:0,scale=250:220,pad=872:220[B];"
      "[c]crop=420:840:1130:60,scale=210:420,pad=872:420[C];[A][B][C]vstack=3")
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", A.video, "-an", "-filter_complex", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                     stdout=subprocess.PIPE, bufsize=10**8)
FS = BW * H_
bar_on, ink, dbar, dsl, dan = [], [], [], [], []
prev = None
while True:
    buf = p.stdout.read(FS)
    if len(buf) < FS: break
    f = np.frombuffer(buf, np.uint8).reshape(H_, BW)
    bar = f[:BH]; sl = f[BH:BH + SH, :SW].astype(np.int16); an = f[BH + SH:, :AW].astype(np.int16)
    acc = bar[8:44, 1:11].mean(); plate = bar[1:8, 20:860].mean()
    on = acc < 100 and plate > 215
    txt = bar[12:42, 16:866]
    bar_on.append(on); ink.append(int((txt < 130).sum()) if on else 0)
    t16 = txt.astype(np.int16)
    if prev is not None:
        dbar.append(float(np.abs(t16 - prev[0]).mean())); dsl.append(float(np.abs(sl - prev[1]).mean())); dan.append(float(np.abs(an - prev[2]).mean()))
    else:
        dbar.append(0.0); dsl.append(0.0); dan.append(0.0)
    prev = (t16, sl, an)
p.wait()
N = len(bar_on); bar_on = np.array(bar_on); ink = np.array(ink); dbar = np.array(dbar); dsl = np.array(dsl); dan = np.array(dan)
def ft(i): return i / FPS
print(f"프레임 {N}", file=sys.stderr)

# ---------------- 자막 구간(영상 실측)
lim = int(END0 * FPS) - 1
BLANK_INK = 40
chg = [i for i in range(1, N) if bar_on[i] and (not bar_on[i - 1] or dbar[i] > 1.5)]
segs = []          # [f0, f1) 글자 있는 자막 구간
i = 0
while i < N:
    if bar_on[i] and ink[i] > BLANK_INK:
        j = i + 1
        while j < N and bar_on[j] and ink[j] > BLANK_INK and dbar[j] <= 1.5: j += 1
        segs.append([i, j]); i = j
    else: i += 1
blank = [i for i in range(N) if bar_on[i] and ink[i] <= BLANK_INK]
blank_runs = []
for i in blank:
    if blank_runs and blank_runs[-1][1] == i: blank_runs[-1][1] = i + 1
    else: blank_runs.append([i, i + 1])
# 같은 자막이 잡음으로 두 구간으로 쪼개진 경우 합치기: 대본 줄 수와 다르면 경고
seg_line = [None] * len(segs)
map_ok = len(segs) == len(subs)
if map_ok:
    seg_line = list(range(len(subs)))
else:   # 실측 구간 수가 다르면 시간 겹침이 가장 큰 줄로 대응(경고)
    for k, (a, b) in enumerate(segs):
        best = max(range(len(subs)), key=lambda n: min(ft(b), subs[n]["end"]) - max(ft(a), subs[n]["start"]))
        seg_line[k] = best
frame_seg = np.full(N, -1)
for k, (a, b) in enumerate(segs): frame_seg[a:b] = k
def line_at(fr):
    k = frame_seg[fr] if 0 <= fr < N else -1
    return None if k < 0 else seg_line[k]

# ---------------- ① 장면 경계(영상 실측 컷)
cuts = [i for i in range(1, min(N, lim)) if dsl[i] > 4.0]
cuts2 = []
for c in cuts:
    if cuts2 and c - cuts2[-1] <= 2: continue
    cuts2.append(c)
exp = [s for s in slides if s["start"] > 0.05]
bound = []
for c in cuts2:
    t = ft(c)
    s = min(exp, key=lambda s: abs(s["start"] - t))
    if abs(s["start"] - t) > 0.1: bound.append(dict(frame=c, t=round(t, 3), slide=None, note="타임라인에 없는 컷")); continue
    new = s["slide"]; old = slides[slides.index(s) - 1]["slide"]
    # 새 장면 쪽으로: 컷부터 자막이 새 장면 대본이 될 때까지 프레임 수(옛 자막 남음 / 빈칸·바 없음)
    stale = 0; f = c
    while f < N and f < c + 120:
        ln = line_at(f)
        if ln is not None and subs[ln]["slide"] == new: break
        stale += 1; f += 1
    # 앞 장면 쪽으로: 컷 전에 새 장면 자막이 먼저 뜬 프레임 수
    early = 0; f = c - 1
    while f >= 0 and f > c - 120:
        ln = line_at(f)
        if ln is not None and subs[ln]["slide"] == new: early += 1; f -= 1
        else: break
    lb, la = line_at(c - 1), line_at(c)
    bound.append(dict(frame=c, t=round(t, 3), slide=new, prev_slide=old,
                      before=(subs[lb]["n"], subs[lb]["slide"]) if lb is not None else None,
                      after=(subs[la]["n"], subs[la]["slide"]) if la is not None else None,
                      stale_frames=stale, early_frames=early))
missing = [s["slide"] for s in exp if not any(b.get("slide") == s["slide"] for b in bound)]

# ---------------- ③ 빈 바
blank_list = [dict(t0=round(ft(a), 3), t1=round(ft(b), 3), frames=b - a) for a, b in blank_runs if a < lim]

# ---------------- ④ 아나운서 첫 0.5초 정지
anchors = tl.get("anchors")
if not anchors:   # v2 방식: 2번(오프닝)·27번(클로징) 시작
    anchors = [dict(name="오프닝", **{"in": next(s for s in slides if s["slide"] == 2)["start"]}),
               dict(name="클로징", **{"in": next(s for s in slides if s["slide"] == 27)["start"]})]
noise = float(np.median(dsl[dsl > 0])) if (dsl > 0).any() else 0.2
anc = []
for a0 in anchors:
    f0 = int(round(a0["in"] * FPS))
    d = dan[f0 + 1:f0 + 16]
    AX = dict(p.split(":") for p in A.anc_x.split(",") if p)
    if a0["name"] in AX:   # 다른 자리 아나운서: 그 창만 따로 디코드
        x0 = int(AX[a0["name"]]); fr_ = []
        q_ = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0, f0 - 1) / FPS:.4f}", "-i", A.video, "-frames:v", "17", "-vf", f"format=gray,crop=420:840:{x0}:60,scale=210:420",
                             "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
        fr_ = np.frombuffer(q_, np.uint8).reshape(-1, 420, 210).astype(np.int16)
        d = np.abs(np.diff(fr_, axis=0)).mean((1, 2))[1:16]
    # 하이젠 25fps→29.97 변환 중복 프레임(단발)은 정상 → 차분 0.1 미만이 연속된 가장 긴 줄 길이
    still = 0; r = 0
    for v in d:
        r = r + 1 if v < 0.1 else 0; still = max(still, r)
    ref = float(np.median(dan[f0 + 30:f0 + 150])) if f0 + 150 < N else None
    anc.append(dict(name=a0["name"], t=round(ft(f0), 3), still_frames_first15=still, still_run_first15=still,
                    first15_mean_diff=round(float(d.mean()), 3), later_median_diff=round(ref, 3) if ref else None))

# ---------------- ⓪·② 음성
SR = 16000
def load(path):
    x = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(x, np.int16).astype(np.float32) / 32768
vid_a = load(A.video)
srcs = {}
voice = np.zeros(len(vid_a) + SR, np.float32)
for e in tl["audio"]:
    sp = e.get("src"); sp = os.path.join(TLD, sp) if sp else A.voice
    if sp not in srcs: srcs[sp] = load(sp)
    seg = srcs[sp][int(e["src_from"] * SR):int(e["src_to"] * SR)]
    o = int(round(e["out"] * SR)); voice[o:o + len(seg)] += seg * e.get("gain", 1.0)
voice = voice[:len(vid_a)]
amap = []
for e in tl["audio"]:
    a = int(e["out"] * SR); b = int((e["out"] + min(8, e["src_to"] - e["src_from"])) * SR)
    L = int(0.2 * SR); r = voice[a:b]; v = vid_a[max(0, a - L):b + L]
    if len(r) < SR // 2 or len(v) < len(r) + 2 * L: continue
    cc = np.correlate(v, r, "valid"); lag = (int(np.argmax(cc)) - L) / SR
    amap.append(dict(out=e["out"], slide=e.get("slide"), lag_ms=round(lag * 1000, 1)))
Hh = 0.005; hop = int(SR * Hh)
fr = voice[:len(voice) // hop * hop].reshape(-1, hop)
DB = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-6)
sil = DB < -40
sil_ends = []   # 0.05초 이상 무음의 끝
run = 0
for i, s in enumerate(sil):
    if s: run += 1
    else:
        if run >= 6: sil_ends.append(i * Hh)          # 30ms 이상 쉼(40ms 쉼 — v2 13번)
        run = 0
sil_ends = np.array(sil_ends)
def rises(a, b, deep=False):
    a0, b0 = int(a / Hh), int(b / Hh); seg = DB[a0:b0]; out = []
    for i in range(2, len(seg) - 2):
        if seg[i] == seg[i - 2:i + 3].min() and seg[i] < seg[max(0, i - 20):i + 20].max() - 6:
            k = i
            while k < len(seg) - 1 and seg[k] < seg[i] + 6: k += 1
            if DB[a0 + k:a0 + k + 6].max() > -35 and (not deep or seg[i] < -45): out.append((a0 + k) * Hh)   # 무음 안 잡음 상승(−120→−64) 제외: 뒤 30ms 가 실제 말소리일 때만
    return out

NUMK = {"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "6": "육", "7": "칠", "8": "팔", "9": "구", "0": "영"}
def nrm(s):
    s = re.sub(r"\d", lambda m: NUMK[m.group()], s)
    return re.sub(r"[^가-힣]", "", s)
cache = {}
_mw = None
def tr(a, b):
    global _mw
    key = (round(a, 2), round(b, 2))
    if key in cache: return cache[key]
    if _mw is None:
        import mlx_whisper; _mw = mlx_whisper
    seg = voice[int(max(0, a) * SR):int(b * SR)]
    if np.abs(seg).max() < 0.003: cache[key] = ""; return ""
    r = _mw.transcribe(seg, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    cache[key] = nrm(r["text"]); return cache[key]
def starts(after, head): return after[:2] == head[:2]          # 첫 두 글자 엄격(느슨하게 하면 앞 줄 끝 음절 「징미끄」도 「미끄럼」으로 통과 — v2 45번에서 확인)
def ends_with(before, head): return any(difflib.SequenceMatcher(None, before[-len(head) - k:][:len(head)], head).ratio() >= 0.75 for k in range(0, 3))

sync = []
if not A.skip_asr:
    seg_start = {seg_line[k]: segs[k][0] for k in range(len(segs))}
    for n, s in enumerate(subs):
        if n not in seg_start: sync.append(dict(n=s["n"], result="자막없음")); continue
        ts = ft(seg_start[n])
        head = nrm(s["text"])[:3]
        se = [float(t) for t in sil_ends if ts - 0.6 <= t <= ts + 1.6 and DB[int(t / Hh):int(t / Hh) + 8].max() > -35]
        gap = sorted(set([round(t, 3) for t in se] + [round(t, 3) for t in rises(ts - 0.6, ts + 1.6, deep=True)]))   # 쉼 끝 · −45dB 아래 깊은 골짜기 끝
        weak = sorted(set(round(t, 3) for t in rises(ts - 0.45, ts + 1.2)) - set(gap))                                  # 얕은 골짜기(판정 보류용)
        how = None; onset = None
        for group, label in ((gap, "쉼경계"), (weak, "얕은골짜기")):
            for c in group:
                if c - 0.12 < 0: continue
                if starts(tr(c, c + 1.3), head) and not ends_with(tr(c - 1.0, c), head):   # 앞 구간은 뒤가 맞을 때만 받아씀
                    onset = c; how = label; break
            if onset is not None: break
        if onset is None:
            sync.append(dict(n=s["n"], slide=s["slide"], text=s["text"], sub_t=round(ts, 3), result="판정불가")); continue
        lead = onset - ts
        res = "OK" if -0.017 <= lead <= 0.16 + 0.017 else ("늦음" if lead < 0 else "너무빠름")
        if res == "늦음" and not any(h in tr(ts - 0.6, ts)[-4:] for h in (head[:2], head[:1] * 2)) and starts(tr(ts, ts + 1.3), head):
            res = "OK"; how += "+앞말없음확인"      # v3 오탐 보정: 쉼 안 후보를 잡아 「늦음」으로 나와도 자막 직전 0.6초에 그 줄 첫 말이 없고 자막 시작 뒤 1.3초가 첫 말로 시작하면 늦지 않음
        if how == "얕은골짜기" and res != "OK": res = "보류"          # 얕은 골짜기는 받아쓰기가 앞 줄 끝 음절을 버려 일찍 잡힐 수 있음 → 사람 확인
        sync.append(dict(n=s["n"], slide=s["slide"], text=s["text"], sub_t=round(ts, 3), voice_t=round(onset, 3),
                         lead=round(lead, 3), how=how, result=res))
        print(s["n"], res, round(lead, 3), how, s["text"][:16], file=sys.stderr, flush=True)

# ---------------- 집계
leads = np.array([x["lead"] for x in sync if "lead" in x])
def dist(arr):
    if not len(arr): return None
    return dict(n=int(len(arr)), median=round(float(np.median(arr)), 3), p10=round(float(np.percentile(arr, 10)), 3),
                p90=round(float(np.percentile(arr, 90)), 3), min=round(float(arr.min()), 3), max=round(float(arr.max()), 3))
summary = dict(
    video=A.video, frames=N, segments=len(segs), lines=len(subs), segment_line_map="순서대응" if map_ok else "시간겹침대응(구간 수 다름!)",
    audio_map_max_lag_ms=max((abs(x["lag_ms"]) for x in amap), default=None),
    cuts_found=len([b for b in bound if b.get("slide")]), cuts_expected=len(exp), cuts_missing=missing,
    cuts_unexpected=[b["t"] for b in bound if not b.get("slide")],
    boundary_stale=sum(1 for b in bound if b.get("stale_frames", 0) > 0), boundary_stale_frames=sum(b.get("stale_frames", 0) for b in bound),
    boundary_early=sum(1 for b in bound if b.get("early_frames", 0) > 0),
    blank_bar_frames=sum(x["frames"] for x in blank_list),
    sync_all=dist(leads), sync_gap=dist(np.array([x["lead"] for x in sync if x.get("how") == "쉼경계"])),
    sync_weak=dist(np.array([x["lead"] for x in sync if x.get("how") == "얕은골짜기"])), sync_hold=[x["n"] for x in sync if x.get("result") == "보류"],
    sync_late=[x["n"] for x in sync if x.get("result") == "늦음"], sync_too_early=[x["n"] for x in sync if x.get("result") == "너무빠름"],
    sync_unknown=[x["n"] for x in sync if x.get("result") in ("판정불가", "자막없음")],
    anchor_still=[(a["name"], a["still_frames_first15"]) for a in anc])
fail = (summary["boundary_stale"] or summary["boundary_early"] or summary["blank_bar_frames"] or summary["cuts_missing"]
        or summary["sync_late"] or summary["sync_too_early"] or any(a["still_run_first15"] >= 3 for a in anc) or not map_ok)
summary["verdict"] = "걸림" if fail else "통과"
out = dict(summary=summary, boundaries=bound, blank=blank_list, anchors=anc, audio_map=amap, sync=sync)
if A.out: json.dump(out, open(A.out, "w"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))
print("경계별: t | 장면 | 컷 직전 자막(줄,장면) | 컷 프레임 자막 | 옛자막 남은 프레임 | 먼저 뜬 프레임")
for b in bound: print(b.get("t"), b.get("slide"), b.get("before"), b.get("after"), b.get("stale_frames"), b.get("early_frames"), b.get("note", ""))

# ---------------- 경계 컨택트시트(컷 직전 / 컷 프레임)
if A.sheet:
    from PIL import Image, ImageDraw, ImageFont
    bs = [b for b in bound if b.get("slide")]
    sel = sorted(set([b["frame"] - 1 for b in bs] + [b["frame"] for b in bs]))
    expr = "+".join(f"eq(n\\,{f})" for f in sel)
    tmp = os.path.splitext(A.sheet)[0] + "_frames"; os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", A.video, "-vf", f"select='{expr}',scale=480:270", "-fps_mode", "passthrough", f"{tmp}/%04d.png"], check=True)
    ims = {f: Image.open(f"{tmp}/{k + 1:04d}.png") for k, f in enumerate(sel)}
    F = ImageFont.truetype("/System/Library/Fonts/AppleSDGothicNeo.ttc", 16)
    W = 2 * 480 + 30; Hh2 = 270 + 26
    sheet = Image.new("RGB", (W * 2, Hh2 * ((len(bs) + 1) // 2)), (240, 240, 240)); d = ImageDraw.Draw(sheet)
    for k, b in enumerate(bs):
        x0 = (k % 2) * W; y0 = (k // 2) * Hh2
        sheet.paste(ims[b["frame"] - 1], (x0 + 5, y0 + 24)); sheet.paste(ims[b["frame"]], (x0 + 490, y0 + 24))
        ok = b["stale_frames"] == 0 and b["early_frames"] == 0
        d.text((x0 + 6, y0 + 3), f"{b['t']:.3f}s  {b['prev_slide']}→{b['slide']}  직전 자막{b['before']}  컷 자막{b['after']}  남음{b['stale_frames']}f {'OK' if ok else '❌'}",
               font=F, fill=(0, 120, 0) if ok else (200, 0, 0))
    sheet.save(A.sheet, quality=85)
    print("시트", A.sheet)
