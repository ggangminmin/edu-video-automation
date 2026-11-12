#!/usr/bin/env python3
"""자막 줄 나눔 검사기 (오더25 · 지적 #10~12 · 2026-11-03 12강수정)

한 문장이 두 줄 이상으로 나뉠 때, 앞 줄 끝은 **연결어미·쉼표 뒤**에서만 끊는다.
  허용 = 쉼표 · 나열 -와/-과(「기능과 / 시공 시스템의」, 같은 말 짝 「마루와 / 마루를」은 위반) · 주제어 -은/-는(「검수는」「사용 조건은」 · 관형형 「가리는」「좋은」은 위반) 뒤 · 명사절 「~것과·~것은」 뒤 · -어/-아 연결(남겨·맞춰·나눠, 뒤가 보조용언이면 위반) · 부사어+는(-에는·-에서는, 팀장 확인용 추가) · -고 · -며 · -면(-다면·-려면) · -서 · -야 · -지만 · -데(-는데·-은데·-인데) · -(으)로 · -도록 · -거나 · -므로 · -니까
         · -면서 · -어도/-아도/-해도/-라도 · ~할 때(는/도) · ~한 뒤/후(에) · ~전에
  🆕11/3 #16 허용 추가 = 나열 중간점(·) 뒤(「기본 정보·사용 자재·시공 방법· / 환경 측정값·사진 등을…」).
  예외 = 표지 인삿말 「…온라인 강의 / 제NN강에…」(팀장 결정 11/3, 11~20강 공통).
  위반 = 그 밖 전부. 이유 표시: 관형형(-ㄹ·-는·-은·-ㄴ) · 목적어(-을/-를) · 소유(-의) · 의존명사로 시작(때·수·것·데·뿐·만큼·줄·듯) · 명사/주어 뒤
검사 대상 = 같은 장(slide) 안에서 앞 줄이 문장 끝(다·요·죠·?·!·.·까)으로 안 끝난 이음. 확인문제 보기(「일 번, …」)끼리는 제외.

쓰는 법:
  python3 line_break_check.py 12 --timeline ../../12강/타임라인_v4.json      # 한 강 (0 = 통과)
  python3 line_break_check.py all                                          # 11~20강 각 최신 타임라인 표
종료 코드 = 위반 수(최대 255). --json <파일> 로 목록 저장.
"""
import json, re, sys, os, glob, argparse

TERM = re.compile(r"(다|요|죠|까|\?|!|\.)$")
QUIZ = re.compile(r"^[일이삼사오육칠팔구]\s*번\s*,")
# 🆕11/3 팀장(16강 p1Q 「가려도 /」): 양보 연결어미 = -어도/-아도/-해도/-라도(-더라도) + 줄어든 꼴 -려도·-겨도·-혀도·-셔도·-쳐도·-져도·-켜도·-펴도·-워도·-줘도·-둬도·-봐도·-돼도·-써도·-커도 + -ㄴ데도/-는데도
#  (-여도·-가도·-와도 는 뺌: 참여도·기여도 / 평가도 / 마루와도 = 명사+도)
OK_END = re.compile(r"(고|며|면|서|야|지만|데|로|도록|거나|므로|니까|면서|어도|아도|해도|라도|려도|겨도|혀도|셔도|쳐도|져도|켜도|펴도|워도|줘도|둬도|봐도|돼도|써도|커도|데도|때|때는|때도|뒤|뒤에|후|후에|전에|뒤로|에는|에서는|것과|것은|것이|것도)$")
DEP_START = re.compile(r"^(때|수|것|데|뿐|만큼|줄|듯)(\s|$|[은는이가을를도에의])")
HANGUL = re.compile(r"[가-힣]")
EO_END = re.compile(r"(겨|춰|눠|쳐|져|켜|펴|워|해|돼|봐)$")            # -어/-아 연결(남겨·맞춰·나눠·검토해)
EO_WORDS = {"가져와", "막아", "나와", "들어", "넣어", "덮어", "붙여", "잡아", "닦아", "깎아"}
NOT_RO = {"서로", "따로"}                                             # -로 처럼 보이지만 부사
AUX_AFTER_EO = re.compile(r"^(보(다|고|면|세요|며|니|았|아)|봐|봅|볼|본|주(다|고|세요|며|면)|줍|줄|준|있|두|둡|놓|버리|내(다|고)|냅)")
AUX_AFTER_YA = re.compile(r"^(하|합|할|한|해|했|됩|된|될|되)")
AUX_AFTER_GO = re.compile(r"^있")
VERBISH = set("하되있없않이지보쓰가오리르내주두우히기치키시드나맞려추켜펴러터저져춰워봐해돼")
STEM_EUN = set("같좋많넓높낮짧얇깊굵맑밝늦싫놓넣덮닫받찍잡붙묻얹앉꽂깎씻읽먹굳젖있없않맞낡옅옳찮갖걷곧믿빚솟얻잃잊좁짙찾쌓섞썩싣묶볶꺾벗웃씹뽑엎닮굶젊옮앓긁끓뚫핥훑")   # 명사 끝에도 흔한 글자(마감·동작·작업·제품·방식…)는 뺌 · 2글자 형용사(좋은·작은)는 len≥3 에서 이미 빠짐
TOPIC2 = {"곳은", "것은", "면은", "문은", "벽은", "틈은", "끝은", "선은", "판은", "방은", "못은", "홈은", "결은", "땐", "때는"}
WAGWA = re.compile(r"[가-힣]{2,}(와|과)$")                          # 명사 나열 -와/-과 (「기능과 / 시공 시스템의」)

def jong(ch):
    o = ord(ch) - 0xAC00
    return o % 28 if 0 <= o < 11172 else -1

# 🆕11/3 팀장(11강 p1T 발견): ① 「-면」 = 앞 글자가 용언 어간(VERBISH·-다/-려/-으/-았… · ㄹ 받침)일 때만 연결어미 — 평면·측면·표면·단면·정면·벽면·디딤면 등 명사 「-면」은 아님
#  ② 숫자 범위 「십에서 / 십오」「10에서 / 15」 = 숫자 사이는 끊지 않음(-에서 를 연결어미 -서 로 읽던 구멍)
#  판정: 용언은 받침 있는 어간 뒤에 「-으면」이 붙으므로 「-면」 바로 앞 글자에 받침(ㄹ·ㅆ 빼고)이 있으면 명사(평·측·단·정·벽·딤·닥…)
#        받침 없는 앞 글자 중 명사 「-면」 = 표면·도면·후면·화면·수면·(경)사면 만 따로 뺌(지면은 「-지면」 동사가 더 흔해 뺌)
MYEON_NOUN_OPEN = set("표도후화수사")   # 「지」 뺌 = 느껴지면·떨어지면
def myeon_conn(w):
    if len(w) < 2 or not w.endswith("면"): return False
    c = w[-2]; j = jong(c)
    if j < 0: return False
    if j == 0: return c not in MYEON_NOUN_OPEN
    return j in (8, 20)                                  # ㄹ(길면·만들면) · ㅆ(했으면 아님 — 「았/었/겠」+면 드묾, 안전하게 허용)
NUMW = re.compile(r"^(\d+|[영일이삼사오육칠팔구십백천만]+)$")
NUM0 = re.compile(r"^(\d|[영일이삼사오육칠팔구십백천만])")

def reason(prev, nxt, part=None):
    """앞 줄 마지막 어절 · 뒤 줄 첫 어절 → (위반 여부, 이유)"""
    p = prev.rstrip()
    n = nxt.lstrip()
    if part == "인삿말" and p.endswith("강의") and re.match(r"^제\s*\d+\s*강", n):
        return False, "예외: 인삿말 명사구 동격(팀장 결정 11/3 — 「강의 / 제NN강」은 덩어리 경계, 「안녕하세요,」 뒤는 0.4초 깜빡임+39자)"
    if DEP_START.match(n):
        return True, "의존명사로 시작(" + n.split()[0] + ")"
    if p.endswith(",") or p.endswith("，"):
        return False, "쉼표"
    if p.endswith("·"):                                    # 🆕11/3 지적 #16(팀장): 「…시공 방법· / 환경 측정값…」 나열 중간점 뒤
        return False, "나열 중간점(·) 뒤"
    w = p.split()[-1].rstrip(".,")
    n0 = n.split()[0] if n.split() else ""
    if w.endswith(("에서", "부터")) and NUMW.match(w[:-2]) and NUM0.match(n0):
        return True, "숫자 범위(「" + w + " / " + n0 + "」) 갈림"
    if w.endswith("면") and not myeon_conn(w) and not w.endswith(","):
        return True, "명사 「-면」(" + w + ") 뒤 — 연결어미 -면 아님"
    if w.endswith("야") and AUX_AFTER_YA.match(n0):
        return True, "-야 하다(보조용언) 갈림"
    if w.endswith("고") and AUX_AFTER_GO.match(n0):
        return True, "-고 있다(보조용언) 갈림"
    if (EO_END.search(w) or w in EO_WORDS) and AUX_AFTER_EO.match(n0):
        return True, "-어 보다/주다/있다(보조용언) 갈림"
    if w in NOT_RO:
        return True, "부사(" + w + ")와 꾸밈받는 말 갈림"
    if EO_END.search(w) or w in EO_WORDS:
        return False, "연결어미(-어/-아)"
    # 🆕오더25 연장(cx 지적 「똑같은 / 조건」「골라놓은 / 제품」): 형태소 분석기 없음(kiwipiepy·konlpy 미설치, 설치 안 함) → 규칙
    #  -은: 앞 글자가 용언 어간(STEM_EUN) 이거나 ㅎ 받침(놓·좋·넣·않·많·괜찮)이면 관형형 → 주제어 아님
    #  -는: 앞 글자 받침 없음 + 용언 어간 끝 글자(VERBISH) 아님 일 때만 주제어(받침 + 는 = 「먹는·받는」 관형형)
    topic = (w in TOPIC2) or \
            (w.endswith("은") and len(w) >= 3 and jong(w[-2]) > 0 and jong(w[-2]) != 27 and w[-2] not in STEM_EUN) or \
            (w.endswith("는") and len(w) >= 3 and jong(w[-2]) == 0 and w[-2] not in VERBISH)
    if w.endswith(("다는", "라는", "냐는", "려는", "다던", "라던")):   # 인용·의도 관형형(「반복된다는 관찰」「저독성이라는 설명」)
        topic = False
    if topic:
        return False, "주제어(-은/-는) 뒤"
    if WAGWA.search(w) and not (n0[:len(w) - 1] == w[:-1]):   # 「마루와 / 마루를」 처럼 같은 말 짝이 갈리면 위반
        return False, "나열 -와/-과 뒤"
    if OK_END.search(w):
        return False, "연결어미(" + OK_END.search(w).group(1) + ")"
    if w.endswith(("을", "를")):
        return True, "목적어(-을/-를)와 서술어 갈림"
    if w.endswith("의") and w not in ("강의", "회의", "주의", "정의", "합의"):
        return True, "소유(-의)와 꾸밈받는 말 갈림"
    last = [c for c in w if HANGUL.match(c)]
    if last:
        c = last[-1]
        if c in ("는", "은", "던", "던") or jong(c) == 8:   # 8 = ㄹ 받침(-ㄹ 관형형·「할」「될」)
            return True, "관형형/꾸밈말과 꾸밈받는 말 갈림"
        if jong(c) == 4:                                      # 4 = ㄴ 받침(「다른」「비슷한」 등 · 명사도 걸림)
            return True, "관형형(-ㄴ)/명사 뒤"
    return True, "명사/주어 뒤(연결어미·쉼표 아님)"

def breaks(tl):
    """검사 대상 이음 목록"""
    S = tl["subs"]; out = []
    for i in range(len(S) - 1):
        a, b = S[i], S[i + 1]
        if a.get("slide") != b.get("slide"):
            continue
        if a.get("part") != b.get("part"):
            continue
        ta, tb = a["text"].strip(), b["text"].strip()
        if TERM.search(ta):
            continue
        if QUIZ.match(tb) or QUIZ.match(ta):
            continue
        bad, why = reason(ta, tb, a.get("part"))
        out.append({"i": i, "n": a.get("n"), "n_next": b.get("n"), "slide": a.get("slide"), "time": round(b["start"], 3),
                    "mmss": f"{int(b['start'] // 60)}:{b['start'] % 60:05.2f}", "prev_end": ta.split()[-1], "next_start": tb.split()[0],
                    "prev": ta, "next": tb, "bad": bad, "why": why})
    return out

def latest(n):
    d = os.path.join(os.path.dirname(__file__), "..", "..", f"{n}강")
    fs = [f for f in glob.glob(os.path.join(d, "타임라인_v*.json")) if "렌더판" not in f and "때" not in os.path.basename(f)]
    def key(f):
        m = re.search(r"_v(\d+)([a-z]?)\.json$", f)
        return (int(m.group(1)), m.group(2)) if m else (0, "")
    fs = [f for f in fs if re.search(r"_v\d+[a-z]?\.json$", f)]
    return max(fs, key=key) if fs else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lec"); ap.add_argument("--timeline"); ap.add_argument("--json"); ap.add_argument("--show-ok", action="store_true")
    a = ap.parse_args()
    if a.lec == "all":
        rows = []; total = 0
        print("| 강 | 타임라인 | 이음(문장 안 줄 나눔) | 위반 | 예(앞 줄 끝 / 뒤 줄 시작 · 시각) |\n|---|---|---|---|---|")
        for n in range(11, 21):
            f = latest(n)
            if not f:
                print(f"| {n} | 없음 | | | |"); continue
            br = breaks(json.load(open(f))); bad = [x for x in br if x["bad"]]; total += len(bad)
            ex = " · ".join(f"「{x['prev_end']}/{x['next_start']}」{x['mmss']}" for x in bad[:3])
            print(f"| {n} | {os.path.basename(f)} | {len(br)} | {len(bad)} | {ex} |")
            rows.append({"lec": n, "timeline": f, "breaks": len(br), "bad": bad})
        print(f"\n합계 위반 {total}")
        if a.json: json.dump(rows, open(a.json, "w"), ensure_ascii=False, indent=1)
        return 0
    f = a.timeline or latest(int(a.lec))
    br = breaks(json.load(open(f))); bad = [x for x in br if x["bad"]]
    print(f"{a.lec}강 {os.path.basename(f)} — 문장 안 줄 나눔 {len(br)}곳 · 위반 {len(bad)}")
    for x in (br if a.show_ok else bad):
        print(f"  {'✗' if x['bad'] else '○'} 줄{x['n']}→{x['n_next']} 장{x['slide']} {x['mmss']} 「…{x['prev'][-16:]}」/「{x['next'][:16]}…」 — {x['why']}")
    if a.json: json.dump(bad, open(a.json, "w"), ensure_ascii=False, indent=1)
    return min(len(bad), 255)

if __name__ == "__main__":
    sys.exit(main())
