#!/bin/bash
# 생성 클립 빠른 검수(10/5): 받아쓰기 + 0.1초 단위 말 구간 + 2fps 컨택트시트. 사용: qa_clip.sh <출력폴더> <클립이름…>  (클립 폴더에서 실행)
S="$1"; shift
for k in "$@"; do
ffmpeg -loglevel error -y -i $k.mp4 -vf "fps=2,scale=640:-1,tile=5x2" -frames:v 1 "$S/${k}_sheet.jpg"
ffmpeg -loglevel error -y -i $k.mp4 -ar 16000 -ac 1 "$S/$k.wav"
whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -np -f "$S/$k.wav" 2>/dev/null | grep "\["
python3 - <<P
import subprocess,numpy as np
a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i','$k.mp4','-ac','1','-ar','16000','-f','f32le','-']),np.float32)
r=[float(np.sqrt((a[i:i+1600]**2).mean())) for i in range(0,len(a)-1600,1600)]
th=0.15*np.percentile(r,95); print('$k',''.join('#' if x>th else '.' for x in r))
P
done
