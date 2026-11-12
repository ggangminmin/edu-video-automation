# fix_subs23.py 복사: v3b 렌더 검사 → 타임라인_v3c
# 오더23(오더09_공용/fix_subs09.py 방식): scene_sub 「늦음·너무빠름」 줄 → 검사기 말 시작(voice_t)을 깨끗한 음성에서 확인(앞 0.12초 안 가장 조용한 30ms ≤ −35dB · 뒤 0.15~0.30 ≥ 앞+10dB)
#  확인되면 타임라인_v3 → 타임라인_v3b 에서 그 줄 start = q(voice_t − 0.09) · voice_on = voice_t · 앞 줄 end = 새 start. 장면 첫 줄·확인 안 된 줄 = 사람 확인 목록.
# 실행(_작업): python3 오더23/fix_subs23.py NN  → NN강/타임라인_v3b.json · 오더23/fix_subs_NN.json
import sys, json, numpy as np, librosa
N = sys.argv[1]; FPS = 30000 / 1001; q = lambda t: round(t * FPS) / FPS
tl = json.load(open(f"{N}강/타임라인_v3b.json")); r = json.load(open(f"{N}강/검사_v3b/scene_sub.json"))   # 검사는 렌더판 기준 · 고침은 줄 기준 차이(delta)로 새 v3 에 적용
subs = {x["n"]: x for x in tl["subs"]}; first = {}
for x in tl["subs"]: first.setdefault(x["slide"], x["n"])
def clean(t0, t1):
    for a in tl["audio"]:
        src = f"{N}강/" + (a["src"] if a.get("src") else "work/v090.wav"); a0 = a["out"]; a1 = a0 + a["src_to"] - a["src_from"]
        if a0 <= t0 and t1 <= a1:
            y, _ = librosa.load(src, sr=16000, offset=a["src_from"] + t0 - a0, duration=t1 - t0); return y
    return None
fix, manual = {}, []
ACCEPT = {"19": [28, 152]}; FALSE = {}
for s in r["sync"]:
    if s["result"] not in ("늦음", "너무빠름"): continue
    x = subs[s["n"]]; vt = s["voice_t"]
    if s["n"] in ACCEPT.get(N, ()):                         # 말 붙은 자리: 원음 골짜기(−27~−36dB)가 검사기 말 시작과 일치 → 검사기 값 채택(눈 확인 11/2 pW)
        fix[s["n"]] = dict(text=x["text"], old_voice=x["voice_on"], new_voice=round(vt, 3), lead_was=s["lead"], how="골짜기 확인"); continue
    if s["n"] in FALSE.get(N, ()): manual.append((s["n"], "오탐(무음 끝 바로 뒤 말 시작 · 눈 확인)", s["lead"])); continue
    if first[x["slide"]] == x["n"]: manual.append((s["n"], "장면 첫 줄", s["lead"])); continue
    y = clean(vt - 0.15, vt + 0.30)
    if y is None: manual.append((s["n"], "소리 조각 밖", s["lead"])); continue
    db = lambda a, b: 20 * np.log10(np.sqrt((y[int(a * 16000):int(b * 16000)] ** 2).mean()) + 1e-7)
    pre = min(db(0.03 + k * 0.01, 0.06 + k * 0.01) for k in range(10)); post = db(0.15, 0.30)
    if pre <= -35 and post - pre >= 10: fix[s["n"]] = dict(text=x["text"], old_voice=x["voice_on"], new_voice=round(vt, 3), lead_was=s["lead"], pre=round(pre), post=round(post))
    else: manual.append((s["n"], f"확인 안 됨 pre{pre:.0f} post{post:.0f}", s["lead"]))
tl = json.load(open(f"{N}강/타임라인_v3.json"))            # 최신 v3(장 첫 줄 규칙 · 20강 22번 손값 반영) 위에 delta 적용 — 19강은 v3 == v3b
L = tl["subs"]
for i, x in enumerate(L):
    if x["n"] in fix:
        f = fix[x["n"]]; assert f["text"] == x["text"]; vt = x["voice_on"] + (f["new_voice"] - f["old_voice"]); st = q(vt - 0.09)
        assert L[i - 1]["slide"] == x["slide"] and st > L[i - 1]["start"]
        x["start"] = st; x["voice_on"] = round(vt, 3); x["how"] = "scene_sub 고침(v3c)"; L[i - 1]["end"] = st
tl["params"]["v3c"] = "오더23(v3b 렌더 scene_sub): scene_sub 늦음·너무빠름 줄 중 깨끗한 음성으로 확인된 것만 시작 고침(fix_subs23.py)"
json.dump(tl, open(f"{N}강/타임라인_v3c.json", "w"), ensure_ascii=False, indent=1)
json.dump(dict(fix=fix, manual=manual), open(f"오더23/fix_subs_{N}_v3c.json", "w"), ensure_ascii=False, indent=1)
print(N, "고침", len(fix), "| 사람 확인", manual)
