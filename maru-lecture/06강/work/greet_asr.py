# 인삿말 타입캐스트 0.9배(강의인삿말/0.9배/인삿말_06강_090.wav → greet_tc_090.wav 48k) 단어 받아쓰기 + 아나운서 클립 2개 받아쓰기(강 번호 확인)
import json, subprocess, mlx_whisper
def dur(f): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]))
M="mlx-community/whisper-large-v3-turbo"
r = mlx_whisper.transcribe("greet_tc_090_16k.wav", path_or_hf_repo=M, language="ko", word_timestamps=True, condition_on_previous_text=False)
w = [[x["start"], x["end"], x["word"]] for s in r["segments"] for x in s.get("words", [])]
d1 = dur("greet_tc_090.wav")
json.dump(dict(src="강의인삿말/0.9배/인삿말_06강_090.wav", dur_src=round(d1*0.9,3), dur_090=d1, text=r["text"], words=w), open("greet_tc_words.json", "w"), ensure_ascii=False, indent=0)
print("인삿말TC", d1, r["text"])
for k in ["인삿말","끝인사"]:
    f=f"../아나운서/06_{k}_090.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-ar","16000","-ac","1",f"../아나운서/06_{k}_090_16k.wav"],check=True)
    r = mlx_whisper.transcribe(f"../아나운서/06_{k}_090_16k.wav", path_or_hf_repo=M, language="ko", word_timestamps=True, condition_on_previous_text=False)
    w = [[x["start"], x["end"], x["word"]] for s in r["segments"] for x in s.get("words", [])]
    json.dump(dict(text=r["text"], words=w), open(f"../아나운서/06_{k}_090_words.json","w"), ensure_ascii=False, indent=0)
    print("클립", k, r["text"])
