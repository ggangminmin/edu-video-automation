# 규칙2 개정(11/2 23:1x): 메모 문장마다 타입캐스트 받아쓰기(mlxwords.json, v090 시각)에 있나 — 장(슬라이드) 소리 구간 안 받아쓰기와 글자 맞춤 비율
# 실행: python3 오더21/sent_vs_voice.py NN  → 비율 낮은 문장 출력 + 오더21/svv_NN.json
import sys, json, re, difflib
N = int(sys.argv[1]); D = f"{N}강"
v2 = json.load(open(f"{D}/타임라인_v2.json")); NOTES = json.load(open(f"{D}/notes_clean.json"))
W = json.load(open(f"{D}/work/mlxwords.json"))
if isinstance(W, dict): W = W.get("words", W)
W = [(w[0], w[1], w[2]) if isinstance(w, list) else (w["start"], w["end"], w["word"]) for w in W]
NUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5"}
def nz(s):
    s = re.sub(r"(일|이|삼|사|오) 번", lambda m: NUM[m.group(1)] + "번", s)
    return re.sub(r"[^가-힣0-9]", "", s)
L = max(s["slide"] for s in v2["slides"]); AU = {a["slide"]: a for a in v2["audio"]}
out = []
for s in range(2, L):
    a = AU[s]; seg = "".join(nz(w) for t0, t1, w in W if a["src_from"] - 0.3 <= t0 < a["src_to"] + 0.3)
    sents = [x for x in re.split(r"(?<=[.?!])\s+", " ".join(NOTES[s - 1])) if nz(x)]
    for x in sents:
        t = nz(x); sm = difflib.SequenceMatcher(None, t, seg, autojunk=False)
        m = sum(b.size for b in sm.get_matching_blocks() if b.size >= 2) / len(t)
        out.append(dict(slide=s, ratio=round(m, 2), sent=x))
json.dump(out, open(f"오더21/svv_{N}.json", "w"), ensure_ascii=False, indent=1)
for o in sorted(out, key=lambda o: o["ratio"])[:12]: print(N, o["slide"], o["ratio"], o["sent"])
