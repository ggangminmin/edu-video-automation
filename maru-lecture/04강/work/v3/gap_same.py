# 문장텀 「다름 1」 확인: 새 카드 글자는 비교 기준(1단계) 판에 없어 비교 불가 → v2 와 v3 깨끗한 음성 무음 목록 자체가 같은지 + 그 3줄 자리 쉼을 v2 음성에서 같은 식으로 잼
import os; os.environ["V"]="v3"
exec(open("04강/work/chk/gap_check04.py").read().split("tl3, v3 = voice")[0])
tl3,v3=voice("04강/타임라인_v3.json"); tl2,v2=voice("04강/타임라인_v2.json")
S3,S2=sils(v3),sils(v2); print("무음 구간 수", len(S2), len(S3), "같음" if len(S2)==len(S3) and all(abs(a-c)<0.002 and abs(b-d)<0.002 for (a,b),(c,d) in zip(S2,S3)) else "다름")
for t in ["확인이 필요한 경우도 있습니다"]:
    x=[s for s in tl3["subs"] if s["text"]==t][0]; f=lambda S:[(u,w) for u,w in S if x["voice_on"]-0.35<=w<=x["voice_on"]+0.12]
    print(f"「{t[:12]}」 voice_on {x['voice_on']} 쉼 v3 {[(round(u,3),round(w,3)) for u,w in f(S3)]} · v2 {[(round(u,3),round(w,3)) for u,w in f(S2)]}")
