# 지직(성대 긁힘·크래클) = 20ms 창 피크/RMS(크레스트) 큰 창. 소리 창(−35dB 넘음)만 · 크레스트 >5 비율 · 최대
import numpy as np, soundfile as sf, json
SR = 48000; a = np.load("clean_v6b.npy"); b = np.load("clean_v7.npy")
def cr(x):
    h = 960; f = x[:len(x)//h*h].reshape(-1, h); r = np.sqrt((f**2).mean(1)); p = np.abs(f).max(1); v = 20*np.log10(r+1e-9) > -35; c = p[v]/r[v]
    return dict(창=int(v.sum()), 크레스트5넘음=int((c > 5).sum()), 비율=round(float((c > 5).mean()), 3), 최대=round(float(c.max()), 2), 중앙=round(float(np.median(c)), 2))
R = {"옛 구간(v6b 27.45~31.70)": cr(a[int(27.45*SR):int(31.70*SR)]), "새 구간(v7 27.45~30.97)": cr(b[int(27.45*SR):int(30.97*SR)]),
     "옛 「마지막에」(v6b 28.82~29.72)": cr(a[int(28.82*SR):int(29.72*SR)]), "새 「마지막에」(v7 28.89~29.74)": cr(b[int(28.89*SR):int(29.74*SR)]),
     "참고 앞 「오늘은…」": cr(a[int(21.8*SR):int(25.9*SR)]), "참고 뒤 「넘어가는…」": cr(a[int(31.75*SR):int(33.6*SR)]), "참고 뒤 「처음의…」": cr(a[int(35.1*SR):int(39.0*SR)])}
for k, v in R.items(): print(k, v)
json.dump(R, open("crest.json", "w"), ensure_ascii=False, indent=1)
