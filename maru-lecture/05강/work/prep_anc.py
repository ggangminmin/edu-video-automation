# 05강 아나운서 준비(오더44): 끝인사 소리 = v090 마지막 장(27) 구간 → bye_tc_090.wav · sound05.json · 클립 wav 를 아나운서B 로 복사
import subprocess, json, shutil
A = 764.10   # 26장 말끝 763.629 ~ 27장 말시작 764.557 쉼 가운데(20ms 칸)
B = 781.438  # v090 끝
subprocess.run(["ffmpeg","-v","error","-y","-i","v090.wav","-ss",str(A),"-to",str(B),"-c:a","pcm_s16le","bye_tc_090.wav"],check=True)
json.dump(dict(lecture=5, bye_v090=[A, B], bye_speech=[764.557, 780.774], prev_slide_voice_end=763.629), open("sound05.json","w"), ensure_ascii=False, indent=1)
for k in ("인삿말","끝인사"):
    for e in ("mp4","wav"): shutil.copy(f"../아나운서/5_{k}_090.{e}", f"../아나운서B/5_{k}_090.{e}")
shutil.copy("greet_tc_090.wav","../아나운서B/greet_tc_090.wav"); shutil.copy("bye_tc_090.wav","../아나운서B/bye_tc_090.wav")
print("ok")
