# 09강 v6 (오더51 토막 자막) = 타임라인_v5 의 자막 나눔·시각만 바꿈 · 소리·장·아나운서·BGM·텀 그대로
# SPLIT: v5 subs 인덱스(문장 첫 카드) → 새 카드 글자들(이어 붙이면 v5 문장과 글자 같음 — 검사함)
# 새 둘째 카드 시작 = 실소리 −0.09 (onset_v6.json 에 실측값 있으면 그것, 없으면 받아쓰기 근사 → newline_onset_check 로 실측 후 채움)
import json, os, sys, re
H = os.path.dirname(os.path.abspath(__file__)); L = os.path.dirname(H)
tl = json.load(open(f"{L}/타임라인_v5.json")); S = tl["subs"]
# 팀장 결정(11/9 · 오더51 공통 · 기준 조정 2회): 짧은 쪽 ≥10자(공백 뺌) + 쏠림 ≥0.45 + line_break 통과하는 자연스러운 자리(연결어미·쉼표 뒤)면 나눔,
#   그런 자리가 없을 때만 잉크 폭 ≤1500px 한 장. v5 자리가 이미 통과하면(50·99·144·185·193) 건드리지 않음.
SPLIT = {
    8:   ["첫 줄이 조금 틀어졌는데 마지막에 맞추면 되겠지 하고", "넘어가는 장면도 생각해 보죠"],
    11:  ["설치 전에는 자재를 여러 장 펼쳐", "색과 무늬, 옹이의 분포를 봅니다"],
}
for k in (24, 48, 67, 130, 134, 156, 171, 233): SPLIT[k] = None   # None = 한 장(팀장 결정)
M77 = os.environ.get("M77", "")   # 77(4:58) 팀장 답 대기: "one" = 한 장 1529px · 그 밖 = v5 그대로
if M77 == "one": SPLIT[77] = None
LIMIT = 1530 if M77 == "one" else 1500
from PIL import ImageFont
_F = ImageFont.truetype("/Users/mac_production/Library/Fonts/Freesentation-7Bold.ttf", 58)
def ink(t): return sum(_F.getlength(c) for c in t) - 0.78 * (len(t) - 1)
# 문장 카드 범위: 첫 카드 i 부터 다음 카드가 같은 장이고 v5 에서 둘째 카드(쉼표·연결 뒤)인 동안
def group(i):
    g = [i]
    while g[-1] + 1 < len(S) and S[g[-1] + 1]["slide"] == S[i]["slide"] and not S[g[-1]]["text"].rstrip().endswith(("다", "요", "죠", "까", ".", "?")):
        g.append(g[-1] + 1)
    return g
FPS = 30000 / 1001
W = json.load(open(f"{H}/mlxwords.json"))
def v2out(t):
    for a in tl["audio"]:
        if a.get("src") is None and a["src_from"] - 1e-6 <= t < a["src_to"]: return a["out"] + t - a["src_from"]
def out2v(o):
    for a in tl["audio"]:
        if a.get("src") is None and a["out"] - 1e-6 <= o < a["out"] + a["src_to"] - a["src_from"]: return a["src_from"] + o - a["out"]
ON = json.load(open(f"{H}/onset_v6.json")) if os.path.exists(f"{H}/onset_v6.json") else {}
def first_word_time(word, t0, t1):
    best = None
    for s, e, w in W:
        o = v2out(s)
        if o is None or not (t0 < o < t1): continue
        if w.strip().startswith(word[:2]):
            if best is None or o < best: best = o
    return best
out = []; ch = []; skip = set()
for i, x in enumerate(S):
    if i in skip: continue
    if i not in SPLIT: out.append(dict(x)); continue
    g = group(i); skip.update(g)
    old = [S[j]["text"] for j in g]; sent = " ".join(old); st0, en0 = S[g[0]]["start"], S[g[-1]]["end"]
    new = SPLIT[i] or [sent]
    assert " ".join(new) == sent, (i, new, sent)
    assert all(ink(t) <= LIMIT for t in new), new
    c1 = dict(S[g[0]]); c1["text"] = new[0]; c1["end"] = en0; out.append(c1); starts = [st0]
    if len(new) == 2:
        key = new[1]
        if key in ON: st = ON[key] - 0.09; how = f"실소리 {ON[key]:.3f} −0.09"
        else:
            # 같은 자리였던 v5 카드가 있으면 그 시작(실측 통과값) 그대로
            same = [S[j] for j in g if S[j]["text"] == key]
            if same: st = same[0]["start"]; how = "v5 시작 그대로"
            else:
                wt = first_word_time(key.split()[0], st0 + 0.3, en0); st = wt - 0.09; how = f"받아쓰기 근사 {wt:.3f}"
        c1["end"] = st
        c2 = dict(S[g[-1]]); c2["text"] = new[1]; c2["start"] = st; c2["voice_on"] = round(st + 0.09, 3); c2["end"] = en0
        c2["v090_on"] = round(out2v(st + 0.09), 3); c2["how"] = "토막 고침 둘째 카드"; c2["sent_start"] = False; out.append(c2); starts.append(st)
    ch.append(dict(i=i, slide=S[i]["slide"], old=old, oldst=[S[j]["start"] for j in g], new=new, st=starts, how=how if len(new) == 2 else f"팀장 결정: 한 장 {len(new[0])}자 · 폭 {round(ink(new[0]))}px"))
for n, x in enumerate(out, 1): x["n"] = n
tl["subs"] = out
tl["params"]["v6"] = "오더51 토막 자막: 문장 " + str(len(ch)) + "곳 나눔·합침(변경표_v6.md) · 소리·장·아나운서 v5 그대로"
json.dump(tl, open(f"{L}/타임라인_v6.json", "w"), ensure_ascii=False, indent=1)
json.dump(ch, open(f"{H}/v6_changes.json", "w"), ensure_ascii=False, indent=1)
for c in ch: print(c["i"], c["slide"], " / ".join(c["old"]), "→", " / ".join(c["new"]), [round(t, 3) for t in c["st"]], c["how"])
