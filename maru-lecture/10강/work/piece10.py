# 10강(오더43) 장 경계 조각 훑기 = 오더21 piece_survey.py + asr_piece.py 합본 사본 · 모든 컷(1→2 ~ L−1→L)
#  ① v090 원음에서 장 k 끝 조각(src_to)·장 k+1 첫 조각(src_from) 자리가 무음(−40dB ≥0.3초)  ② 출력 깨끗한 음성에서 말끝~컷 · 컷~말 시작 사이 소리 없음(peak < −40)
#  ③ 받아쓰기(말끝 앞 0.8초 · 말 시작 뒤 0.8초) → 장 끝 = 메모 마지막 3글자 · 다음 장 = 첫 2글자 **엄격** 대조
# 실행(_작업): ~/.venvs/tts/bin/python 10강/work/piece10.py 10강/타임라인_v1.json 10강/검사_v1  (heavy_run asr)
import json, re, subprocess, sys, os, numpy as np, mlx_whisper
tlp, O = sys.argv[1:3]; D = "10강"; SR = 48000; os.makedirs(f"{O}/chk_piece", exist_ok=True)
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
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
NUM = str.maketrans({"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오"})
def tr(a, b): return mlx_whisper.transcribe(v[int(a * SR):int(b * SR)][::3].copy(), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
for k in range(1, L):
    ak = [a for a in tl["audio"] if a["slide"] == k]; an = [a for a in tl["audio"] if a["slide"] == k + 1]
    p1 = p2 = "-"; ovl = 0
    if all(not a.get("src") for a in ak) and all(not a.get("src") for a in an):
        end_src = max(a["src_to"] for a in ak); nxt_src = min(a["src_from"] for a in an)
        e1 = insil(S0, end_src); e2 = insil(S0, nxt_src)
        p1 = "무음 밖(말 중간)" if not e1 else ("짧은 쉼 %.2f" % (e1[1] - e1[0]) if e1[1] - e1[0] < 0.3 else "ok")
        p2 = "무음 밖(말 중간)" if not e2 else ("짧은 쉼 %.2f" % (e2[1] - e2[0]) if e2[1] - e2[0] < 0.3 else "ok")
        ovl = round(end_src - nxt_src, 3) if end_src > nxt_src + 0.005 else 0
    cut = SL[k + 1]["start"]; ve = SL[k]["voice_end"]; vs = SL[k + 1]["voice_start"]
    x = v[int((ve + 0.05) * SR):int(cut * SR)]; y = v[int(cut * SR):int((vs - 0.05) * SR)]
    pk = lambda z: round(float(20 * np.log10(np.abs(z).max() + 1e-9)), 1) if len(z) else -180
    a_txt, b_txt = tr(ve - 0.8, ve + 0.1), tr(vs - 0.1, vs + 0.8)
    subs_k = [s for s in tl["subs"] if s["slide"] == k]; subs_n = [s for s in tl["subs"] if s["slide"] == k + 1]
    want_end, want_head = kn(subs_k[-1]["text"])[-3:], kn(subs_n[0]["text"])[:2]
    ga, gb = kn(a_txt).translate(NUM), kn(b_txt).translate(NUM)
    end_ok = ga.endswith(want_end); head_ok = gb.startswith(want_head)
    ok = p1 in ("ok", "-") and p2 in ("ok", "-") and ovl == 0 and pk(x) < -40 and pk(y) < -40 and end_ok and head_ok
    r = dict(k=k, cut=round(cut, 3), 조각끝=p1, 다음조각시작=p2, 겹침=ovl, 말끝뒤_컷전_peak=pk(x), 컷뒤_말시작전_peak=pk(y),
             끝_받아쓰기=a_txt, 끝_기대=want_end, 끝_ok=end_ok, 첫_받아쓰기=b_txt, 첫_기대=want_head, 첫_ok=head_ok, ok=ok)
    rows.append(r); print(("✓" if ok else "✗"), k, "→", k + 1, f"컷 {cut:.2f}", p1, p2, ovl, r["말끝뒤_컷전_peak"], r["컷뒤_말시작전_peak"], f"끝「{a_txt[-12:]}」({want_end}) 첫「{b_txt[:12]}」({want_head})", flush=True)
json.dump(rows, open(f"{O}/경계_조각_훑기.json", "w"), ensure_ascii=False, indent=1)
bad = [r for r in rows if not r["ok"]]; print("넘김", len(rows), "걸림", len(bad)); sys.exit(1 if bad else 0)
