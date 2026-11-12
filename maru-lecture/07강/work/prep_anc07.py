# 07강 아나운서 준비(오더46): 끝인사 소리 = v090 마지막 장(25) 구간 → bye_tc_090.wav · sound09.json(이름은 make_tl 호환)
import subprocess, json
A = 769.68   # 24장 말끝 769.177 ~ 25장 말시작 770.191 쉼 가운데(20ms 칸) · silencedetect −40dB d0.5
B = 787.199  # v090 끝
subprocess.run(["ffmpeg","-v","error","-y","-i","v090.wav","-ss",str(A),"-to",str(B),"-c:a","pcm_s16le","bye_tc_090.wav"],check=True)
json.dump(dict(lecture=7, greet_src="강의인삿말/0.9배/인삿말_07강_090.wav", bye_v090=[A, B], bye_speech=[770.191, 786.564], prev_slide_src_to=769.177), open("sound09.json","w"), ensure_ascii=False, indent=1)
print("ok")
