# 지직(거친 목소리) = 유성음 HNR(자기상관 최대 r → 10log10(r/(1−r))) 낮음 · 40ms 창 · 소리 −35dB 넘고 r>0.3(유성)만 · 중앙값·하위10%·「r<0.6 거친 창」 비율
import numpy as np, json
SR = 48000; a = np.load("clean_v6b.npy"); b = np.load("clean_v7.npy")
def hnr(x):
    h = int(0.04*SR); out = []
    for i in range(0, len(x)-h, h//2):
        f = x[i:i+h]; 
        if 20*np.log10(f.std()+1e-9) < -35: continue
        f = (f - f.mean()) * np.hanning(h); ac = np.correlate(f, f, "full")[h-1:]; ac /= ac[0]
        lo, hi = SR//400, SR//70; r = ac[lo:hi].max()
        if r > 0.3: out.append(r)
    r = np.array(out); d = 10*np.log10(r/(1-r+1e-9))
    return dict(유성창=len(r), HNR중앙=round(float(np.median(d)),1), HNR하위10=round(float(np.percentile(d,10)),1), 거친창비율=round(float((r<0.6).mean()),3))
R = {"옛 구간": hnr(a[int(27.45*SR):int(31.70*SR)]), "새 구간": hnr(b[int(27.45*SR):int(30.97*SR)]),
     "참고 앞 「오늘은…」": hnr(a[int(21.8*SR):int(25.9*SR)]), "참고 뒤 「넘어가는…」": hnr(a[int(31.75*SR):int(33.6*SR)]), "참고 뒤 「처음의…」": hnr(a[int(35.1*SR):int(39.0*SR)])}
for k, v in R.items(): print(k, v)
json.dump(R, open("hnr.json","w"), ensure_ascii=False, indent=1)
