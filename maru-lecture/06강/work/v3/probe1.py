# 새 나눔 4곳: 받아쓰기 단어 시각 + −50dB 쉼 + RMS (받아쓰기 없음, 가벼움)
exec(open("v3/base.py").read())
P = {93: (387.487, 393.627, "공급자에게"), 144: (608.374, 612.879, "적고"), 81: (340.273, 346.213, "실제로"), 119: (505.972, 511.745, "같은")}
for k, (a, b, w) in P.items():
    ws = words_out(a - 0.5, b); print(f"\n#{k} {w}", ws)
    c = [t for t, x in ws if x.startswith(w[:2])]
    for t in c:
        print("  후보", t, "쉼", pauses(t - 0.6, t + 0.4)); print("  RMS", rms(t - 0.45, t + 0.25))
