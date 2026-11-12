# 09강 아나운서 준비(오더44): 끝인사 소리 = v090 마지막 장(25) 구간 → bye_tc_090.wav · sound09.json · 클립 wav 를 아나운서B 로 복사
import subprocess, json, shutil
A = 797.66   # 24장 말끝 797.2225 ~ 25장 말시작 798.1075 쉼 가운데(20ms 칸)
B = 815.543  # v090 끝
subprocess.run(["ffmpeg","-v","error","-y","-i","v090.wav","-ss",str(A),"-to",str(B),"-c:a","pcm_s16le","bye_tc_090.wav"],check=True)
json.dump(dict(lecture=9, bye_v090=[A, B], bye_speech=[798.1075, 814.848], prev_slide_voice_end=797.2225), open("sound09.json","w"), ensure_ascii=False, indent=1)
for k in ("인삿말","끝인사"):
    for e in ("mp4","wav"): shutil.copy(f"../아나운서/9_{k}_090.{e}", f"../아나운서B/9_{k}_090.{e}")
shutil.copy("greet_tc_090.wav","../아나운서B/greet_tc_090.wav"); shutil.copy("bye_tc_090.wav","../아나운서B/bye_tc_090.wav")
print("ok")
