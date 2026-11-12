# 짝수 모음 클립 앞 60초 받아쓰기 → 제4강 구간 찾기
import mlx_whisper, json, subprocess
M="mlx-community/whisper-large-v3-turbo"; out={}
for k in ["인삿말","끝인사"]:
    f=f"moum_{k}_head.wav"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"../../인삿말/짝수_{k}.mp4","-t","60","-vn","-ar","16000","-ac","1",f],check=True)
    r=mlx_whisper.transcribe(f,path_or_hf_repo=M,language="ko",word_timestamps=True,condition_on_previous_text=False)
    out[k]=[[s["start"],s["end"],s["text"]] for s in r["segments"]]
    for s in out[k]: print(k, round(s[0],2), round(s[1],2), s[2])
json.dump(out,open("moum_head.json","w"),ensure_ascii=False,indent=0)
