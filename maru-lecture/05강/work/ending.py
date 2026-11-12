# v2 엔딩 — 00강 226.13~226.80 재현: 방사형 줌 블러(슬라이드가 중심에서 바깥으로 번짐) → 나무색으로 덮임 → 중앙 로고가 가로 번짐을 풀며 들어옴
# 카드 로고 = 00강 실측 영역 (732,492)~(1184,586) 에 맞춤(배경 대비 차>35 기준, 판정서와 같은 잣대)
import subprocess, numpy as np
from PIL import Image, ImageFilter
R = "../../.."
BG = (223, 182, 144)
L = Image.open(f"{R}/교재/대한마루협회 로고.png").convert("RGBA")
TARGET = (732, 492, 1184, 586)

def ink_bbox(img):
    a = np.asarray(img.convert("RGB")).astype(int)
    d = np.abs(a - np.array(BG)).max(2) > 35
    ys, xs = np.where(d); return xs.min(), ys.min(), xs.max(), ys.max()

def place(s, x, y):
    Ls = L.resize((round(L.width * s), round(L.height * s)), Image.LANCZOS)
    c = Image.new("RGBA", (1920, 1080), BG + (255,)); c.alpha_composite(Ls, (round(x), round(y))); return c, Ls
# 맞춤: 크기 → 위치 순으로 두 번
s, x, y = 0.2287, 700, 430
for _ in range(4):
    c, _ = place(s, x, y); b = ink_bbox(c)
    s *= ((TARGET[2] - TARGET[0]) / (b[2] - b[0]) + (TARGET[3] - TARGET[1]) / (b[3] - b[1])) / 2
    c, _ = place(s, x, y); b = ink_bbox(c)
    x += (TARGET[0] + TARGET[2] - b[0] - b[2]) / 2; y += (TARGET[1] + TARGET[3] - b[1] - b[3]) / 2   # 중심 맞춤
card, Ls = place(s, x, y)
print("카드 로고 영역", ink_bbox(card), "목표", TARGET, "배율", round(s, 4))
card.convert("RGB").save("card.png")
MARK_R = round(x + 492 * s) + 2   # 원본 로고 마크 오른끝 x492
logo_only = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); logo_only.alpha_composite(Ls, (round(x), round(y)))

# 전환 20프레임(0.667초). 00강 프레임 관찰(226.0~): +0.04 번짐 시작, +0.37 까지 번짐·밝아짐, +0.40 나무색, 로고는 +0.37 부터 가로 번짐 → +0.57 선명
src = Image.open("../slides/s-27.png").convert("RGB")   # 전환 시작 화면 = 슬라이드27(05강 마지막 장)(자막·아나운서 이미 빠짐, 우상단 로고는 render 에서 위에 얹음)
A = np.asarray(src).astype(np.float32)
CX, CY = 900, 528                                    # 00강 줄무늬가 모이는 점(실측 근사)
N = 20; FPS = 30000 / 1001
def zoom(img, k, steps=26):
    acc = np.zeros_like(A)
    for i in range(steps):
        z = 1 + k * i / (steps - 1)
        w, h = round(1920 * z), round(1080 * z)
        im = img.resize((w, h), Image.BILINEAR)
        l, t = round(CX * z - CX), round(CY * z - CY)
        acc += np.asarray(im.crop((l, t, l + 1920, t + 1080))).astype(np.float32)
    return acc / steps
def ease(u): return u * u * (3 - 2 * u)
bgc = np.array(BG, np.float32)
frames = []
for f in range(N):
    t = f / FPS
    p = min(1, max(0, (t - 0.12) / 0.38))            # 나무색 덮기 0.12→0.50 (00강 +0.3 에도 번짐 남음)
    k = 1.6 * ease(min(1, t / 0.30))                 # 번짐 세기(00강처럼 긴 줄무늬)
    z = zoom(src, k) if k > 0.005 else A.copy()
    yy, xx = np.mgrid[0:1080, 0:1920]
    r = np.sqrt(((xx - CX) / 1.0) ** 2 + ((yy - CY) * 3.0) ** 2)      # 가로로 긴 중앙 흰 빛
    glow = np.exp(-r / 160.0)[..., None] * 0.85 * np.sin(np.pi * min(1, t / 0.45))
    z = z * (1 - glow) + 255 * glow
    out = z * (1 - 0.92 * ease(p)) + bgc * 0.92 * ease(p) if p < 1 else bgc + 0 * z
    fr = Image.fromarray(out.clip(0, 255).astype(np.uint8)).convert("RGBA")
    if t >= 0.36:                                    # 로고 진입: 마크는 제자리 선명, 글자는 오른쪽으로 끌린 번짐이 줄어듦(00강 +0.4~0.6)
        q = min(1, (t - 0.36) / 0.26)
        blur = int(round(260 * (1 - ease(q))))
        lo = logo_only
        if blur > 1:
            arr = np.asarray(lo).astype(np.float32); acc = np.zeros_like(arr)
            for d in range(blur): acc += np.roll(arr, d, axis=1)   # 오른쪽으로 끌리는 꼬리
            lo = Image.fromarray((acc / blur).astype(np.uint8))
        a = np.asarray(lo).copy(); a[..., 3] = (a[..., 3] * min(1, 0.4 + q)).astype(np.uint8)
        fr.alpha_composite(Image.fromarray(a))
        mk = np.asarray(logo_only).copy(); mk[:, MARK_R:, 3] = 0                     # 마크만 선명하게 위에
        mk[..., 3] = (mk[..., 3] * min(1, 0.6 + q)).astype(np.uint8)
        fr.alpha_composite(Image.fromarray(mk))
    frames.append(fr.convert("RGB"))
for i, fr in enumerate(frames): fr.save(f"zbf_{i:02d}.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30000/1001", "-i", "zbf_%02d.png", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "zb.mp4"], check=True)
print("zb.mp4", N, "프레임")
