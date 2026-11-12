# pS 11/3 01:xx: 장 넘김마다 소리 조각 경계가 말 중간을 자르지 않았나(19강 2→3 「엠에스|디에스는」 같은 것) — 11강 v5(납품 v5c)·12~15 v3(=v3b)
#  ① v090 원음에서 장 k 마지막 조각 끝(src_to)·장 k+1 첫 조각 시작(src_from) 자리가 무음(−40dB)이고 그 무음이 ≥0.3초인가
#  ② 출력(깨끗한 음성)에서 장 k 말끝(voice_end) 뒤 ~ 컷 사이, 컷 ~ 장 k+1 말 시작(voice_start) 사이에 소리가 없나
#  ③ 받아쓰기용 조각(장 k 말끝 앞 0.8초 · 장 k+1 말 시작 뒤 0.8초, 깨끗한 음성) → 오더21/chk_piece/NN_kk_{a,b}.wav
import json, re, subprocess, sys, os, numpy as np
SR = 48000; os.makedirs("오더21/chk_piece", exist_ok=True)
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def sils(v):
    o = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "silencedetect=n=-40dB:d=0.02", "-f", "null", "-"], input=v.tobytes(), capture_output=True).stderr.decode()
    return list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
def insil(S, t, tol=0.005): return next(((u, w) for u, w in S if u - tol <= t <= w + tol), None)
res = {}
for N, tlp in ((11, "11강/타임라인_v5.json"), (12, "12강/타임라인_v3.json"), (13, "13강/타임라인_v3.json"), (14, "14강/타임라인_v3.json"), (15, "15강/타임라인_v3.json")):
    D = f"{N}강"; tl = json.load(open(tlp)); src = load(f"{D}/work/v090.wav"); S0 = sils(src)
    T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
    for a in tl["audio"]:
        p = f"{D}/" + a["src"] if a.get("src") else f"{D}/work/v090.wav"
        if p not in cache: cache[p] = load(p)
        seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
        i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
    S1 = sils(v[:int(T * SR)])
    SL = {s["slide"]: s for s in tl["slides"]}; L = max(SL); rows = []
    body = [a for a in tl["audio"] if not a.get("src")]
    for k in range(2, L):
        ak = [a for a in body if a["slide"] == k]; an = [a for a in body if a["slide"] == k + 1]
        end_src = max(a["src_to"] for a in ak); nxt_src = min(a["src_from"] for a in an) if an else None
        e1 = insil(S0, end_src); e2 = insil(S0, nxt_src) if nxt_src is not None else ("끝인사", 0)
        p1 = "무음 밖(말 중간)" if not e1 else ("짧은 쉼 %.2f" % (e1[1] - e1[0]) if e1[1] - e1[0] < 0.3 else "ok")
        p2 = "-" if nxt_src is None else ("무음 밖(말 중간)" if not e2 else ("짧은 쉼 %.2f" % (e2[1] - e2[0]) if e2[1] - e2[0] < 0.3 else "ok"))
        ovl = round(end_src - nxt_src, 3) if nxt_src is not None and end_src > nxt_src + 0.005 else 0
        cut = SL[k + 1]["start"]; ve = SL[k]["voice_end"]; vs = SL[k + 1]["voice_start"]
        x = v[int((ve + 0.05) * SR):int(cut * SR)]; y = v[int(cut * SR):int((vs - 0.05) * SR)]
        pk = lambda z: round(float(20 * np.log10(np.abs(z).max() + 1e-9)), 1) if len(z) else -180
        snd_before, snd_after = pk(x), pk(y)
        ok = p1 == "ok" and p2 in ("ok", "-") and ovl == 0 and snd_before < -40 and snd_after < -40
        for tag, a_, b_ in (("a", ve - 0.8, ve + 0.1), ("b", vs - 0.1, vs + 0.8)):
            seg = v[int(a_ * SR):int(b_ * SR)]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ar", "16000", f"오더21/chk_piece/{N}_{k:02d}_{tag}.wav"], input=seg.tobytes())
        rows.append(dict(k=k, cut=round(cut, 3), 조각끝_src=round(end_src, 3), 조각끝=p1, 다음조각시작_src=nxt_src and round(nxt_src, 3), 다음조각시작=p2, 겹침=ovl,
                         말끝뒤_컷전_peak=snd_before, 컷뒤_말시작전_peak=snd_after, ok=ok))
    res[N] = rows
    print(N, "넘김", len(rows), "걸림", [(r["k"], r["조각끝"], r["다음조각시작"], r["겹침"], r["말끝뒤_컷전_peak"], r["컷뒤_말시작전_peak"]) for r in rows if not r["ok"]])
json.dump(res, open("오더21/piece_survey.json", "w"), ensure_ascii=False, indent=1)
