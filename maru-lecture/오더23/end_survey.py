# 오더23(pS 00:5x): 장마다 타임라인 말끝(voice_end) vs 실제 말끝(타임라인대로 깐 깨끗한 음성, −40dB 무음 시작) → 차이 > 1프레임이면 대기(문제 5.5·스스로 3·넘김 1.71)가 그만큼 길어짐
# 실행: python3 오더23/end_survey.py NN 타임라인_xx.json → 오더23/end_survey_NN.json
import sys, json, re, subprocess, numpy as np
N, TLN = sys.argv[1:3]; D = f"{N}강"; SR = 48000
exec(open("오더23/gap_check23.py").read().split("def gaps")[0].split("N, TLN, BASEN")[0])   # import 만
exec("def voice(tlp):" + open("오더23/gap_check23.py").read().split("def voice(tlp):")[1].split("def gaps")[0])
tl, v = voice(f"{D}/{TLN}"); S = sils(v); L = max(s["slide"] for s in tl["slides"]); out = []
for s in tl["slides"]:
    if not 2 <= s["slide"] < L: continue
    ve = s["voice_end"]; nxt = s["end"]
    real = max((u for u, w in S if u <= nxt + 0.01 and u > s["start"]), default=None)        # 컷 전 마지막 무음 시작 = 실제 말끝
    kind = "문제" if s.get("wait") == "문제" or s.get("quiz_wait") else ("스스로" if s.get("wait") == "스스로" or s.get("self_check_wait") else "넘김")
    want = {"문제": 5.5, "스스로": 3.0, "넘김": 1.71}[kind]
    out.append(dict(slide=s["slide"], kind=kind, voice_end=round(ve, 3), real_end=round(real, 3), late=round(ve - real, 3), wait_real=round(nxt - real, 3), want=want))
bad = [o for o in out if abs(o["wait_real"] - o["want"]) > 1.5 / 29.97]
json.dump(dict(rows=out, bad=bad), open(f"오더23/end_survey_{N}.json", "w"), ensure_ascii=False, indent=1)
print(N, TLN, "장", len(out), "대기 어긋남(>1프레임)", [(o["slide"], o["kind"], o["wait_real"], o["late"]) for o in bad])
