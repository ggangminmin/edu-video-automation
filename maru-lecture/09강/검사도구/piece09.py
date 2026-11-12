# 09강 장 경계 조각 훑기(오더44 · 오더21 piece_survey.py + asr_piece.py 합본, 강·판 이름만 + 표지→2 · 24→25 포함)
#  ① v090 원음에서 장 k 마지막 조각 끝·장 k+1 첫 조각 시작이 무음(−40dB)이고 그 무음 ≥0.3초 · 겹침 0
#  ② 깨끗한 음성에서 말끝 뒤~컷 · 컷~다음 말 시작 사이 소리 없음(peak < −40dB)
#  ③ 받아쓰기(엄격): 장 k 말끝 앞 0.8초 조각 끝 = 장 k 마지막 줄 끝 3글자 · 장 k+1 말 시작 뒤 0.8초 조각 첫 2글자 = 장 k+1 첫 줄 첫 2글자 (숫자→한글 읽기 맞춤)
# 실행(_작업): heavy_run.sh asr ~/.venvs/tts/bin/python 09강/검사도구/piece09.py v2
import json, re, subprocess, sys, os, numpy as np, mlx_whisper
VER = sys.argv[1]; D = "09강"; SR = 48000; O = f"{D}/검사_{VER}"; os.makedirs(O, exist_ok=True)
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def sils(v):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.02", "-f", "null", "-"], input=v.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
def insil(S, t, tol=0.005): return next(((u, w) for u, w in S if u - tol <= t <= w + tol), None)
tl = json.load(open(f"{D}/타임라인_{VER}.json")); src = load(f"{D}/work/v090.wav"); S0 = sils(src)
T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
for a in tl["audio"]:
    p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
    if p not in cache: cache[p] = load(p)
    seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
    i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
SL = {s["slide"]: s for s in tl["slides"]}; L = max(SL); body = [a for a in tl["audio"] if not a.get("src")]
NUM = {"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "7": "칠", "9": "구", "10": "십"}
def kn(t):
    t = re.sub(r"(\d)\s*mm", r"\1밀리미터", t); t = re.sub(r"(\d)\s*m\b", r"\1미터", t)   # 받아쓰기 단위 표기 → 메모 읽기(17→18 「10mm 이하」)
    return re.sub(r"[^가-힣A-Za-z]", "", re.sub(r"\d+", lambda m: NUM.get(m.group(), m.group()), t))
def asr(a_, b_):
    seg = v[int(a_ * SR):int(b_ * SR)]; y = np.interp(np.arange(0, len(seg), 3), np.arange(len(seg)), seg).astype(np.float32)
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
pk = lambda z: round(float(20 * np.log10(np.abs(z).max() + 1e-9)), 1) if len(z) else -180
rows = []
for k in range(1, L):
    subs_k = [x for x in tl["subs"] if x["slide"] == k]; subs_n = [x for x in tl["subs"] if x["slide"] == k + 1]
    cut = SL[k + 1]["start"]; ve = SL[k]["voice_end"]; vs = SL[k + 1]["voice_start"]
    p1 = p2 = "-"; ovl = 0
    if 2 <= k:
        ak = [a for a in body if a["slide"] == k]; an = [a for a in body if a["slide"] == k + 1]
        end_src = max(a["src_to"] for a in ak); nxt_src = min(a["src_from"] for a in an) if an else None
        e1 = insil(S0, end_src); e2 = insil(S0, nxt_src) if nxt_src is not None else None
        p1 = "무음 밖(말 중간)" if not e1 else ("짧은 쉼 %.2f" % (e1[1] - e1[0]) if e1[1] - e1[0] < 0.3 else "ok")
        p2 = "-(끝인사 소리)" if nxt_src is None else ("무음 밖(말 중간)" if not e2 else ("짧은 쉼 %.2f" % (e2[1] - e2[0]) if e2[1] - e2[0] < 0.3 else "ok"))
        ovl = round(end_src - nxt_src, 3) if nxt_src is not None and end_src > nxt_src + 0.005 else 0
    x = v[int((ve + 0.05) * SR):int(cut * SR)]; y = v[int(cut * SR):int((vs - 0.05) * SR)]
    sb, sa = pk(x), pk(y)
    ta, tb = asr(ve - 0.8, ve + 0.1), asr(vs - 0.1, vs + 0.8)
    want_end = kn(subs_k[-1]["text"])[-3:]; want_start = kn(subs_n[0]["text"])[:2]
    ea, eb = kn(ta), kn(tb)
    asr_ok = ea.endswith(want_end) and eb.startswith(want_start)
    ok = p1 in ("ok", "-") and p2 in ("ok", "-", "-(끝인사 소리)") and ovl == 0 and sb < -40 and sa < -40
    rows.append(dict(k=k, cut=round(cut, 3), 조각끝=p1, 다음조각시작=p2, 겹침=ovl, 말끝뒤_컷전_peak=sb, 컷뒤_말시작전_peak=sa, ok=ok,
                     끝_받아쓰기=ta, 끝_기대=want_end, 시작_받아쓰기=tb, 시작_기대=want_start, 받아쓰기_엄격=asr_ok))
    print(("✓" if ok and asr_ok else "✗"), f"{k}→{k+1} 컷 {cut:.3f} | 조각 {p1}/{p2} 겹침 {ovl} | 소리 {sb}/{sa} | 끝 「{ta[-12:]}」 기대 …{want_end} | 시작 「{tb[:12]}」 기대 {want_start}…", flush=True)
json.dump(rows, open(f"{O}/경계_조각.json", "w"), ensure_ascii=False, indent=1)
bad = [r["k"] for r in rows if not (r["ok"] and r["받아쓰기_엄격"])]
print("넘김", len(rows), "걸림", bad); sys.exit(1 if bad else 0)
