# 포즈 실측: 초록 키 마스크 → 머리 꼭대기 y, 머리 중심 x, 어깨폭, 손(피부색) 중심
import numpy as np, subprocess, sys
def frames(f, ss, t, scale=1):
    w,h=1080//scale,1920//scale
    raw=subprocess.run(['ffmpeg','-v','error','-ss',str(ss),'-t',str(t),'-i',f,'-vf',f'scale={w}:{h}','-pix_fmt','rgb24','-f','rawvideo','-'],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(-1,h,w,3)
def measure(fr):
    r,g,b=[fr[...,i].astype(int) for i in range(3)]
    m=~((g>r+60)&(g>b+60))
    rows=np.where(m.sum(1)>3)[0]; top=rows[0]
    hx=np.where(m[top+40])[0].mean()
    sh=np.where(m[top+330])[0]; shw=sh.max()-sh.min()
    skin=m&(r>150)&(r>g+15)&(r>b+25)
    skin[:top+300]=False   # 얼굴 제외
    ys,xs=np.where(skin)
    return dict(top=int(top),headx=round(float(hx),1),shoulder=int(shw),handx=round(float(xs.mean()),1) if len(xs) else None,handy=round(float(ys.mean()),1) if len(ys) else None,n=len(xs))
if __name__=='__main__':
    f,ss=sys.argv[1],float(sys.argv[2])
    print(measure(frames(f,ss,0.04)[0]))
