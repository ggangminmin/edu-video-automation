# 오더15-2: 쉼 고정점을 「대본의 같은 글자 자리」 쉼끼리만 짝(11강 입싱크_방식.md 2번 — 어느 단어 앞 쉼인지 받아쓰기로 확인)
#  쉼(−40dB ≥0.08초) 위치 = 그 쉼 앞에 끝난 글자 수(받아쓰기 글자열 기준) → 클립·타깃 글자열을 글자 단위로 맞춰
#  같은 글자 자리(±2자)의 쉼이면 짝 → 쉼 시작끼리·끝끼리 고정점. 한쪽에만 있는 쉼 = 입이 거기서 멈출 수 없는 곳(원인 목록).
#  실행: python3 anchor_words.py <clip.wav> <target.wav> <warp.json> → 1줄 고정점 · 2줄 JSON(짝/한쪽만)
import sys, json, re, difflib, subprocess
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
def sil(p, a, b):
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [(s, e) for s, e in zip(map(float, re.findall(r"silence_start: ([\d.]+)", o)), map(float, re.findall(r"silence_end: ([\d.]+)", o))) if a + 0.05 < s and e < b - 0.05]
def chars(p):
    W = json.load(open(p.replace(".wav", "_words.json")))["words"]; s = ""; mids = []
    for w, a, b in W:
        t = re.sub(r"[^가-힣0-9]", "", w)
        if t: mids.append((len(s), (a + b) / 2, a)); s += t
    return s, mids
def pos(mids, t):                                           # t 앞에 가운데가 있는 단어들의 글자 수
    p = 0
    for i, (k, m, _) in enumerate(mids):
        if m < t: p = mids[i + 1][0] if i + 1 < len(mids) else 10 ** 6
    return p
sC, mC = chars(cw); sT, mT = chars(tw)
SC, ST = sil(cw, cs, ce), sil(tw, ts, te)
blk = difflib.SequenceMatcher(None, sT, sC, autojunk=False).get_matching_blocks()
def t2c(p):
    for a, b, n in blk:
        if a <= p <= a + n: return b + (p - a)
    return None
def c2t(p):
    for a, b, n in blk:
        if b <= p <= b + n: return a + (p - b)
    return None
def word_on(mids, S, p):                                  # 글자 자리 p 에서 시작하는 단어의 소리 시작(쉼 안이면 쉼 끝)
    c = [a for k, m, a in mids if k == p]
    if not c: return None
    a = c[0]
    for s0, e0 in S:
        if s0 - 0.02 <= a < e0: a = e0
    return a
def merge(S, mids):                                     # 같은 글자 자리(±1자) 쉼 여러 개 = 한 쉼(첫 시작 ~ 끝 끝) — 18강 「방법과 | 개인」 타입캐스트 쉼 2번
    out = []
    for s, e in S:
        p = pos(mids, (s + e) / 2)
        if out and abs(out[-1][0] - p) <= 1: out[-1] = (out[-1][0], out[-1][1], e)
        else: out.append((p, s, e))
    return out
PC = merge(SC, mC)
pairs, onlyT, used = [], [], set()
for p, s, e in merge(ST, mT):
    q = t2c(p); ctx = sT[max(0, p - 4):p] + "|" + sT[p:p + 4]
    c = [x for x in PC if q is not None and abs(x[0] - q) <= 2 and x not in used]
    if not c: onlyT.append(dict(t=[round(s, 2), round(e, 2)], at=ctx, why="클립은 여기서 안 쉼(말 이어짐)")); continue
    x = min(c, key=lambda x: abs(x[0] - q)); used.add(x)
    pairs.append(dict(c=[round(x[1], 3), round(x[2], 3)], t=[round(s, 3), round(e, 3)], at=ctx))
onlyC = [dict(c=[round(s, 2), round(e, 2)], at=sC[max(0, p - 4):p] + "|" + sC[p:p + 4], why="타입캐스트는 여기서 안 쉼") for p, s, e in PC if (p, s, e) not in used]
anc = {(x["c"][0], x["t"][0]) for x in pairs} | {(x["c"][1], x["t"][1]) for x in pairs}
one = []                                                  # 한쪽만 쉼: 클립만 → 그 쉼을 타깃 다음 말 시작 둘레 0.06초로 지나감 · 타깃만 → 클립 다음 말 시작 둘레 0.06초를 타깃 쉼 내내 늘림
import os
ONE = os.environ.get("ONE", "1") == "1"                 # ONE=0 → 한쪽만 쉼 고정점 안 넣음(11강 문서: 한쪽에만 있는 쉼은 빼기)
for x in (onlyC if ONE else []):
    p = [q for q, s0, e0 in PC if round(s0, 2) == x["c"][0]][0]; tp = c2t(p); ton = word_on(mT, ST, tp) if tp is not None else None
    if ton: anc |= {(x["c"][0], round(ton - 0.04, 3)), (x["c"][1], round(ton + 0.02, 3))}; one.append(("클립만", x["at"], x["c"], round(ton, 3)))
for x in (onlyT if ONE else []):
    p = [q for q, s0, e0 in merge(ST, mT) if round(s0, 2) == x["t"][0]][0]; cp = t2c(p); con = word_on(mC, SC, cp) if cp is not None else None
    if con: anc |= {(round(con - 0.04, 3), x["t"][0]), (round(con + 0.02, 3), x["t"][1])}; one.append(("타깃만", x["at"], x["t"], round(con, 3)))
anc = sorted(anc); ok = []
for c, t in anc:
    if not ok or (c > ok[-1][0] + 0.01 and t > ok[-1][1] + 0.01): ok.append((c, t))
print(",".join(f"{c}:{t}" for c, t in ok)); print(json.dumps(dict(pairs=pairs, only_target=onlyT, only_clip=onlyC, one_side=one), ensure_ascii=False))
