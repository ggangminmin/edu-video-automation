# 08강 v3 타임라인(오더 51 토막 카드) = v2 subs 나눔만 바꿈 · 소리·장·아나운서 그대로
# 새 나눔 자리 첫 어절 = mlxwords(받아쓰기) 위치를 기준점으로 깨끗한 음성 5ms RMS 실소리(newline_onset_check 와 같은 onset()) − 0.09
import json, re, subprocess, numpy as np, copy, sys
tl = json.load(open("../../타임라인_v2.json")); S = tl["subs"]
# (묶음 첫 줄 번호(0기준), 새 카드들, 방식)
PLAN = [
 ([3,4,5], ["8강에서는 일자와 헤링본 등 다양한 시공 패턴의 특징을 알아보고,", "패턴을 선택할 때 고려할 사항을 살펴봅니다"], "고르게 2장(앞 36자 · 폭 1247px · 팀장 결정)"),
 ([34,35], ["시공자는 패턴과 함께 실제 공간에서", "달라지는 조건을 설명해야 합니다"], "고르게 2장"),
 ([36,37], ["헤링본은 직사각형 판의 끝과 옆이 엇물려 지그재그 무늬를 만듭니다"], "한 장 합침(팀장 결정: 한 장 36자 · 폭 1294px)"),
 ([40,41,42], ["쉐브론의 절단 각도는 제품에 따라 달라지니 한 각도로 단정하지 말고", "전용 자재의 형상을 확인합니다"], "3장→고르게 2장(앞 37자 · 폭 1304px · 팀장 결정)"),
 ([61,62], ["실제 평면 위에 놓고 출입구에서 보이는 중심과", "벽 주변 마감을 살핍니다"], "고르게 2장"),
 ([63,64], ["제품의 좌우 구분, 규격, 납기와 시공 지침을 읽은 뒤", "자재량, 비용, 기간을 설명합니다"], "고르게 2장"),
 ([72,73], ["초기에 조금 틀어진 방향도 여러 줄을 시공하면 크게 벌어질 수 있죠"], "한 장 합침(팀장 결정: 한 장 37자 · 폭 1270px)"),
 ([77,78], ["고객이 균일한 리듬을 원하는지", "자연스러운 분포를 원하는지도 샘플과 자료로 확인합니다"], "고르게 2장(한 장 폭 1692px>1500 · 팀장 결정: 연결어미(검사기 미등록) 「원하는지 /」)"),
 ([81,82], ["시공 중에는 처음 합의한 흐름이 유지되는지 전체를 한 번씩 살펴봅니다"], "한 장 합침(팀장 결정: 한 장 38자 · 폭 1348px)"),
 ([85,86], ["전체를 보는 시선과 이음부를 보는 시선을", "번갈아 사용하는 것이 패턴 검토에 도움이 됩니다"], "고르게 2장(한 장 49자>1500px · 팀장 결정: 목적어 뒤 부사어 「시선을 / 번갈아」)"),
 ([109,110], ["사진 속 분위기와 실제로 설치할 제품의 결합 구조를", "같은 정보로 취급하지 않습니다"], "고르게 2장(한 장 폭 1585px>1500 · 팀장 결정: 목적어 뒤 부사어 「구조를 / 같은 정보로」)"),
 ([130,131], ["외관과 자재 소요, 실제 작업을 함께 비교하면", "대안의 차이를 설명하기 쉽습니다"], "고르게 2장"),
 ([139,140], ["색과 규격, 패턴이 함께 바뀌는 경우에는", "각각의 변경을 확인합니다"], "고르게 2장"),
 ([189,190], ["사선(대각선) 시공은 넓어 보이는 효과가 있어 좁은 공간·현관에 많이 씁니다"], "한 장 합침(팀장 결정: 한 장 42자 · 폭 1455px)"),
 ([203,204], ["두 패턴은 멀리서 비슷해 보여도 이음부를 가까이 보면 구별하기 쉽습니다"], "한 장 합침(팀장 결정: 한 장 39자 · 폭 1390px)"),
 ([220,221], ["판의 모양, 결합, 공간 형상에 따라 자재 소요와 작업도 달라집니다"], "한 장 합침(팀장 결정: 한 장 37자 · 폭 1246px · 끝인사)"),
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
