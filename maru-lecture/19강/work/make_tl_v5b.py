# 19강 v5b 타임라인(오더37) — v5 + 뒤 쉼 1프레임 더(v5 새 문장 끝 쉼 1.49 < 1.5) · 그 밖 make_tl_v5.py 와 같음
# (v5 머리말) 19강 v5 타임라인(오더37) = v4b + 10장 「취급·저장과 노출 방지·개인보호구 항목을 찾으세요.」 소리만 새 중간점 음성(19강 중간점.wav 0.9배)으로 — 12강 work/make_tl_v7.py 방식
#  audio 59(v090 331.2449→335.5441) → a: 앞 쉼 그대로 · b: ../중간점_새음성/19_10장.wav 전체 · c: 뒤 쉼 그대로(Δ 프레임 격자로 맞춤)
#  옛 말 331.72~335.08(3.36초) → 새 말 3.560초. 그 뒤 전부 Δ 밀기. 자막 글자 그대로(98번 한 줄, 시작 그대로 — 새 말 시작이 옛 말과 거의 같음)
import json, wave
FPS = 30000 / 1001
SEG_FROM, SEG_TO, OLD_ON, OLD_END, NEW = 331.2449, 335.5441, 331.72, 335.08, "../중간점_새음성/19_10장.wav"
t = json.load(open("../타임라인_v4b.json"))
A = t["audio"]; i = next(k for k, a in enumerate(A) if abs(a["src_from"] - SEG_FROM) < 1e-3 and not a.get("src")); old = A[i]
assert abs(old["src_to"] - SEG_TO) < 1e-3
w = wave.open("../" + NEW); flen = w.getnframes() / w.getframerate()
a_ = dict(old, src_from=SEG_FROM, src_to=round(OLD_ON - 0.02, 4))
b_ = dict(slide=old["slide"], out=round(old["out"] + (OLD_ON - 0.02 - SEG_FROM), 4), src_from=0.0, src_to=round(flen, 4), src=NEW, note="오더37 19강 중간점 새 음성(0.9배) 10장")
old_end = old["out"] + SEG_TO - SEG_FROM
D0 = (b_["out"] + flen + (SEG_TO - (OLD_END + 0.04))) - old_end
D = (int(D0 * FPS + 0.999) + 1) / FPS                                      # 프레임 격자로 올림 + 1프레임(문장 끝 쉼 ≥1.5 — v5 1.49)
c_from = OLD_END + 0.04                                                    # v5b: 원음 뒤 쉼은 v5 와 같은 자리부터(옛 말 끝 +0.04)
c_ = dict(old, out=round(b_["out"] + flen + (D - D0), 4), src_from=round(c_from, 4), src_to=SEG_TO)   # 새 파일 끝(10ms 페이드 무음)과 뒤 쉼 사이 무음 (D−D0) 끼움
new_end = c_["out"] + c_["src_to"] - c_["src_from"]; assert abs(new_end - old_end - D) < 2e-4
print(f"새 파일 {flen:.3f}초 · 옛 조각 끝 {old_end:.4f} → {new_end:.4f} · Δ0 {D0:+.4f} → Δ {D:+.4f} ({round(D*FPS)}프레임)")
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
S = t["subs"]; k = next(k for k, x in enumerate(S) if x["text"].startswith("취급·저장과"))
S[k]["voice_on"] = round(b_["out"] + 0.02, 3); S[k]["how"] = (S[k].get("how") or "") + " · 오더37 새 소리"
t["params"]["v5b_19"] = f"오더37: 10장 중간점 문장 = 새 음성(19_10장.wav) · 뒤 Δ {D:+.4f}초 · 자막 글자 그대로"
json.dump(t, open("../타임라인_v5b.json", "w"), ensure_ascii=False, indent=1)
for x in S[k - 1:k + 2]: print(x["n"], round(x["start"], 3), round(x["end"], 3), x.get("voice_on"), x["text"])
print("말", round(b_["out"] + 0.02, 3), "~", round(b_["out"] + 0.02 + 3.56, 3), "· total", round(t["total"], 3))
