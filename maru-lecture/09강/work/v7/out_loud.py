# 최종 출력 음량(cx 판정 방식): (L+R)/2 모노 · 옛 v6b 27.449833~31.689833 / 새 VER 27.449833~30.969833 · LUFS(ebur128) · 5ms 발화칸 RMS(−40dB 넘음) · 클리핑
import subprocess, numpy as np, re, json, sys
VER = sys.argv[1]
def get(p, a=None, b=None):
    x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ar","48000","-ac","2","-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64).reshape(-1,2)
    return x
def lufs(m):
    o = subprocess.run(["ffmpeg","-f","f64le","-ar","48000","-ac","1","-i","-","-af","ebur128","-f","null","-"],input=m.tobytes(),capture_output=True).stderr.decode(); return float(re.findall(r"I:\s+(-?[0-9.]+) LUFS",o)[-1])
def rms(m):
    f = m[:len(m)//240*240].reshape(-1,240); r = np.sqrt((f**2).mean(1)); r = r[20*np.log10(r+1e-12) > -40]; return round(float(20*np.log10(np.sqrt((r**2).mean()))),3)
R = {}
for kind, ext in (("mp4", f"09강_{{}}.mp4"), ("mix", "work/mix_{}.wav")):
    xa, xb = get(ext.format("v6b")), get(ext.format(VER))
    a = xa[int(27.449833*48000):int(31.689833*48000)].mean(1); b = xb[int(27.449833*48000):int(30.969833*48000)].mean(1)
    R[kind] = dict(옛_LUFS=lufs(a), 새_LUFS=lufs(b), LU차=round(lufs(b)-lufs(a),2), 옛_RMS=rms(a), 새_RMS=rms(b), RMS차=round(rms(b)-rms(a),3),
                   새판_전체_피크_dBFS=round(float(20*np.log10(np.abs(xb).max())),2), 새판_0dBFS_샘플=int((np.abs(xb) >= 0.99997).sum()), 새판_구간_피크=round(float(20*np.log10(np.abs(xb[int(27.45*48000):int(30.97*48000)]).max())),2))
print(json.dumps(R, ensure_ascii=False, indent=1)); json.dump(R, open(f"검사_{VER}/출력음량.json","w"), ensure_ascii=False, indent=1)
