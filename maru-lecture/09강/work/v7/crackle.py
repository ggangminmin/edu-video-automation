# 지직거림(클릭·크래클) 실측: 옛(v6b 27.45~31.70) vs 새(v7 27.45~30.97) · 고역(>6kHz) 순간 피크 · 2차 차분 튐 · 스펙트럼 그림
import numpy as np, sys, json
from scipy.signal import butter, sosfiltfilt
import soundfile as sf
SR = 48000; a = np.load("09강/work/v7/clean_v6b.npy"); b = np.load("09강/work/v7/clean_v7.npy")
def stats(z):
    h = sosfiltfilt(butter(6, 6000, "hp", fs=SR, output="sos"), z)
    d2 = np.abs(np.diff(z, 2)); fr = z[:len(z)//240*240].reshape(-1,240); sp = np.sqrt((fr**2).mean(1)).repeat(240)[:len(d2)] + 1e-6
    spikes = int(((d2 / sp) > 1.2).sum())                         # 둘레 소리 대비 2차 차분 튐(샘플)
    e = h[:len(h)//240*240].reshape(-1,240); hr = np.sqrt((e**2).mean(1)); pk = np.abs(e).max(1); crest = pk / (hr + 1e-9)
    return dict(고역_RMS_dB=round(float(20*np.log10(h.std())),1), 고역_피크_dB=round(float(20*np.log10(np.abs(h).max())),1), 고역_크레스트_5ms창_최대=round(float(crest.max()),1),
                고역_크레스트_8넘는_창=int((crest > 8).sum()), 차분튐_샘플=spikes, 전체RMS_dB=round(float(20*np.log10(z.std())),1))
old = a[int(27.45*SR):int(31.70*SR)]; new = b[int(27.45*SR):int(30.97*SR)]
r = dict(옛_v6b=stats(old), 새_v7=stats(new), 옛_뒤문장_넘어가는=stats(a[int(31.75*SR):int(33.6*SR)]), 옛_앞문장_오늘은=stats(a[int(21.8*SR):int(25.9*SR)]))
print(json.dumps(r, ensure_ascii=False, indent=1)); json.dump(r, open("09강/work/v7/crackle.json", "w"), ensure_ascii=False, indent=1)
sf.write("09강/work/v7/old_region.wav", old, SR, subtype="FLOAT"); sf.write("09강/work/v7/new_region.wav", new, SR, subtype="FLOAT")
