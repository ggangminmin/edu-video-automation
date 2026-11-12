import os,re,json,subprocess,unicodedata as u
from pptx import Presentation
R="../.."; AD=f"{R}/11-19강"; PD=f"{R}/강의자료"
def nf(x): return u.normalize("NFC",x)
def norm(s): return re.sub(r"[^가-힣0-9A-Za-z]","",s)
def notes(n):
    f=[x for x in os.listdir(PD) if nf(x).startswith(f"261030_마루시공전문가_{n}강") and x.endswith(".pptx")][0]
    out=[]
    for s in Presentation(f"{PD}/{f}").slides:
        t=s.notes_slide.notes_text_frame.text.split("교재:")[0] if s.has_notes_slide else ""
        out.append(" ".join(l.strip() for l in t.splitlines() if l.strip() and not re.match(r"\s*\d{2}-\d{3}",l)))
    return out
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
def whisper(src,ss,t,tag):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",str(ss),"-i",src,"-t",str(t),"-ac","1","-ar","16000",f"{tag}.wav"],check=True)
    subprocess.run(["whisper-cli","-m",os.path.expanduser("~/.cache/whisper-cpp/ggml-large-v3-turbo.bin"),"-l","ko","-f",f"{tag}.wav","-oj","-of",tag,"-np"],check=True,capture_output=True)
    js=json.load(open(f"{tag}.json"))["transcription"]
    return [(ss+x["offsets"]["from"]/1000, ss+x["offsets"]["to"]/1000, x["text"]) for x in js]
import difflib
def find(segs,key,after=0):
    k=norm(key)[:12]; best=(0,None)
    for a,b,t in segs:
        r=difflib.SequenceMatcher(None,k,norm(t)[:12]).ratio()
        if r>best[0]: best=(r,a)
    print("   match",round(best[0],2)); return best[1]
res={}
for n in range(11,21):
    a=[x for x in os.listdir(AD) if f"{n}강" in nf(x)][0]; src=f"{AD}/{a}"; D=dur(src); N=notes(n)
    h=whisper(src,0,75,f"h{n}"); tl=whisper(src,D-60,60,f"t{n}")
    # opening: from voice start to start of slide-3 text
    nxt=next(x for x in N[2:] if x)
    o_end=find(h,nxt); o_start=max(0,h[0][0]-0.05)
    c_start=find(tl,N[-1]); c_end=tl[-1][1]
    # end of previous segment before boundaries (trim silence)
    o_last=max(b for a_,b,t in h if b<=o_end+0.01)
    res[n]=dict(src=src,open=[round(o_start,2),round(o_last+0.25,2)],close=[round(c_start-0.05,2),round(min(D,c_end+0.3),2)],
                open_txt=N[1][:30],close_txt=N[-1][:30],D=D)
    print(n,res[n]["open"],res[n]["close"],round(D,1))
json.dump(res,open("segments.json","w"),ensure_ascii=False,indent=1)
