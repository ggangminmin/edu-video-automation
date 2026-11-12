# 오더23: 오더09_공용/check_onsets09.py 복사 · v2→v3 경로만
# 인삿말·끝인사 자막 줄 시작 검산: 자막 시작 뒤 0.09초 = 말 시작인지. 소리 파일에서 voice_on 앞 0.12초 안 가장 조용한 30ms(쉼) · 뒤 0.15초(소리 있어야) dB
import sys, json, numpy as np, librosa
N = sys.argv[1]; tl = json.load(open(f"{N}강/타임라인_v3b.json")); L = tl["slides"][-1]["slide"]
A = {a["slide"]: a for a in tl["audio"]}
bad = 0
for sl in (1, L):
    a = A[sl]; y, _ = librosa.load(f"{N}강/{a['src']}", sr=16000)
    def db(t0, t1):
        s = y[max(0, int(t0 * 16000)):max(1, int(t1 * 16000))]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-7) if len(s) else -99
    for x in tl["subs"]:
        if x["slide"] != sl: continue
        t = x["voice_on"] - a["out"] + a["src_from"]           # 소리 파일 안 시각
        pre, post = min(db(t - 0.12 + k * 0.01, t - 0.09 + k * 0.01) for k in range(10)), db(t, t + 0.15)   # 앞 0.12초 안 가장 조용한 30ms(짧은 쉼)
        lead = round(x["voice_on"] - x["start"], 3)
        ok = post - pre >= 10 and 0.05 <= lead <= 0.12
        bad += not ok
        print(f"  {sl:>2} {x['start']:8.3f} 앞{pre:6.1f} 뒤{post:6.1f} 선행{lead:.3f} {'OK ' if ok else '확인'} {x['text'][:28]}")
print(N, "확인 필요", bad)
