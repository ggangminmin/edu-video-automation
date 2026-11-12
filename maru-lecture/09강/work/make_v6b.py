# 09강 v6b (팀장 결정 11/9: v5 부터 있던 늦은 자막 3줄, 규칙 24 세 근거로 발견) = 타임라인_v6 에서 n 36·100·139 시작만 실소리 −0.09 + 앞 카드 끝 맞춤
import json, os
L = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tl = json.load(open(f"{L}/타임라인_v6.json")); S = tl["subs"]
ON = {36: 131.045, 100: 392.645, 139: 558.265}   # 100: ㅅ 마찰 시작(392.60~.645 쉼 끝) · 11/9 음절 역산으로 고침(첫 추정 392.745 = 모음 「이」)   # 근거 = 검사_v6/판정불가_근거.md
for i, x in enumerate(S):
    if x["n"] in ON:
        new = round(ON[x["n"]] - 0.09, 3); d = new - x["start"]
        assert S[i - 1]["end"] == x["start"] and S[i - 1]["slide"] == x["slide"]
        print(x["n"], x["text"][:12], round(x["start"], 3), "→", new, f"({d:+.3f})")
        x["start"] = new; S[i - 1]["end"] = new; x["voice_on"] = round(ON[x["n"]], 3)
        if "v090_on" in x: x["v090_on"] = round(x["v090_on"] + d, 3)
        x["how"] = "v6b 늦은 자막 고침(실소리 −0.09 · 세 근거)"
tl["params"]["v6b"] = "팀장 결정 11/9: 36·100·139 시작 = 실소리 −0.09(판정불가_근거.md) · 그 외 v6 와 같음"
json.dump(tl, open(f"{L}/타임라인_v6b.json", "w"), ensure_ascii=False, indent=1)
