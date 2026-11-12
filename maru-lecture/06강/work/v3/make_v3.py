# 06강 v3(오더51 토막 자막 · 팀장 11/9 확정 기준): 타임라인_v2 → 타임라인_v3. 자막 나눔·시각만(subs) · 그 밖 키 v2 그대로
#  MERGE = 두 장 → 한 장(첫 장 시작 · 둘째 장 끝 · 첫 장 voice_on) · SPLIT = 새 나눔(둘째 장 시작 = 첫 어절 실소리 −0.09)
#  실소리 = 깨끗한 음성 5ms RMS(−50dB 쉼 끝 · 상승) + 쉼 사이 조각 받아쓰기 + 앞 창(앞말 끝까지)·뒤 창(v3/probe2~4.txt)
import json
tl = json.load(open("../타임라인_v2.json")); S = tl["subs"]
MERGE = {18: "한 장 41자 1476px(자연스러운 자리 없음)", 23: "두 장(「아니고, /」 v2 경계 그대로)", 132: "한 장 37자 1369px", 149: "한 장 36자 1235px(나열 안 가름)",
         151: "한 장 37자 1336px", 176: "두 장(「이므로 /」 v2 경계 그대로)", 198: "한 장 38자 1353px(확인문제)", 223: "한 장 36자 1260px(끝인사)"}
SPLIT = {81: ("홍보 문구를 검토할 때는 제품 자료가", 341.250, "팀장 결정: 주어 뒤(line_break 1)"),
         93: ("자료마다 내용이 다르면 개정 정보와 적용 범위를 확인하고", 390.315, "고르게 24/12 「-고」"),
         119: ("마루 위에서 나는 느낌과 아래층에 전달되는 소음도", 508.255, "팀장 결정: 주어 뒤(line_break 1)"),
         144: ("자료 목록에는 어떤 제품의 어떤 항목을 확인하는 문서인지", 612.665, "팀장 결정: 「-는지」 연결어미(검사기 미등록)")}
new = []; i = 0
while i < len(S):
    x = S[i]
    if i in MERGE:
        y = S[i + 1]; m = dict(x); m["text"] = x["text"] + " " + y["text"]; m["end"] = y["end"]; m["v3"] = f"합침(v2 #{i}+#{i+1}) · {MERGE[i]}"
        new.append(m); i += 2; continue
    if i in SPLIT:
        y = S[i + 1]; full = x["text"] + " " + y["text"]; a, on, why = SPLIT[i]; assert full.startswith(a + " "), i; b = full[len(a) + 1:]
        ns = round(on - 0.09, 3); assert x["start"] < ns < y["end"]
        x2 = dict(x); y2 = dict(y); x2["text"] = a; y2["text"] = b; x2["end"] = ns; y2["start"] = ns; y2["voice_on"] = on
        y2["how"] = "v3 실소리 −0.09(5ms RMS + 쉼 조각 받아쓰기 · 받아쓰기 단어 시각은 0.4~0.55 이름)"
        x2["v3"] = y2["v3"] = f"다시 나눔(v2 #{i}/#{i+1}) · {why}"
        new += [x2, y2]; i += 2; continue
    new.append(x); i += 1
tl["subs"] = new
tl["params"]["v3"] = "오더51 토막 자막: 한 장 6 · 3장→2장 2 · 다시 나눔 4(둘째 장 시작 = 실소리 −0.09) · 소리·장·아나운서·BGM v2 그대로"
json.dump(tl, open("../타임라인_v3.json", "w"), ensure_ascii=False, indent=1)
print(len(S), "→", len(new))
