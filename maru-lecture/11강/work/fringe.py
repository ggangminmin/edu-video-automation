# 아나운서 윤곽 2px 띠 안 초록 픽셀(G > max(R,B)+8) 개수 — 영상 프레임 vs 그 슬라이드 원본 PNG 차이로 아나운서 영역을 잡는다(00강·11강 같은 방식)
import sys, numpy as np, subprocess
from PIL import Image, ImageFilter
def frame(video, t, out):
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{t}","-i",video,"-frames:v","1",out],check=True); return out
def measure(frame_png, slide_png, y1=905):
    F = np.asarray(Image.open(frame_png).convert("RGB")).astype(int)
    S = np.asarray(Image.open(slide_png).convert("RGB").resize((1920,1080))).astype(int)
    d = np.abs(F - S).max(2) > 40
    d[y1:] = False; d[:, :1000] = False; d[:150, 1500:] = False          # 자막바 아래·왼쪽·우상단 로고 제외
    m = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
    dil = np.asarray(m.filter(ImageFilter.MaxFilter(5))) > 0; ero = np.asarray(m.filter(ImageFilter.MinFilter(5))) > 0
    band = dil & ~ero                                                     # 경계 양쪽 2px 띠
    g = (F[..., 1] > np.maximum(F[..., 0], F[..., 2]) + 8) & band
    return int(band.sum()), int(g.sum()), g
if __name__ == "__main__":
    v, t, s = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    f = frame(v, t, f"fr_{t}.png"); b, gn, _ = measure(f, s); print(f"{t}s 띠 픽셀 {b} · 초록 {gn}")
