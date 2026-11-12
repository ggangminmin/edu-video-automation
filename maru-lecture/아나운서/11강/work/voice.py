import librosa, numpy as np, subprocess, re, sys
txt={'v_tcclose':"복잡한곳에서는절단전에실측값과판의방향을확인하고가배치해보세요기준선과결합부경계부조건을함께맞춰야합니다12강에서는벽과문다른바닥을연결하는마감과완료검사를살펴보겠습니다"}
txt['v_bye']=txt['v_tcclose']
for n in ['v_body','v_tcclose','v_bye','v_greet']:
    f=f'{sys.argv[1]}/{n}.wav'
    y,sr=librosa.load(f,sr=16000)
    f0,vf,_=librosa.pyin(y,fmin=60,fmax=300,sr=sr,frame_length=1024)
    f0=f0[vf]
    cen=np.median(librosa.feature.spectral_centroid(y=y,sr=sr))
    iv=librosa.effects.split(y,top_db=35); act=sum(e-s for s,e in iv)/sr
    o=subprocess.run(['ffmpeg','-i',f,'-af','ebur128','-f','null','-'],capture_output=True,text=True).stderr
    I=re.findall(r'I:\s+(-?[0-9.]+) LUFS',o)[-1]
    rate=f"{len(txt[n])/act:.2f}음절/초(발화)" if n in txt else ''
    print(f"{n}: F0 중앙 {np.median(f0):.0f}Hz (25~75% {np.percentile(f0,25):.0f}~{np.percentile(f0,75):.0f}) · 음색중심 {cen:.0f}Hz · 음량 {I} LUFS · 길이 {len(y)/sr:.2f}s 발화 {act:.2f}s {rate}")
