# 녹음≠메모 후보: 문장마다 메모 ↔ 받아쓰기(cpp·mlx) 글자 차이 중 두 받아쓰기가 같은 자리에서 다른 것
import json, re, difflib
S = json.load(open("svv10.json"))
def nz(s): return re.sub(r"[^가-힣0-9a-zA-Z]", "", s)
mlx = [(a, w) for a, b, w in json.load(open("mlxwords.json"))]
cpp = [(w["offsets"]["from"] / 1000, w["text"]) for w in json.load(open("wfull.json"))["transcription"]]
memo = "".join(nz(o["sent"]) for o in S); own = []
for o in S: own += [o["k"]] * len(nz(o["sent"]))
def ops(ws):
    asr = "".join(nz(w) for _, w in ws)
    sm = difflib.SequenceMatcher(None, memo, asr, autojunk=False); r = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        k = own[min(i1, len(own) - 1)]
        r.setdefault(k, []).append((memo[max(0,i1-3):i2+3], memo[i1:i2], asr[j1:j2]))
    return r
A, B = ops(mlx), ops(cpp)
for o in S:
    k = o["k"]
    if k in A and k in B:
        print(o["slide"], o["t"], o["sent"][:50]); print("   mlx", A[k]); print("   cpp", B[k])
