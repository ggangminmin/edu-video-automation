# 07강 v3 타임라인(오더 51 토막 카드) = v2 subs 나눔만 바꿈 · 소리·장·아나운서 그대로
# 새 나눔 자리 첫 어절 = mlxwords(받아쓰기) 위치를 기준점으로 깨끗한 음성 5ms RMS 실소리(newline_onset_check 와 같은 onset()) − 0.09
import json, re, subprocess, numpy as np, copy, sys
tl = json.load(open("../../타임라인_v2.json")); S = tl["subs"]
# (묶음 첫 줄 번호(0기준), 새 카드들, 방식)
PLAN = [
 ([7,8], ["오늘은 단면을 보면서 두 방식이 어떻게 작동하는지 비교해 보겠습니다"], "한 장 합침(팀장 결정: 한 장 37자 · 폭 1337px)"),
 ([30,31,32], ["표면에 막이 생겼거나 작업 가능 시간이 지난 재료를 그대로 사용하면", "적절한 접촉이 이루어지지 않을 수 있습니다"], "3장→고르게 2장(앞 37자 · 폭 1301px · 팀장 결정)"),
 ([50,51], ["부유식은 판끼리 결합한 바닥층을 바탕에 직접 붙이지 않고 놓는 방식입니다"], "한 장 합침(팀장 결정: 한 장 40자 · 폭 1434px)"),
 ([52,53], ["교재는 벽 주변에 십에서 십이 밀리미터의 신축 유격선을 두도록 설명합니다"], "한 장 합침(팀장 결정: 한 장 40자 · 폭 1433px · v2 예외 #2 없어짐)"),
 ([60,61,62], ["교재의 방습 비닐은 이음부를 겹쳐 밀봉하지만,", "완충재는 겹침으로 높이 차이가 생기지 않게 하는 점을 구별해 주세요"], "3장→고르게 2장(뒤 37자 · 폭 1303px · 팀장 결정)"),
 ([70,71,72], ["접착제가 없으니 바로 깔면 된다는 판단 대신,", "결합 순서와 경계부, 연속 시공 가능 범위, 가구와의 관계를 확인합니다"], "3장→고르게 2장(뒤 39자 · 폭 1331px · 팀장 결정)"),
 ([95,96], ["접착과 결합 구조는 뒤에서 하자 원인을 조사할 때도 살펴보게 됩니다"], "한 장 합침(팀장 결정: 한 장 37자 · 폭 1304px)"),
 ([124,125], ["복도와 방이 이어지면 바닥층이 움직이는 범위와 경계를 함께 봐야 합니다"], "한 장 합침(팀장 결정: 한 장 39자 · 폭 1389px · 「범위와 / 경계를」 짝 갈림 피함)"),
 ([143,144], ["고객의 우선순위를 적고 그 요구를 어느 범위에서", "충족할 수 있는지 자료와 연결하세요"], "고르게 2장(한 장 폭 1625px>1500 · 「적고 /」 10/25 쏠림 · 팀장 결정: 부사어 「범위에서 /」)"),
 ([147,148], ["구역별 접착 작업은 도포하는 사람과 설치하는 사람의 속도를 맞춰야 합니다"], "한 장 합침(팀장 결정: 한 장 40자 · 폭 1433px · 「사람과 / 설치하는 사람」 짝 갈림 피함)"),
 ([152,153], ["이미 시간이 지난 접착층은 덧바르기로 해결하려 하지 말고", "제품 절차에 따라 처리합니다"], "고르게 2장(연결어미 「말고 /」)"),
 ([154,155], ["빨리 끝내기 위해 필요한 확인을 줄이는 것은 시간 관리가 아닙니다"], "한 장 합침(팀장 결정: 한 장 36자 · 폭 1260px)"),
 ([232,233], ["공법을 고른 뒤에는 마루, 바탕, 부자재, 경계부가 함께 맞는지 살펴야 합니다"], "한 장 합침(팀장 결정: 한 장 43자 · 폭 1442px · 끝인사 · 나열 갈림 피함)"),
 ([235,236], ["8강에서는 같은 자재를 어떤 방향과 배열로 놓을지 패턴을 비교하겠습니다"], "한 장 합침(팀장 결정: 한 장 39자 · 폭 1409px · 끝인사 · 「방향과 / 배열로」 짝 갈림 피함)"),
]
# ---- 깨끗한 음성 + db (newline_onset_check 와 같음)
SR, H = 16000, 80; FR = SR / H; TH, RUN, GAP, SHALLOW, VWIN = -50.0, 6, 6, -45.0, 0.15
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32)
cache = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for a in tl["audio"]:
    k = a.get("src"); f = "../v090.wav" if k is None else "../" + k.replace("work/", "")
    if f not in cache: cache[f] = load(f)
    y = cache[f][int(a["src_from"]*SR):int(a["src_to"]*SR)] * float(a.get("gain",1.0)); o = int(round(a["out"]*SR)); V[o:o+len(y)] += y[:max(0,len(V)-o)]
db = 20*np.log10(np.sqrt(np.mean(V[:len(V)//H*H].reshape(-1,H)**2,1))+1e-9)
def onset(ref):
    i0, i1 = max(0,int((ref-0.3)*FR)), min(len(db)-RUN,int((ref+0.3)*FR)); seg = db[i0:i1]; runs=[]; j=0
    while j < len(seg):
        if seg[j] < TH:
            k=j
            while k < len(seg) and seg[k] < TH: k+=1
            if k-j >= GAP: runs.append((i0+j,i0+k))
            j=k
        else: j+=1
    if runs:
        s_,e_ = min(runs,key=lambda r: abs(r[1]/FR-ref)); m=e_
        while m < len(db)-RUN and not all(db[m:m+RUN] > TH): m+=1
        return m/FR, "쉼"
    v0,v1 = max(3,int((ref-VWIN)*FR)), min(len(db)-4,int((ref+VWIN)*FR))
    vs=[m for m in range(v0,v1) if db[m] <= SHALLOW and db[m]==db[m-3:m+4].min()]
    if not vs: return None, "이어진 말"
    m=min(vs,key=lambda m: abs(m/FR-ref)); return m/FR, "골짜기"
# ---- 받아쓰기 단어(출력 시각)
W = json.load(open("../mlxwords.json"))
def src2out(t):
    for a in tl["audio"]:
        if a.get("src") is None and a["src_from"] - 1e-6 <= t <= a["src_to"] + 1e-6: return a["out"] + t - a["src_from"]
words = [(src2out(w[0]), w[2].strip()) for w in W]; words = [w for w in words if w[0] is not None]
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
MAN = json.load(open("onset_man_v3.json")) if __import__("os").path.exists("onset_man_v3.json") else {}
rep = []; new = []; k = 0; plan = {g[0]: (g, c, h) for g, c, h in PLAN}
i = 0
while i < len(S):
    if i not in plan: new.append(copy.deepcopy(S[i])); i += 1; continue
    g, cards, how = plan[i]; old = [S[j] for j in g]
    assert " ".join(x["text"] for x in old).split() == " ".join(cards).split(), (g, "글자 다름")
    t0, t1 = old[0]["start"], old[-1]["end"]
    out = []
    for ci, txt in enumerate(cards):
        x = copy.deepcopy(old[0]) if ci == 0 else {k_: v for k_, v in old[0].items() if k_ in ("slide", "part")}
        x["text"] = txt
        if ci > 0:
            same = [o for o in old[1:] if o["text"].split()[0] == txt.split()[0] and " ".join(cards[ci:]).startswith(o["text"].split(" ")[0])]
            # 앞 판에도 이 자리에서 나뉘었으면 그 시각 그대로
            prevtxt = " ".join(cards[:ci]).split(); cum = 0; hit = None
            for o in old:
                if cum == len(prevtxt): hit = o; break
                cum += len(o["text"].split())
            if hit is not None and hit is not old[0]:
                x["start"], x["voice_on"], x["how"] = hit["start"], hit["voice_on"], hit.get("how", "앞 판 그대로")
                rep.append(dict(n=old[0]["n"], text=txt, src="앞 판 같은 자리", start=hit["start"]))
            else:
                w0 = kn(txt.split()[0]); cand = [w for w in words if t0 <= w[0] <= t1 + 0.3 and kn(w[1]).startswith(w0[:2])]
                assert cand, (txt, "받아쓰기 단어 못 찾음")
                ref = cand[0][0]
                if txt in MAN: on, oh = MAN[txt], "손 실측"
                else: on, oh = onset(ref)
                if on is None: on = ref; oh = "이어진 말→받아쓰기 기준(확인 필요)"
                x["start"] = on - 0.09; x["voice_on"] = round(on, 3); x["how"] = f"v3 나눔 실소리({oh})−0.09"
                rep.append(dict(n=old[0]["n"], text=txt, asr=round(ref, 3), onset=round(on, 3), how=oh, start=round(on - 0.09, 3)))
        out.append(x)
    for ci, x in enumerate(out): x["end"] = out[ci + 1]["start"] if ci + 1 < len(out) else t1
    out[0]["v3"] = how
    new.extend(out); i = g[-1] + 1
for n_, x in enumerate(new, 1): x["n"] = n_
tl["subs"] = new
json.dump(tl, open("../../타임라인_v3.json", "w"), ensure_ascii=False, indent=1)
json.dump(rep, open("onset_v3.json", "w"), ensure_ascii=False, indent=1)
for r in rep: print(r)
print("subs", len(S), "→", len(new))
