# 오더34 + 팀장 알림(18강 p1V 발견 · cx U1): 타임라인_v4 → v4b = 줄 나눔으로 새로 생긴 줄 시작만 실소리 기준으로 다시
#  실소리 = 깨끗한 음성(타임라인 audio 대로 깐 v090·인삿말·끝인사) 5ms RMS · 받아쓰기 시각 ±0.15초 안 가장 깊은 골짜기 → 골짜기 뒤 −50dB 를 30ms 이상 넘는 첫 시각
#           (골짜기가 −45dB 보다 얕으면 = 쉼 없이 이어진 말 → 골짜기 자체) · 새 줄 시작 = 실소리 − 0.09 (18강 make_tl_v4b.py ONSET 과 같은 정의)
#  + 18강 cx D1 예방: 글자가 앞판(v3c)과 같은 줄은 시작을 앞판 그대로
import json, numpy as np, subprocess
def _load(f): return np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True).stdout,np.float32)
tl = json.load(open("../타임라인_v4.json")); base = json.load(open("../타임라인_v3c.json")); SR = 16000
src = {None: _load("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in src: src[k] = _load(k.replace("work/", ""))
    y = src[k][int(s["src_from"] * SR):int(s["src_to"] * SR)]; o = int(s["out"] * SR); V[o:o + len(y)] += y
H = 80; db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
def onset(v):
    i0, i1 = int((v - 0.15) * 200), int((v + 0.15) * 200); m = i0 + int(np.argmin(db[i0:i1]))
    if db[m] > -45: return m / 200, float(db[m])
    j = m
    while not all(db[j + q] > -50 for q in range(6)): j += 1
    return j / 200, float(db[m])
S = tl["subs"]; old = {(round(s["start"], 4), s["text"]) for s in base["subs"]}; oldt = {s["text"]: s for s in base["subs"]}
rows = []
# 🆕받아쓰기 검증(onset_asr_v4b.py) 뒤 손 실측: 이어진 말(쉼 없음)에서 골짜기가 앞 음절 안에 잡힌 줄 · 받아쓰기 시각이 맞은 줄
OVR = {"마루시공전문가가 갖춰야": 8.83, "앞으로의 직업 전망과": 13.49, "동료에게 확인한": 25.293, "완료와 관리": 630.80}
for k, s in enumerate(S):
    if (round(s["start"], 4), s["text"]) in old: continue
    if s["text"] in oldt and k > 0 and S[k - 1]["text"] == base["subs"][base["subs"].index(oldt[s["text"]]) - 1]["text"]:
        o = oldt[s["text"]]; rows.append(dict(n=s["n"], text=s["text"], was=round(s["start"], 3), now=round(o["start"], 3), why="글자 앞판 같음 → 앞판 시작"))
        s["start"] = o["start"]; s["voice_on"] = o.get("voice_on"); S[k - 1]["end"] = s["start"]; continue
    if not str(s.get("how", "")).startswith("줄나눔v4"): continue
    on, vdb = onset(s["voice_on"])
    for k_, v_ in OVR.items():
        if s["text"].startswith(k_): on = v_   # 받아쓰기 검증(onset_v4b_asr.json)에서 골짜기 자리가 틀린 줄 — 손 실측
    rows.append(dict(n=s["n"], text=s["text"], was=round(s["start"], 3), asr=s["voice_on"], valley_db=round(vdb, 1), onset=round(on, 3), now=round(on - 0.09, 3), d=round(on - 0.09 - s["start"], 3)))
    s["start"] = on - 0.09; s["voice_on"] = round(on, 3); S[k - 1]["end"] = s["start"]; s["how"] = "줄나눔v4b(실소리 −50dB 30ms 상승 −0.09)"
# 🆕팀장 알림: newline_onset_check v2 걸림 줄 — 자막 시작 직접(두 후보 다 통과하는 자리 또는 검사기 쉼 끝 −0.09)
START = {"동료에게 확인한": (25.17, 25.34, "두 후보 쉼 끝 25.18(고객 ㄱ 막힘)·골짜기 25.34 모두 선행 0~0.177 안"), "실행할 수 있는": (455.70, 455.87, "두 후보 쉼 끝 455.72·골짜기 455.87 모두 선행 0~0.177 안"), "추가 수입을": (66.29, 66.38, "검사기 쉼 끝 66.38 −0.09 · 받아쓰기: 66.38 앞 = 「…알면서」 끝 / 66.105 앞 = 「알면」에서 끊김")}
for k, s in enumerate(S):
    for k_, (st_, on_, why) in START.items():
        if s["text"].startswith(k_):
            s["start"] = st_; s["voice_on"] = on_; S[k - 1]["end"] = st_; s["how"] = "줄나눔v4b(newline_onset_check: " + why + ")"
            rows.append(dict(n=s["n"], text=s["text"], now=st_, why=why))
for a, c in zip(S, S[1:]): assert a["end"] <= c["start"] + 1e-6 and c["start"] > a["start"] + 0.5, (a, c)
tl["params"]["v4b"] = "새 줄 시작 = 실소리(깨끗한 음성 −50dB 30ms 상승) − 0.09 (18강 p1V 방식)"
json.dump(tl, open("../타임라인_v4b.json", "w"), ensure_ascii=False, indent=1)
json.dump(rows, open("onset_v4b.json", "w"), ensure_ascii=False, indent=1)
for r in rows: print(r)
print("고침", len(rows))
