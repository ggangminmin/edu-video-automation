# 오더15-2 검산: 클립·타입캐스트가 「둘 다 쉬는」 자리(anchor_words.py 짝)마다 쉼 시작·끝의 입 시각 − 소리 시각(출력 기준, 기준 0.1초)
#  onsetcheck 은 한쪽에만 있는 쉼도 가장 가까운 것과 짝지어 재므로, 입이 멈출 수 없는 자리(대본 말 이어짐)까지 오차로 셈 → 이걸로 구분
import sys, json, numpy as np
cw, tw, wj, aj = sys.argv[1:5]
info = json.load(open(wj)); cs = info["clip_speech"][0]; ts = info["target_speech"][0]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
d = json.loads(open(aj).read().splitlines()[1])
errs = []
for p in d["pairs"]:
    for i, nm in ((0, "시작"), (1, "끝")):
        u_mouth = cs + float(np.interp(p["c"][i] - cs, cl, tau)); u_voice = cs + (p["t"][i] - ts)
        errs.append((p["at"], nm, round(u_mouth - u_voice, 3)))
e = np.abs([x[2] for x in errs]) if errs else np.array([0.0])
res = dict(n=len(errs), median=round(float(np.median(e)), 3), max=round(float(e.max()), 3), over=[x for x in errs if abs(x[2]) > 0.1],
           only_target=d["only_target"], only_clip=d["only_clip"])
json.dump(res, open(wj.replace(".json", "_pause.json"), "w"), ensure_ascii=False, indent=1)
print(wj.split("/")[-1], {k: res[k] for k in ("n", "median", "max", "over")}, "| 타깃만 쉼", len(d["only_target"]), "· 클립만 쉼", len(d["only_clip"]))
