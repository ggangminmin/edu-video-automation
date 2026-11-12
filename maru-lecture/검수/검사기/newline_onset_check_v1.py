# 줄 나눔 새 줄 시작 검사기 (11/3 팀장 · 18강 p1V 발견 「mlxwords −0.09 가 실소리 대비 −0.06~+0.25 틀림」 · 11강 p1T 만듦)
#  앞 납품 타임라인과 시작 시각이 바뀐 자막 줄마다: 깨끗한 음성(타임라인 audio 대로 v090·인삿말·끝인사를 깐 것, BGM 없음)에서 실소리 시작을 재고
#  자막 선행 = 실소리 시작 − 자막 시작. 기준 0 ≤ 선행 ≤ 0.177(말보다 늦으면 걸림 · 0.177 넘게 이르면 걸림). 규칙 「자막 = 말 0.09초 앞」.
#  실소리 시작(18강 변경표_v4 U1 방식): 5ms RMS · 기준점(voice_on 또는 시작+0.09) ±0.3초 안 「−50dB 밑 15ms 이상」 쉼 중 끝이 기준점에 가장 가까운 것
#    → 그 쉼 뒤 −50dB 를 30ms 이상 넘는 첫 시각. 쉼이 없고 가장 깊은 골짜기가 −45dB 보다 얕으면 = 이어진 말 → 「판정불가」(따로 표).
#    −50~−45dB 골짜기만 있으면 골짜기 시각 자체(18강 29번 처리와 같음, 「골짜기」 표시).
# 실행(_작업 에서): python3 검수/검사기/newline_onset_check.py NN --timeline NN강/타임라인_vN.json --prev NN강/타임라인_vM.json [--json out.json] [--all]
#   --all = 바뀐 줄만이 아니라 모든 줄. 종료코드 0 통과 · 1 걸림(판정불가는 걸림 아님 — 사람/받아쓰기 확인 몫).
#   🆕 --asr(무거움 → heavy_run.sh asr): 고른 소리 시작으로 [시작, +1.3초] 받아쓰기가 그 줄 첫 어절로 시작 · [시작−0.9, 시작] 끝에 첫 어절 없음 = 「받아쓰기✓」 표시만.
#      (후보를 받아쓰기로 고르게 해 봤더니 whisper 가 0.6초 어긋난 구간도 문장으로 받아 적어 29번을 115.04 로 잘못 고름 → 고르기엔 안 씀)
#   「다른 후보」: 기준점 ±0.3초 안 다른 쉼 끝·−40dB 밑 골짜기 중 판정이 달라지는 것(파열음 막힘 「작업」 ㄱ 같은 단어 안 쉼 vs 얕은 단어 경계) → 걸림 줄은 사람/받아쓰기로 확인.
#   검산(18강 v4초안 vs v3c · p1V 실측 onset50 18곳): --asr 없이 16/18 같음(±5ms) · 다른 2곳 = 114.32/114.435 · 326.535/326.705(쉼 vs 얕은 골짜기)
import sys, os, json, argparse, subprocess, numpy as np
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # _작업
ap = argparse.ArgumentParser(); ap.add_argument("lec"); ap.add_argument("--timeline", required=True); ap.add_argument("--prev", required=True)
ap.add_argument("--json"); ap.add_argument("--all", action="store_true"); ap.add_argument("--quiet", action="store_true"); ap.add_argument("--asr", action="store_true")
a = ap.parse_args()
SR, H = 16000, 80                       # 5ms
LO, HI, TH, RUN, SHALLOW = 0.0, 0.177, -50.0, 6, -45.0
GAP = int(os.environ.get("GAP_MS", "15")) // 5   # 쉼 최소 길이(5ms 칸)
L = os.path.join(W, f"{a.lec}강")
def P(p): return p if os.path.isabs(p) else os.path.join(W, p)
tl = json.load(open(P(a.timeline))); prev = json.load(open(P(a.prev)))
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def srcpath(k):
    if k is None: return os.path.join(L, "work", "v090.wav")
    for c in [os.path.join(L, k), os.path.join(L, "work", k), os.path.join(W, k)]:
        if os.path.exists(c): return c
    raise SystemExit(f"소리 조각 없음: {k}")
cache = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = load(srcpath(k))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR))
    V[o:o + len(y)] += y[:max(0, len(V) - o)]
db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
FR = SR / H   # 200/s

def cands(ref):
    """[(소리 시작 후보, 종류, dB)] 기준점에 가까운 순 — 쉼 끝(−50 밑 ≥15ms 뒤 −50 을 30ms 넘는 첫 시각) · 골짜기(−40 밑 지역 최소, 쉼 밖)"""
    i0, i1 = max(0, int((ref - 0.3) * FR)), min(len(db) - RUN, int((ref + 0.3) * FR)); out = []; inrun = np.zeros(i1 - i0, bool)
    j = i0
    while j < i1:
        if db[j] < TH:
            k = j
            while k < i1 and db[k] < TH: k += 1
            if k - j >= GAP:
                m = k
                while m < len(db) - RUN and not all(db[m:m + RUN] > TH): m += 1
                out.append((m / FR, "쉼", round(float(db[j:k].min()), 1))); inrun[j - i0:k - i0] = True
            j = k
        else: j += 1
    for m in range(i0 + 3, i1 - 3):
        if not inrun[m - i0] and db[m] < -40 and db[m] == db[m - 3:m + 4].min(): out.append((m / FR, "골짜기", round(float(db[m]), 1)))
    return sorted(out, key=lambda c: abs(c[0] - ref))
_mlx = None
def asr(t0, t1):
    global _mlx
    if _mlx is None:
        import mlx_whisper as _m; _mlx = _m
    y = V[max(0, int(t0 * SR)):int(t1 * SR)]
    return _mlx.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip() if len(y) > SR * 0.2 else ""
import re as _re
def kn(t): return _re.sub(r"[^가-힣0-9A-Za-z]", "", t)
def asr_ok(on, text):
    w0 = kn(text.split()[0])[:2]
    aft, bef = kn(asr(on - 0.03, on + 1.3)), kn(asr(on - 0.9, on - 0.03))
    return aft.startswith(w0) and w0 not in bef[-4:], aft[:8], bef[-6:]

def onset(ref):
    i0, i1 = max(0, int((ref - 0.3) * FR)), min(len(db) - RUN, int((ref + 0.3) * FR))
    seg = db[i0:i1]; runs = []; j = 0
    while j < len(seg):
        if seg[j] < TH:
            k = j
            while k < len(seg) and seg[k] < TH: k += 1
            if k - j >= GAP: runs.append((i0 + j, i0 + k))   # [시작, 끝) 프레임
            j = k
        else: j += 1
    if runs:
        s_, e_ = min(runs, key=lambda r: abs(r[1] / FR - ref))
        m = e_
        while m < len(db) - RUN and not all(db[m:m + RUN] > TH): m += 1
        return m / FR, "쉼", round(float(db[s_:e_].min()), 1)
    m = i0 + int(np.argmin(seg)); vdb = float(db[m])
    if vdb > SHALLOW: return None, "이어진 말", round(vdb, 1)
    return m / FR, "골짜기", round(vdb, 1)

old = [round(s["start"], 3) for s in prev["subs"]]
def changed(st): return all(abs(st - o) > 0.002 for o in old)
rows = []
for s in tl["subs"]:
    if not a.all and not changed(s["start"]): continue
    ref = s.get("voice_on") or s["start"] + 0.09
    on, how, vdb = onset(ref); aft = bef = ""; aok = None
    if a.asr and on is not None: aok, aft, bef = asr_ok(on, s["text"])
    r = dict(n=s["n"], slide=s.get("slide"), t=round(s["start"], 3), mmss=f"{int(s['start'] // 60)}:{s['start'] % 60:05.2f}", text=s["text"],
             ref=round(ref, 3), onset=None if on is None else round(on, 3), how=how, gap_db=vdb, asr_ok=aok, asr_after=aft, asr_before=bef)
    if on is None: r["lead"] = None; r["result"] = "판정불가"
    else:
        ld = on - s["start"]; r["lead"] = round(ld, 3)
        r["result"] = "OK" if LO - 1e-6 <= ld <= HI + 1e-6 else ("늦음" if ld < LO else "너무빠름")
    def verdict(t): ld_ = t - s["start"]; return "OK" if LO - 1e-6 <= ld_ <= HI + 1e-6 else ("늦음" if ld_ < LO else "너무빠름")
    r["alt"] = [dict(onset=round(c[0], 3), how=c[1], db=c[2], result=verdict(c[0])) for c in cands(ref)
                if (on is None or abs(c[0] - on) > 0.02) and verdict(c[0]) != r["result"]][:2]
    rows.append(r)
bad = [r for r in rows if r["result"] in ("늦음", "너무빠름")]; unk = [r for r in rows if r["result"] == "판정불가"]
print(f"{a.lec}강 {os.path.basename(a.timeline)} vs {os.path.basename(a.prev)} — 바뀐 줄 {len(rows)} · 걸림 {len(bad)}(늦음 {sum(r['result']=='늦음' for r in bad)} · 너무빠름 {sum(r['result']=='너무빠름' for r in bad)}) · 판정불가 {len(unk)} · 기준 선행 {LO}~{HI}초")
for r in rows:
    if a.quiet and r["result"] == "OK": continue
    print(f"  {'✗' if r in bad else ('?' if r in unk else '✓')} {r['n']:>3} {r['mmss']} 자막 {r['t']} 소리 {r['onset']} 선행 {r['lead']} [{r['how']} {r['gap_db']}dB] {r['result']}{'' if r['asr_ok'] is None else (' 받아쓰기✓' if r['asr_ok'] else ' 받아쓰기✗')} 「{r['text'][:22]}」"
          + ("" if not r["alt"] or r["result"] == "OK" else "  · 다른 후보 " + ", ".join(f"{c['onset']}({c['how']} {c['db']}dB → {c['result']})" for c in r["alt"])))
if a.json: json.dump(dict(rows=rows, bad=len(bad), unknown=len(unk)), open(a.json, "w"), ensure_ascii=False, indent=1)
sys.exit(1 if bad else 0)
