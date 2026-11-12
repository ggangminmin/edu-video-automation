# mix_v7 vs mix_v6b: ① 0~27.40 그대로 ② BGM(= mix − 깨끗한 음성×−1.2dB) 시간 이동 없이 같음(끝 페이드 전까지) ③ 음성 조각 상관(seg_corr 와 같은 방식, mix 로)
import numpy as np, subprocess, json
SR = 48000; W = "09강/work"
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
ma, mb = load(f"{W}/mix_v6b.wav"), load(f"{W}/mix_v7.wav"); ca, cb = np.load(f"{W}/v7/clean_v6b.npy"), np.load(f"{W}/v7/clean_v7.npy")
g = 10**(-1.2/20); n = min(len(ma), len(ca)); ba = ma[:n] - g*ca[:n]; n2 = min(len(mb), len(cb)); bb = mb[:n2] - g*cb[:n2]
c = lambda x, y: float(np.dot(x, y)/np.sqrt(np.dot(x, x)*np.dot(y, y)))
p = int(27.40*SR); e = int((955.043933 - 5.9)*SR)
r = dict(앞_0_27_40_상관=round(c(ma[:p], mb[:p]), 6), 앞_최대차_LSB=int(np.abs(ma[:p]-mb[:p]).max()*32768),
         BGM_0_끝페이드전_상관=round(c(ba[:e], bb[:e]), 6), BGM_잔차_dB=round(float(20*np.log10(np.abs(ba[:e]-bb[:e]).max()+1e-12)), 1),
         길이=[len(ma)/SR, len(mb)/SR])
print(json.dumps(r, ensure_ascii=False)); json.dump(r, open("09강/검사_v7/믹스비교.json", "w"), ensure_ascii=False)
