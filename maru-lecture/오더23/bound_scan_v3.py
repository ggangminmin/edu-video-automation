# 오더23 경계 훑기 v3(pS 01:0x): v2(말끝 뒤 소리)도 18강 13→14 를 못 잡음 — 타임라인 말끝 자체가 다음 장 첫 단어 끝으로 잡혀 있었기 때문.
#  v3 = 장마다 깨끗한 음성(v090)에서 「마지막 긴 쉼(≥0.25, −40dB) 뒤 ~ 조각 끝」 말 조각의 받아쓰기 글자(mlxwords, 단어 가운데가 구간 안)를
#       ① 이 장 마지막 자막 끝 글자 ② 다음 장 첫 자막 앞 글자와 대조 → ②와 더 닮았으면 걸림(다음 장 말이 이 장에 들어감).
#       머리도 같게: 「조각 시작 ~ 첫 긴 쉼」 글자 ↔ 이 장 첫 자막 앞 vs 앞 장 마지막 자막 끝.
# 실행: python3 오더23/bound_scan_v3.py NN 타임라인_xx.json
import sys, json, re, subprocess, difflib
N, TLN = sys.argv[1:3]; D = f"{N}강"
tl = json.load(open(f"{D}/{TLN}")); L = max(s["slide"] for s in tl["slides"])
W = json.load(open(f"{D}/work/mlxwords.json")); W = W.get("words", W) if isinstance(W, dict) else W
nz = lambda t: re.sub(r"[^가-힣0-9a-zA-Z]", "", t)
o = subprocess.run(["ffmpeg", "-i", f"{D}/work/v090.wav", "-af", "silencedetect=n=-40dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True).stderr
SIL = list(zip(map(float, re.findall(r"silence_start: ([0-9.]+)", o)), map(float, re.findall(r"silence_end: ([0-9.]+)", o))))
subs = {}
for x in tl["subs"]: subs.setdefault(x["slide"], []).append(x["text"])
def words(a, b): return nz("".join(w[2] for w in W if w[0] < b - 0.03 and w[1] > a + 0.03))   # 겹치는 단어 전부(가운데 기준은 19강 「MSDS는」 18.66~19.58 을 놓침)
def sim(a, b): return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if a and b else 0
bad, rows = [], []
for s in range(2, L):
    P = [a for a in tl["audio"] if a["slide"] == s and not a.get("src")]
    sf = min(a["src_from"] for a in P); st = max(a["src_to"] for a in P)
    inner = [(u, v) for u, v in SIL if sf + 0.05 < v and u < st - 0.05]
    t0 = max((v for u, v in inner if v < st - 0.05), default=sf); tail = words(t0, st)
    h1 = min((u for u, v in inner if u > sf + 0.05), default=st); head = words(sf, h1)
    me_end = nz(subs[s][-1])[-max(1, len(tail)):]; nx_beg = nz(subs[s + 1][0])[:max(1, len(tail))] if s + 1 < L else ""
    me_beg = nz(subs[s][0])[:max(1, len(head))]; pv_end = nz(subs[s - 1][-1])[-max(1, len(head)):] if s - 1 >= 2 else ""
    r = dict(slide=s, tail=[round(t0, 2), round(st, 2), tail], tail_me=round(sim(tail, me_end), 2), tail_next=round(sim(tail, nx_beg), 2),
             head=[round(sf, 2), round(h1, 2), head], head_me=round(sim(head, me_beg), 2), head_prev=round(sim(head, pv_end), 2))
    rows.append(r)
    if r["tail_next"] > r["tail_me"] or (pv_end and r["head_prev"] > r["head_me"]): bad.append(r)
json.dump(dict(rows=rows, bad=bad), open(f"오더23/bound_v3_{N}.json", "w"), ensure_ascii=False, indent=1)
print(N, TLN, "장", len(rows), "걸림", [(b["slide"], b["tail"], b["tail_me"], b["tail_next"], b["head"][2][:10], b["head_me"], b["head_prev"]) for b in bad])
