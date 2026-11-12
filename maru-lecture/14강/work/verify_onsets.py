# 의심 줄(두 받아쓰기와 0.35초 넘게 어긋난 줄)만 짧은 창으로 다시 받아써 첫 단어 위치 확인
import runpy,io,contextlib,json,numpy as np,subprocess,re
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path('align14.py')
on,M,tt,fc,lines=g['on'],g['MLX_LINE'],g['stime'],g['first_char'],g['lines']
import mlx_whisper
raw=subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-ar","16000","-"],capture_output=True).stdout
x=np.frombuffer(raw,np.int16).astype(np.float32)/32768
out=[]
for i in range(len(lines)):
    if not(abs(on[i]-M[i])>0.35 and abs(on[i]-tt[fc[i]])>0.35): continue
    a=on[i]-2.0; b=on[i]+3.0
    r=mlx_whisper.transcribe(x[int(a*16000):int(b*16000)],path_or_hf_repo="mlx-community/whisper-large-v3-turbo",language="ko",word_timestamps=True,condition_on_previous_text=False)
    ws=[(round(a+w["start"],2),w["word"].strip()) for s in r["segments"] for w in s.get("words",[])]
    key=re.sub(r"[^가-힣A-Za-z0-9]","",lines[i][1].split()[0])[:2]
    hit=[t for t,w in ws if re.sub(r"[^가-힣A-Za-z0-9]","",w).startswith(key)]
    out.append(dict(i=i,text=lines[i][1],on=on[i],first_word_hit=hit,words=ws))
    print(i,lines[i][1][:14],'on',on[i],'창받아쓰기',hit[:3],flush=True)
json.dump(out,open('verify_onsets.json','w'),ensure_ascii=False,indent=1)
