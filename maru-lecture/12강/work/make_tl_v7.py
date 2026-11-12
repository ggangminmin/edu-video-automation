# 12강 v7 타임라인(오더36 ⓑ) = v6 + 20장 「보고서에는 기본 정보·사용 자재·시공 방법·환경 측정값·사진 등을 기록합니다.」 소리만 새 중간점 음성으로
#  audio 123(v090 665.4479→671.9461) → a: v090 665.4479→665.96(앞 쉼 그대로) · b: 새 문장 ../중간점_새음성/12_20장.wav 전체 · c: v090 671.525→671.9461(뒤 쉼 그대로)
#  옛 말 665.98~671.485(5.505초) → 새 말 6.490초 · 그 뒤 전부 Δ 밀기(소리·자막·장·끝인사·엔딩·total). 자막 글자 그대로, 187번(둘째 줄) 시작만 새 소리 단어 시각 −0.09.
import json, wave
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
t = json.load(open("../타임라인_v6.json"))
A = t["audio"]; i = next(k for k, a in enumerate(A) if abs(a["src_from"] - 665.4479) < 1e-3 and not a.get("src")); old = A[i]
assert abs(old["src_to"] - 671.9461) < 1e-3
NEW = "../중간점_새음성/12_20장.wav"
w = wave.open("../" + NEW); flen = w.getnframes() / w.getframerate()
a_ = dict(old, src_from=665.4479, src_to=665.96)
b_ = dict(slide=old["slide"], out=round(old["out"] + (665.96 - 665.4479), 4), src_from=0.0, src_to=round(flen, 4), src=NEW, note="오더36 중간점 새 음성(0.9배) 20장")
old_end = old["out"] + old["src_to"] - old["src_from"]
D0 = (b_["out"] + flen + (671.9461 - 671.525)) - old_end                    # 0.985 = 29.5 프레임
D = round(round(D0 * FPS) + (0.5 if (D0 * FPS) % 1 == 0.5 else 0)) / FPS if False else (int(D0 * FPS + 0.999) / FPS)   # 프레임 격자로 올림(장 컷 ±1프레임 흔들림 방지)
c_from = 671.525 - (D - D0); assert c_from > 671.485 + 0.02, c_from      # 뒤 쉼을 늘려 맞춤(원음 말 끝 671.485 뒤)
c_ = dict(old, out=round(b_["out"] + flen, 4), src_from=round(c_from, 4), src_to=671.9461)
new_end = c_["out"] + c_["src_to"] - c_["src_from"]; assert abs(new_end - old_end - D) < 2e-4, (new_end - old_end, D)
print(f"새 파일 {flen:.3f}초 · 옛 조각 끝 {old_end:.4f} → 새 {new_end:.4f} · Δ {D:+.4f}")
A[i:i + 1] = [a_, b_, c_]
TH = old_end - 1e-3
def sh(x): return x + D if x >= TH else x
for a in A[i + 3:]: a["out"] = round(a["out"] + D, 4)
for s in t["slides"]:
    for k in ("start", "end", "voice_start", "voice_end"):
        if k in s: s[k] = sh(s[k])
for x in t["subs"]:
    x["start"] = sh(x["start"]); x["end"] = sh(x["end"])
    if x.get("voice_on"): x["voice_on"] = round(sh(x["voice_on"]), 3)
for an in t["anchors"]:
    for k in ("in", "out", "clip_t0"):
        if an.get(k) is not None and an[k] >= TH: an[k] = an[k] + D
E = t["ending"]
for k, v in list(E.items()):
    if isinstance(v, list): E[k] = [sh(z) for z in v]
    elif isinstance(v, (int, float)): E[k] = sh(v)
t["total"] = t["total"] + D
# 187번 둘째 줄 「환경 측정값·…」 시작 = 새 소리 「환경」 시작(중간점_090 3.89 → 자른 파일 −0.035) − 0.09
S = t["subs"]; k = next(k for k, x in enumerate(S) if x["text"].startswith("환경 측정값·사진"))
von = b_["out"] + (3.89 - 0.035); S[k]["start"] = q(von - 0.09); S[k]["voice_on"] = round(von, 3); S[k - 1]["end"] = S[k]["start"]
S[k]["how"] = "오더36 새 소리 「환경」 시작 −0.09"
S[k - 1]["voice_on"] = round(b_["out"] + 0.02, 3); S[k - 1]["how"] = (S[k - 1].get("how") or "") + " · 오더36 새 소리"
t["params"]["v7"] = f"오더36: 20장 중간점 문장 = 새 음성(12_20장.wav) · 뒤 Δ {D:+.4f}초 · 자막 글자 그대로"
json.dump(t, open("../타임라인_v7.json", "w"), ensure_ascii=False, indent=1)
for x in S[k - 2:k + 3]: print(x["n"], round(x["start"], 3), round(x["end"], 3), x.get("voice_on"), x["text"])
print("ending", {k: v for k, v in E.items() if not isinstance(v, str)}, "total", t["total"])
