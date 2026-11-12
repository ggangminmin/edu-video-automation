# 4곳: 넓은 범위 −45dB 15ms 이상 쉼 → 쉼 사이 조각 따로 받아쓰기 + 쉼마다 앞 창[t0-1.2,t0]·뒤 창[t1,t1+1.2]
exec(open("v3/base.py").read())
import mlx_whisper
def asr(x, y):
    return mlx_whisper.transcribe(V[max(0, int(x * SR)):int(y * SR)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko")["text"].strip()
R = {93: (388.9, 390.9), 144: (611.3, 613.3), 81: (340.2, 342.0), 119: (506.9, 508.9)}
for k, (a, b) in R.items():
    ps = pauses(a, b, TH=-45, GAP=3); print(f"\n#{k} 쉼(−45dB ≥15ms)", ps, flush=True)
    edges = [a] + [x for p in ps for x in p] + [b]
    for j in range(0, len(edges) - 1, 2):
        x, y = edges[j], edges[j + 1]
        if y - x > 0.08: print(f"   조각 [{x:.3f},{y:.3f}] 「{asr(x - 0.02, y + 0.02)}」", flush=True)
    for p0, p1 in ps:
        print(f"   쉼 {p0}~{p1} | 앞 「{asr(p0 - 1.2, p0)}」 | 뒤 「{asr(p1, p1 + 1.2)}」", flush=True)
