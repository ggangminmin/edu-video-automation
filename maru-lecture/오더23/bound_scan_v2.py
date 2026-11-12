# 오더23 경계 훑기 v2(pS 01:0x · cx-18강 13→14 「작업」 놓침 반성):
#  v1(경계_조각_훑기.txt) 은 「조각 끝이 쉼 안인가 · 말끝이 그 쉼 시작인가」만 봄 → 말끝 뒤에 다음 장 첫 단어가 오고 그 뒤 짧은 쉼에 조각 끝이 걸리면 통과시킴(18강 13→14).
#  v2 = 장마다 깨끗한 음성(v090)에서 ① 말끝(voice_end)+0.03 ~ 조각 끝(src_to) ② 조각 시작(src_from) ~ 첫 말(voice_start)−0.03 구간에
#       10ms 창 음량이 −40dB 넘는 곳이 있으면 걸림(= 그 장 화면에서 다른 장 말이 들림 / 말이 대기 안에 숨음). 둘 다 표지·마지막 장(별도 소리) 제외.
# 실행: python3 오더23/bound_scan_v2.py NN 타임라인_xx.json
import sys, json, numpy as np, librosa
N, TLN = sys.argv[1:3]; D = f"{N}강"
tl = json.load(open(f"{D}/{TLN}")); L = max(s["slide"] for s in tl["slides"])
y, sr = librosa.load(f"{D}/work/v090.wav", sr=16000); H = 160
db = 20 * np.log10(np.sqrt(np.convolve(y ** 2, np.ones(H) / H, "valid")[::H]) + 1e-7)     # 10ms 칸
def o2s(s, t):                                     # 출력 시각 → v090 시각(그 장 조각 지도)
    P = [a for a in tl["audio"] if a["slide"] == s and not a.get("src")]
    best = min(P, key=lambda a: 0 if a["out"] <= t <= a["out"] + a["src_to"] - a["src_from"] else min(abs(t - a["out"]), abs(t - a["out"] - a["src_to"] + a["src_from"])))
    return best["src_from"] + t - best["out"], P
def loud(a, b):
    i, j = int(a * 100), int(b * 100)
    if j <= i: return None, None
    k = i + int(np.argmax(db[i:j])); return round(float(db[k]), 1), round(k / 100, 2)
bad, rows = [], []
for s in tl["slides"]:
    if not 2 <= s["slide"] < L: continue
    ve, P = o2s(s["slide"], s["voice_end"]); vs, _ = o2s(s["slide"], s["voice_start"])
    sf = min(a["src_from"] for a in P); st = max(a["src_to"] for a in P)
    tl_, tt = loud(ve + 0.03, st); hl, ht = loud(sf, vs - 0.03)
    r = dict(slide=s["slide"], src=[round(sf, 3), round(st, 3)], voice=[round(vs, 3), round(ve, 3)], tail_max=tl_, tail_at=tt, head_max=hl, head_at=ht)
    rows.append(r)
    if (tl_ is not None and tl_ > -40) or (hl is not None and hl > -40): bad.append(r)
json.dump(dict(rows=rows, bad=bad), open(f"오더23/bound_v2_{N}.json", "w"), ensure_ascii=False, indent=1)
print(N, TLN, "장", len(rows), "걸림", [(b["slide"], "꼬리", b["tail_max"], b["tail_at"], "머리", b["head_max"], b["head_at"]) for b in bad])
