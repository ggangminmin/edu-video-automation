# 규칙 24·⑥: newline_onset --all 판정불가·걸림 줄(바뀐 카드 밖 포함) 세 근거 — 쉼(−45dB ≥15ms)·쉼 사이 조각 받아쓰기·자막 시작/실소리에서 앞 창[t-1.0,t]·뒤 창[t,t+1.2]
exec(open("v3/base.py").read().replace("../타임라인_v2.json", "../타임라인_v3.json"))
import mlx_whisper
def asr(x, y):
    return mlx_whisper.transcribe(V[max(0, int(x * SR)):int(y * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
N = [i for i, x in enumerate(S) if x["n"] in (18, 75, 83, 87, 148, 167, 190)]   # 검사기 줄 번호 = n 필드(줄3 은 probe5_줄3.txt)
for n in N:
    x = S[n]; st = x["start"]; on = x["voice_on"]
    print(f"\n줄{x['n']} 「{x['text']}」 자막 {st:.3f} voice_on {on:.3f}", flush=True)
    a, b = st - 0.5, st + 0.6
    ps = pauses(a, b, TH=-45, GAP=3); print("  쉼(−45 ≥15ms)", ps, " −50 ≥30ms", pauses(a, b))
    edges = [a] + [v for p in ps for v in p] + [b]
    for j in range(0, len(edges) - 1, 2):
        u, w = edges[j], edges[j + 1]
        if w - u > 0.06: print(f"   조각 [{u:.3f},{w:.3f}] 「{asr(u - 0.01, w + 0.01)}」", flush=True)
    for t in sorted(set([round(st, 3), round(on, 3), round(on + 0.05, 3)])):
        print(f"   t={t} 앞 「{asr(t - 1.0, t)}」 | 뒤 「{asr(t, t + 1.2)}」", flush=True)
    print("  RMS", rms(st - 0.1, st + 0.25))
