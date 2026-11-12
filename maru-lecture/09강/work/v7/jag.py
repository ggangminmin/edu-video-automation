# 지직 = 유성음 안에서 2ms 진폭이 들쭉날쭉(크래클). 2ms RMS 이웃 차 >6dB 인 칸 수 / 소리 칸 (−40dB 넘는 칸만)
import numpy as np, soundfile as sf, json
def jag(p, a=None, b=None):
    x, sr = sf.read(p); x = x[int((a or 0)*sr):int(b*sr) if b else None]; h = int(0.002*sr)
    r = 20*np.log10(np.sqrt((x[:len(x)//h*h].reshape(-1,h)**2).mean(1))+1e-9); v = (r[1:] > -40) & (r[:-1] > -40)
    j = np.abs(np.diff(r)) > 6; return dict(소리칸=int(v.sum()), 튐칸=int((j & v).sum()), 비율=round(float((j & v).sum()/max(v.sum(),1)),4))
R = {"옛 전체": jag("old_region.wav"), "새 전체": jag("new_region.wav"),
     "옛 「마지막에」 1.37~2.27": jag("old_region.wav", 1.37, 2.27), "새 「마지막에」 1.44~2.29": jag("new_region.wav", 1.44, 2.29)}
print(json.dumps(R, ensure_ascii=False)); json.dump(R, open("jag.json","w"), ensure_ascii=False)
