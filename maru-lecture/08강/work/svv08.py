# 메모 문장 ↔ 녹음 받아쓰기(mlx · cpp 둘 다) 글자 맞춤 — 오더21 sent_vs_voice 방식 + 이웃 장까지(장 경계 ±3초) · 낮은 문장은 받아쓰기 조각 같이 출력
import json, re, difflib
tl = json.load(open("../타임라인_초안.json")); NOTES = json.load(open("../notes_clean.json"))
M = [(a, b, w) for a, b, w in json.load(open("mlxwords.json"))]
C = [(w["offsets"]["from"]/1000, w["offsets"]["to"]/1000, w["text"]) for w in json.loads(open("wfull.json","rb").read().decode("utf-8","replace"))["transcription"]]
NUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5"}
def nz(s):
    s = re.sub(r"(일|이|삼|사|오) 번", lambda m: NUM[m.group(1)] + "번", s); return re.sub(r"[^가-힣0-9]", "", s)
L = max(s["slide"] for s in tl["slides"]); AU = {a["slide"]: a for a in tl["audio"]}
out = []
for s in range(2, L + 1):
    a = AU[s]
    segs = ["".join(nz(w) for t0, t1, w in W if a["src_from"] - 3 <= t0 < a["src_to"] + 3) for W in (M, C)]
    for x in [x for x in re.split(r"(?<=[.?!])\s+", " ".join(NOTES[s - 1])) if nz(x)]:
        t = nz(x); r = []
        for seg in segs:
            sm = difflib.SequenceMatcher(None, t, seg, autojunk=False); r.append(round(sum(b.size for b in sm.get_matching_blocks() if b.size >= 2) / len(t), 2))
        out.append(dict(slide=s, mlx=r[0], cpp=r[1], sent=x))
json.dump(out, open("svv08.json", "w"), ensure_ascii=False, indent=1)
for o in sorted(out, key=lambda o: max(o["mlx"], o["cpp"]))[:20]: print(o["slide"], o["mlx"], o["cpp"], o["sent"])
