# 민석 귀 확인 A/B: 최종 출력(mp4, BGM 포함)에서 n90 앞뒤 1초
import subprocess
for nm, src, a, b in (("옛_v3_6-16.39~6-22.86_최종출력.wav", "../../07강_v3.mp4", 376.39, 382.855), ("새_v4_6-16.43~6-22.83_최종출력.wav", "../../07강_v4.mp4", 376.426, 382.826)):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(a),"-to",str(b),"-i",src,"-vn","-c:a","pcm_s16le","-ar","48000",f"../../검사_v4/AB/{nm}"], check=True)
print("ok")
