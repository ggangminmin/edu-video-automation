import subprocess,sys,os
P="../.."
av, out, KEYP = sys.argv[1], sys.argv[2], sys.argv[3]
PRE=0.5; R=1/0.9
subs=[(0.00,"평면에서 패턴을 골랐는데"),(2.0,"막상 놓으려니 기둥과 문틀이 있습니다"),(5.12,"어디서 시작하고 어느 결합부를 남겨 잘라야 할까요?"),
(9.06,"이번에는 기준선에서 출발해 장애물 주변을 실측하고"),(11.3,"가배치하는 순서를 살펴보겠습니다"),(15.12,"전체 배치를 유지하면서 특수부를 처리하는 방법에 집중하겠습니다")]
END=18.82
os.makedirs("sub",exist_ok=True)
for i,(t,txt) in enumerate(subs):
    subprocess.run(["magick","-size","1920x1080","xc:none","-font","/Library/Fonts/NotoSansKR-Bold.otf","-pointsize","50","-fill","#24313a","-kerning","-1",
      "-gravity","center","-annotate","+0+420",txt,f"sub/{i}.png"],check=True)
dur=PRE+21.66+1.0
inp=["-loop","1","-t",str(dur),"-i","s11-02.png","-i",av,"-loop","1","-t",str(dur),"-i",f"{P}/마루시공-자막바-3.png","-loop","1","-t",str(dur),"-i",f"{P}/교재/대한마루협회 로고.png",
     "-i","open_090.mp3","-stream_loop","-1","-i",f"{P}/BGM/Clear Focus.mp3"]
for i in range(len(subs)): inp+=["-loop","1","-t",str(dur),"-i",f"sub/{i}.png"]
f=[f"[1:v]setpts=PTS-STARTPTS+{PRE}/TB,fps=29.97,{KEYP},despill=type=green,scale=-1:1459[av]",
   "[3:v]scale=280:-1[lg]",
   "[0:v][av]overlay=940:33:eof_action=pass[a1]","[a1][2:v]overlay[a2]","[a2][lg]overlay=1550:66[a3]"]
last="a3"
for i,(t,_) in enumerate(subs):
    s=PRE+t*R; e=PRE+(subs[i+1][0]*R if i+1<len(subs) else END*R+0.3)
    f.append(f"[{last}][{6+i}:v]overlay=enable='between(t,{s:.2f},{e:.2f})'[b{i}]"); last=f"b{i}"
f.append(f"[4:a]adelay={int(PRE*1000)}|{int(PRE*1000)},apad[vo]")
f.append(f"[5:a]volume=-20dB,afade=t=in:d=1,afade=t=out:st={dur-1.5}:d=1.5[bg]")
f.append("[vo][bg]amix=inputs=2:duration=first:normalize=0[aout]")
subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",";".join(f),"-map",f"[{last}]","-map","[aout]","-t",str(dur),
  "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-r","30000/1001","-c:a","aac","-b:a","192k",out],check=True)
print("ok",out)
