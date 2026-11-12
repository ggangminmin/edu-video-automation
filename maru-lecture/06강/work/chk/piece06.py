# 06강 장 경계 조각 훑기(오더21 piece_survey.py + asr_piece.py 합본 · 지금_규칙 24) — 깨끗한 음성(타임라인 audio 표대로) 기준
#  ① v090 원음에서 장 k 마지막 조각 끝·장 k+1 첫 조각 시작이 무음(−40dB) ≥0.3초 안 · 겹침 없음
#  ② 출력에서 말끝 뒤~컷 · 컷~다음 말 사이 소리 peak < −40dB
#  ③ 받아쓰기 엄격 대조: 장 k 말끝 앞 0.8초 끝 = 그 장 메모 마지막 3글자 · 장 k+1 말 시작 뒤 0.8초 첫 = 다음 장 메모 첫 2글자 (숫자 읽기는 숫자로도 허용)
# 실행(_작업): heavy_run.sh asr ~/.venvs/tts/bin/python 06강/work/chk/piece06.py 06강/타임라인_vN.json 06강/검사_vN
import json, re, subprocess, sys, os, numpy as np, mlx_whisper
tlp, O = sys.argv[1:3]; D = "06강"; SR = 48000; os.makedirs(f"{O}/piece", exist_ok=True)
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def sils(v):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.02", "-f", "null", "-"], input=v.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
def insil(S, t, tol=0.005): return next(((u, w) for u, w in S if u - tol <= t <= w + tol), None)
tl = json.load(open(tlp)); src = load(f"{D}/work/v090.wav"); S0 = sils(src)
T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
for a in tl["audio"]:
    p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
    if p not in cache: cache[p] = load(p)
    seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
    i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
SL = {s["slide"]: s for s in tl["slides"]}; L = max(SL); rows = []
body = [a for a in tl["audio"] if not a.get("src")]
NUMK = {"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "6": "육", "7": "칠", "8": "팔", "9": "구"}
def kn(t): return re.sub(r"[^가-힣0-9]", "", t)
def kk(t): return "".join(NUMK.get(c, c) for c in kn(t))           # 숫자 → 한글 읽기(「4번」→「사번」)
def txt(k): return "".join(x["text"] for x in tl["subs"] if x["slide"] == k)
def asr(a_, b_):
    seg = v[int(a_ * SR):int(b_ * SR)]; y = seg[::3].astype(np.float32)   # 48k → 16k
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
bad = 0
for k in range(1, L):
    cut = SL[k + 1]["start"]; ve = SL[k]["voice_end"]; vs = SL[k + 1]["voice_start"]
    p1 = p2 = "-"; ovl = 0
    if k >= 2:
        ak = [a for a in body if a["slide"] == k]; an = [a for a in body if a["slide"] == k + 1]
        end_src = max(a["src_to"] for a in ak); nxt_src = min(a["src_from"] for a in an) if an else None
        e1 = insil(S0, end_src); p1 = "무음 밖(말 중간)" if not e1 else ("짧은 쉼 %.2f" % (e1[1] - e1[0]) if e1[1] - e1[0] < 0.3 else "ok")
        if nxt_src is not None:
            e2 = insil(S0, nxt_src); p2 = "무음 밖(말 중간)" if not e2 else ("짧은 쉼 %.2f" % (e2[1] - e2[0]) if e2[1] - e2[0] < 0.3 else "ok")
            ovl = round(end_src - nxt_src, 3) if end_src > nxt_src + 0.005 else 0
    x = v[int((ve + 0.05) * SR):int(cut * SR)]; y = v[int(cut * SR):int((vs - 0.05) * SR)]
    pk = lambda z: round(float(20 * np.log10(np.abs(z).max() + 1e-9)), 1) if len(z) else -180
    ta, tb = asr(ve - 0.8, ve + 0.1), asr(vs - 0.1, vs + 0.8)
    want_end, want_head = kk(txt(k))[-3:], kk(txt(k + 1))[:2]
    end_ok = kk(ta).endswith(want_end); head_ok = kk(tb).startswith(want_head)
    ok = p1 in ("ok", "-") and p2 in ("ok", "-") and ovl == 0 and pk(x) < -40 and pk(y) < -40 and end_ok and head_ok
    bad += not ok
    rows.append(dict(k=k, cut=round(cut, 3), 조각끝=p1, 다음조각시작=p2, 겹침=ovl, 말끝뒤_컷전_peak=pk(x), 컷뒤_말시작전_peak=pk(y),
                     끝_받아쓰기=ta, 끝_기대=want_end, 끝_ok=end_ok, 첫_받아쓰기=tb, 첫_기대=want_head, 첫_ok=head_ok, ok=ok))
    print(("✓" if ok else "✗"), f"{k}→{k+1} 컷 {cut:.3f} | 끝「{ta[-12:]}」기대 …{want_end} {'✓' if end_ok else '✗'} | 첫「{tb[:10]}」기대 {want_head}… {'✓' if head_ok else '✗'} | 조각 {p1}/{p2} 겹침 {ovl} | peak {pk(x)}/{pk(y)}", flush=True)
json.dump(rows, open(f"{O}/장경계_조각훑기.json", "w"), ensure_ascii=False, indent=1)
print("장 경계", len(rows), "· 걸림", bad); sys.exit(1 if bad else 0)
