# 11강 v5 경계 ±2프레임 검사(pS/pT 지시 · 오더09_공용/edge16.py 방식 확장)
#  장 컷 26곳 전부: 프레임마다 ① 보이는 장(앞/뒤 슬라이드 원본 중 가까운 쪽, 아나운서·자막바·로고 자리 빼고)
#  ② 보이는 자막(앞 장 마지막 줄 / 새 장 첫 줄 — 자막바 자리에서 bar+자막 합성본과 가까운 쪽)
#  ③ 표지→2 · 26→27 은 아나운서 유무(아나운서 자리에서 장 원본과 다른 화소 > 4000)
#  기준: 장 컷 프레임 = 계획 프레임(round(start·fps)) · 자막 = 장과 같은 프레임에 바뀜 · 아나운서 있음 ⇔ 아나운서 장
# 실행(_작업/11강/work): python3 edge_v5.py ../11강_v5.mp4 ../타임라인_v5.json 결과.json
import sys, json, subprocess, numpy as np
from PIL import Image
V, TLP, OUT = sys.argv[1:4]; FPS = 30000 / 1001
tl = json.load(open(TLP)); S = sorted(tl["slides"], key=lambda s: s["slide"]); SUB = tl["subs"]
AX = {1: 447, 27: 952}; AW = {1: 700, 27: 700}
def png(n): return np.asarray(Image.open(f"../slides/s-{n:02d}.png").convert("RGB").resize((1920, 1080)), np.int16)
bar = Image.open("bar.png").convert("RGBA")
def subimg(n):
    im = bar.copy(); im.alpha_composite(Image.open(f"sub_v5/{n:03d}.png").convert("RGBA")); return np.asarray(im, np.int16)
def frame(k):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(k - 0.4) / FPS:.5f}", "-i", V, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(1080, 1920, 3).astype(np.int16)
Y0, Y1, X0, X1 = 930, 990, 300, 1620                  # 자막 글자 자리
out = []; bad = 0
MAXT = float(__import__("os").environ.get("MAXT", "1e9"))
for i in range(1, len(S)):
    if S[i]["start"] > MAXT: break
    pa, pb = S[i - 1]["slide"], S[i]["slide"]; Pa, Pb = png(pa), png(pb)
    kc = int(round(S[i]["start"] * FPS))
    la = [x for x in SUB if x["slide"] == pa][-1]["n"]; lb = [x for x in SUB if x["slide"] == pb][0]["n"]
    Sa, Sb = subimg(la), subimg(lb)
    m = np.ones((1080, 1920), bool); m[880:] = False; m[:150, 1540:] = False
    for s_, x in AX.items():
        if s_ in (pa, pb): m[:, x:x + AW[s_]] = False
    for k in range(kc - 2, kc + 3):
        f = frame(k)
        sl = pa if np.abs(f - Pa).max(2)[m].mean() < np.abs(f - Pb).max(2)[m].mean() else pb
        fr = f[Y0:Y1, X0:X1]; da = np.abs(fr - Sa[Y0:Y1, X0:X1, :3]).mean(); db = np.abs(fr - Sb[Y0:Y1, X0:X1, :3]).mean()
        sb = la if da < db else lb
        want_sl = pa if k < kc else pb; want_sb = la if k < kc else lb
        ok = sl == want_sl and sb == want_sb
        ann = None
        if 1 in (pa, pb) or 27 in (pa, pb):
            s_ = 1 if 1 in (pa, pb) else 27; x = AX[s_]; ref = Pa if sl == pa else Pb
            am = np.zeros((1080, 1920), bool); am[40:880, x + 150:x + AW[s_] - 150] = True
            ann = int((np.abs(f - ref).max(2)[am] > 40).sum()) > 4000
            ok = ok and ann == (sl == s_)
        bad += not ok
        out.append(dict(cut=f"{pa}→{pb}", frame=k, plan_cut=kc, t=round(k / FPS, 3), slide=int(sl), sub=int(sb), announcer=ann, ok=bool(ok)))
for o in out:
    if not o["ok"]: print("걸림", o)
res = dict(경계=len(S) - 1, 프레임=len(out), 걸림=bad, 판정="통과" if not bad else "걸림", 프레임별=out)
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=0)
print("경계", len({o["cut"] for o in out}), "곳 ±2프레임", "통과" if not bad else f"걸림 {bad}"); sys.exit(1 if bad else 0)
