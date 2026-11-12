# 대본(메모) ↔ 0.9배 음성 받아쓰기 글자 대조 → 다른 곳 목록(받아쓰기 띄어쓰기·문장부호 무시)
import json, re, difflib, sys
notes = json.load(open("../notes_clean.json"))
def nc(s): return re.sub(r"[^가-힣0-9A-Za-z]", "", s)
src = sys.argv[1] if len(sys.argv) > 1 else "cpp"
if src == "cpp":
    words = [(x["offsets"]["from"]/1000, x["text"]) for x in json.load(open("wfull.json"))["transcription"]]
else:
    words = [(a, w) for a, b, w in json.load(open("mlxwords.json"))]
S, Sslide = "", []
for i, ps in enumerate(notes, 1):
    for p in ps:
        for c in nc(p): S += c; Sslide.append(i)
T, Tt = "", []
for t, w in words:
    for c in nc(w): T += c; Tt.append(t)
sm = difflib.SequenceMatcher(None, S, T, autojunk=False)
m = sum(n for *_, n in sm.get_matching_blocks())
print(f"[{src}] 대본 {len(S)}자 · 받아쓰기 {len(T)}자 · 일치 {m} ({m/len(S):.1%})")
for op, a, b, c, d in sm.get_opcodes():
    if op == "equal": continue
    t = Tt[min(c, len(Tt)-1)]
    print(f"슬{Sslide[min(a,len(S)-1)]:>2} {t:7.2f}s {op:7} 대본「{S[max(0,a-4):a]}[{S[a:b]}]{S[b:b+4]}」 음성「{T[max(0,c-4):c]}[{T[c:d]}]{T[d:d+4]}」")
