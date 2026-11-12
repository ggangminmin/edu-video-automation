# 09강 사본(오더44 · 팀장 추가 · 오더23/end_survey.py): 장마다 타임라인 말끝 vs 실제 말끝(깨끗한 음성 −40dB 무음 시작) → 실제 대기(문제 5.5·스스로 3·넘김 1.71) 어긋남 >1프레임
#  🆕 원음 클릭이 무음을 가르는 경우(10강 예외 ③④) 대비: 컷 전 마지막 「−40dB 무음 시작」 + 그 무음 안 클릭 무시판(−40dB 무음 사이 소리 ≤30ms 는 무음으로 이어 붙임) 둘 다 표시
import sys, json, re, subprocess, numpy as np
VER = sys.argv[1]
src = open("09강/검사도구/gap_check09.py").read().split("def gap(")[0].replace("VER = sys.argv[1]", f"VER = '{VER}'")
exec(src)   # tl · v(깨끗한 음성) · S3 · SL · L
def merge(S, g=0.03):
    out = []
    for u, w in S:
        if out and u - out[-1][1] <= g: out[-1] = (out[-1][0], w)
        else: out.append((u, w))
    return out
SM = merge(S3); rows = []
for s in tl["slides"]:
    if not 2 <= s["slide"] < L: continue
    nxt = s["end"]
    real = max((u for u, w in S3 if u <= nxt + 0.01 and u > s["start"]), default=None)
    real_m = max((u for u, w in SM if u <= nxt + 0.01 and u > s["start"]), default=None)
    kind = "문제" if s.get("quiz_wait") else ("스스로" if s.get("self_check_wait") else "넘김"); want = {"문제": 5.5, "스스로": 3.0, "넘김": 1.71}[kind]
    rows.append(dict(slide=s["slide"], kind=kind, voice_end=round(s["voice_end"], 3), real_end=round(real, 3), real_end_클릭무시=round(real_m, 3),
                     late=round(s["voice_end"] - real, 3), wait_real=round(nxt - real, 3), wait_real_클릭무시=round(nxt - real_m, 3), want=want))
bad = [r for r in rows if abs(r["wait_real"] - r["want"]) > 1.5 / 29.97 or abs(r["wait_real_클릭무시"] - r["want"]) > 1.5 / 29.97]
json.dump(dict(rows=rows, bad=bad), open(f"09강/검사_{VER}/end_survey.json", "w"), ensure_ascii=False, indent=1)
print("09", VER, "장", len(rows), "대기 어긋남(>1프레임)", [(r["slide"], r["kind"], r["wait_real"], r["wait_real_클릭무시"], r["late"]) for r in bad])
for r in rows: print(" ", r["slide"], r["kind"], "말끝", r["voice_end"], "실제", r["real_end"], "/", r["real_end_클릭무시"], "대기", r["wait_real"], "/", r["wait_real_클릭무시"])
sys.exit(1 if bad else 0)
