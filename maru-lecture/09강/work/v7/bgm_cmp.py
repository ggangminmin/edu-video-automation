# render09 와 같은 BGM 사슬을 v6b·v7 total 로 각각 → 끝 페이드 전까지 같은지 · 그리고 mix − BGM = 음성만 → 조각 상관
import json, subprocess, numpy as np
SR = 48000
def bgm(T):
    BG = json.load(open("09강/타임라인_v7.json"))["bgm"]; nb = BG["loops"]
    ch = "".join(f"[{j}:a]aformat=sample_rates=48000:channel_layouts=stereo[b{j}];" for j in range(nb)); cur = "b0"
    for j in range(1, nb): ch += f"[{cur}][b{j}]acrossfade=d={BG['crossfade']}:c1=tri:c2=tri[x{j}];"; cur = f"x{j}"
    ch += f"[{cur}]adelay=21:all=1,volume={BG['gain_db'] - 1.2:.2f}dB,afade=t=out:st={T - 5.836:.3f}:d={BG['fade_out']},atrim=0:{T},aformat=channel_layouts=mono[bg]"
    o = subprocess.run(["ffmpeg", "-v", "error", *sum([["-i", "../" + BG["file"]] for _ in range(nb)], []), "-filter_complex", ch, "-map", "[bg]", "-f", "f32le", "-ar", "48000", "-"], capture_output=True).stdout
    return np.frombuffer(o, np.float32).astype(np.float64)
Ta, Tb = round(30000/1001*0 + 955.778, 6), 955.043933
q = lambda t: round(t * 30000 / 1001) * 1001 / 30000
a, b = bgm(q(Ta)), bgm(q(Tb)); e = int((q(Tb) - 5.9) * SR)
print("BGM 끝페이드 전 최대차", float(np.abs(a[:e] - b[:e]).max()))
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32).astype(np.float64)
ma, mb = load("09강/work/mix_v6b.wav"), load("09강/work/mix_v7.wav")
va = ma[:len(a)] - a[:len(ma)]; vb = mb[:len(b)] - b[:len(mb)]
np.save("09강/work/v7/mixvoice_v6b.npy", va.astype(np.float32)); np.save("09강/work/v7/mixvoice_v7.npy", vb.astype(np.float32))
print("음성만 잔차(앞 10초) 최대", float(np.abs(va[:10*SR]).max()) if False else "", )
