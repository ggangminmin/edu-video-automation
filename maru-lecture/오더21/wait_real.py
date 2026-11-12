# 확인문제(5.5)·스스로 확인하기(3.0) 장: 실제 mp4 소리 기준 말끝 → 다음 컷 대기 실측 (pS 11/3 00:4x)
#  말끝 = 컷 앞 구간에서 10ms RMS 가 BGM 바닥(대기 구간 중앙값) + 12dB 를 넘는 마지막 프레임 끝 · 비교용 = 타임라인 깐 깨끗한 음성 −40dB 마지막 소리
import json, subprocess, sys, numpy as np
SR = 16000
def dec(p, a, d):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", p, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def db(x): n = SR // 100; m = len(x) // n; return 20 * np.log10(np.sqrt((x[:m * n].reshape(m, n) ** 2).mean(1)) + 1e-9)
rows = []
for N in (12, 13, 14, 15):
    D = f"{N}강"; tl = json.load(open(f"{D}/타임라인_v3.json")); S = tl["slides"]
    sys.argv = ["x", str(N)]; exec(open("오더21/gap_check21.py").read().split("def sils")[0].split("N = sys.argv")[0])
    for i, s in enumerate(S[:-1]):
        if not (s.get("quiz_wait") or s.get("self_check_wait")): continue
        cut = S[i + 1]["start"]; want = 5.5 if s.get("quiz_wait") else 3.0
        a = cut - want - 3.0; x = db(dec(f"{D}/{D}_v3b.mp4", a, want + 3.0))
        floor = float(np.median(x[-int((want - 0.6) * 100):-20]))
        loud = np.where(x > floor + 12)[0]; end_mp4 = a + (loud.max() + 1) / 100 if len(loud) else None
        rows.append(dict(강=N, 장=s["slide"], 종류="확인문제" if s.get("quiz_wait") else "스스로", 기준=want, 타임라인_말끝=round(s["voice_end"], 3), 실측_말끝=round(end_mp4, 3),
                         컷=round(cut, 3), 실측_대기=round(cut - end_mp4, 3), 타임라인_대기=round(cut - s["voice_end"], 3), BGM바닥=round(floor, 1)))
out = ["# 대기 실측 v3b — 확인문제 5.5±0.1 · 스스로 확인하기 3.0±0.1 (실제 mp4 소리, 2026-11-03 야간-12~15)", "",
       "말끝 = 컷 앞 10ms RMS 가 BGM 바닥(대기 구간 중앙값)+12dB 넘는 마지막 프레임 끝. `오더21/wait_real.py`.", "",
       "| 강 | 장 | 종류 | 타임라인 말끝 | 실측 말끝 | 컷 | 실측 대기 | 타임라인 대기 | 차(실측−타임라인 말끝) | 판정 |", "|---|---|---|---|---|---|---|---|---|---|"]
bad = []
for r in rows:
    ok = abs(r["실측_대기"] - r["기준"]) <= 0.1
    if not ok: bad.append(r)
    out.append(f"| {r['강']} | {r['장']} | {r['종류']} | {r['타임라인_말끝']} | {r['실측_말끝']} | {r['컷']} | **{r['실측_대기']}** | {r['타임라인_대기']} | {round(r['실측_말끝'] - r['타임라인_말끝'], 3)} | {'✅' if ok else '❌'} |")
out += ["", f"범위 밖 {len(bad)}곳: " + (", ".join(f"{r['강']}강 {r['장']}번 {r['실측_대기']}" for r in bad) if bad else "없음")]
open("오더21/대기_실측_v3b.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
