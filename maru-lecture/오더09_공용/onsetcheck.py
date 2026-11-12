# 입 싱크 검산(소리 시작점 방식): 쉼(−40dB 아래 ≥0.08초) 뒤 말 시작점을 클립·타깃에서 각각 찾고,
#  클립 시작점을 warp 지도로 출력 시각에 옮겨 타깃 시작점과 짝(±0.4초 안 가장 가까운 것) → 오차. whisper 단어 시각 오류(무음 시작에 찍힘)와 무관.
# 실행: python3 onsetcheck.py <clip.wav> <target.wav> <warp.json>
import sys, json, numpy as np, librosa
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
def onsets(p, a, b):
    y, _ = librosa.load(p, sr=16000); fr = librosa.util.frame(np.pad(y, (0, 160)), frame_length=160, hop_length=160)
    d = 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7); out = []; run = 0
    for i in range(int(a * 100), int(b * 100)):
        if d[i] < -40: run += 1
        else:
            if run >= 8: out.append(i / 100)
            run = 0
    return out
C = [cs + float(np.interp(c - cs, cl, tau)) for c in onsets(cw, cs + 0.05, ce)]   # 입 모양 시작이 나오는 출력 시각
T = [cs + (t - ts) for t in onsets(tw, ts + 0.05, te)]                            # 타입캐스트 말 시작 출력 시각
pairs = []
for t in T:
    k = int(np.argmin([abs(c - t) for c in C])) if C else None
    if k is not None and abs(C[k] - t) <= 0.4: pairs.append((round(t, 2), round(C[k] - t, 3)))
    else: pairs.append((round(t, 2), None))
e = np.array([abs(x[1]) for x in pairs if x[1] is not None])
res = dict(n_target_onsets=len(T), n_clip_onsets=len(C), matched=int(len(e)), median=round(float(np.median(e)), 3) if len(e) else None,
           max=round(float(e.max()), 3) if len(e) else None, over_0_1=[x for x in pairs if x[1] is not None and abs(x[1]) > 0.1],
           unmatched=[x[0] for x in pairs if x[1] is None], pairs=pairs)
json.dump(res, open(wj.replace(".json", "_onset.json"), "w"), ensure_ascii=False, indent=1)
print(wj.split("/")[-1], {k: v for k, v in res.items() if k != "pairs"})
