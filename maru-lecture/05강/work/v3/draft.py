# 계획대로 나눔만 바꾼 초안(시각 = 글자 비율 임시) → line_break · short_card 확인용
import json, sys; sys.path.insert(0, "v3"); from plan import MERGE, SPLIT
tl = json.load(open("../타임라인_v2.json")); S = tl["subs"]; new = []; i = 0
while i < len(S):
    x = S[i]
    if i in MERGE:
        y = S[i+1]; m = dict(x); m["text"] = x["text"] + " " + y["text"]; m["end"] = y["end"]; new.append(m); i += 2; continue
    if i in SPLIT:
        y = S[i+1]; full = x["text"] + " " + y["text"]; a = SPLIT[i]; assert full.startswith(a + " "), i; b = full[len(a)+1:]
        t = x["start"] + (y["end"] - x["start"]) * len(a) / len(full)
        x2 = dict(x, text=a, end=t); y2 = dict(y, text=b, start=t); new += [x2, y2]; i += 2; continue
    new.append(x); i += 1
for k, x in enumerate(new): x["n"] = k + 1
tl["subs"] = new; json.dump(tl, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
