#!/usr/bin/env python3
"""장 컷 경계 ±2프레임 검사기 (공용 · 판정 전 필수) — 반복 실수 2회(14강 v2 p9 반려 · 11강 v5 자체 검사)로 만든 것.

잡는 것: 슬라이드 concat 이 PNG 를 25fps 칸으로 반올림해 장 컷이 ±1프레임 흔들리거나, 아나운서 등장·퇴장(overlay enable)과
         장 컷이 서로 다른 프레임으로 반올림되는 것.
  장 컷마다 계획 프레임 kc = round(start × 29.97) 의 kc−2 … kc+2 다섯 프레임에서
  ① 보이는 장 = 앞/뒤 슬라이드 원본 PNG 중 가까운 쪽(아나운서·자막바·로고 자리 빼고)  → k<kc 앞 장 · k≥kc 새 장
  ② 보이는 자막 = 자막 글자 자리(y930~990)가 kc−3 프레임(앞 자막)·kc+3 프레임(새 자막) 중 어느 쪽과 같은지 → 장과 같은 프레임에 바뀜
  ③ 아나운서 장(표지 = 첫 장 · 끝인사 = 마지막 장) 경계: 아나운서 자리에서 장 원본과 다른 화소 > 4000 ⇔ 아나운서 장이 보임
  ④ (오더 24) 끝 검정: 타임라인 ending.black 구간 프레임 3장 밝기 ≤ 3 · 영상 길이(컨테이너·영상 스트림) = total ±1.5프레임
기준: 걸림 0.

사용(_작업 에서):  python3 검수/검사기/edge_check.py NN --video NN강/NN강_vN.mp4 --timeline NN강/타임라인_vN.json
                    [--slides NN강/slides] [--anc-x 인삿말:447,끝인사:952] [--anc-w 700] [--out 결과.json]
  · 아나운서 x 는 타임라인 anchors 의 "x" 를 쓰고, 없으면 --anc-x(없으면 인삿말 934 · 끝인사 952).
  · 프레임 25장/경계를 ffmpeg 로 뽑음 — 가벼워서 heavy_run 불필요(27경계 ≈ 1~2분).
결과: 화면 + --out(기본 검수/검사기/edge_NN_<영상이름>.json) · 종료코드 0 통과 · 1 걸림.
검산(11/2): 끝 검정 = 11강_v5b 걸림(190) · 11강_v4 통과(0). 경계 = 11강_v5.mp4 → 걸림 4(2→3·18→19·24→25 늦음 · 20→21 이름) · 11강 v5b 시험 45초 → 통과.
"""
import sys, os, json, argparse, subprocess, numpy as np
from PIL import Image
ap = argparse.ArgumentParser(); ap.add_argument("lec"); ap.add_argument("--video", required=True); ap.add_argument("--timeline", required=True)
ap.add_argument("--slides"); ap.add_argument("--anc-x", default=""); ap.add_argument("--anc-w", type=int, default=700); ap.add_argument("--out")
ap.add_argument("--maxt", type=float, default=1e9, help="이 시각까지의 경계만(시험 렌더용)")
A = ap.parse_args(); FPS = 30000 / 1001
tl = json.load(open(A.timeline)); S = sorted(tl["slides"], key=lambda s: s["slide"])
SD = A.slides or os.path.join(os.path.dirname(os.path.abspath(A.timeline)), "slides")
ax = {"인삿말": 934, "끝인사": 952}
for kv in filter(None, A.anc_x.split(",")): k, v = kv.split(":"); ax[k] = int(v)
for a in tl.get("anchors", []):
    if "x" in a and a["name"] not in {kv.split(":")[0] for kv in filter(None, A.anc_x.split(","))}: ax[a["name"]] = a["x"]
ANN = {S[0]["slide"]: ax["인삿말"], S[-1]["slide"]: ax["끝인사"]}       # 아나운서 장 → x
# 🆕11/3 팀장(오더33 등장 0.5초 알파 페이드): anchors/ending 에 fade_in 있으면 등장 판정 = 장 컷 + fade_in/2 프레임(알파≥50%) · 컷~그 사이는 「아나운서 없음」 허용
FIN = {}
for a in tl.get("anchors", []):
    f_ = a.get("fade_in", tl.get("ending", {}).get("fade_in", 0)) or 0
    if f_ > 0: FIN[S[0]["slide"] if a["name"] == "인삿말" else S[-1]["slide"]] = f_
def png(n): return np.asarray(Image.open(f"{SD}/s-{n:02d}.png").convert("RGB").resize((1920, 1080)), np.int16)
def frame(k):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(k - 0.4) / FPS:.5f}", "-i", A.video, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(1080, 1920, 3).astype(np.int16)
Y0, Y1, X0, X1 = 930, 990, 300, 1620
out = []; bad = 0
for i in range(1, len(S)):
    if S[i]["start"] > A.maxt: break
    pa, pb = S[i - 1]["slide"], S[i]["slide"]; Pa, Pb = png(pa), png(pb); kc = int(round(S[i]["start"] * FPS))
    m = np.ones((1080, 1920), bool); m[880:] = False; m[:150, 1540:] = False
    for s_, x in ANN.items():
        if s_ in (pa, pb): m[:, max(0, x):x + A.anc_w] = False
    Ra, Rb = frame(kc - 3)[Y0:Y1, X0:X1], frame(kc + 3)[Y0:Y1, X0:X1]
    for k in range(kc - 2, kc + 3):
        f = frame(k)
        sl = pa if np.abs(f - Pa).max(2)[m].mean() < np.abs(f - Pb).max(2)[m].mean() else pb
        fr = f[Y0:Y1, X0:X1]; sub = "앞" if np.abs(fr - Ra).mean() < np.abs(fr - Rb).mean() else "새"
        want_sl = pa if k < kc else pb; want_sub = "앞" if k < kc else "새"
        ok = sl == want_sl and sub == want_sub; ann = None
        s_ = pa if pa in ANN else (pb if pb in ANN else None)
        if s_ is not None:
            x = ANN[s_]; ref = Pa if sl == pa else Pb
            am = np.zeros((1080, 1920), bool); am[40:880, max(0, x + 150):x + A.anc_w - 150] = True
            ann = int((np.abs(f - ref).max(2)[am] > 40).sum()) > 4000
            fade_ok = s_ == pb and s_ in FIN and kc <= k < kc + round(FIN[s_] / 2 * FPS) and not ann   # 페이드 앞 절반: 없어도 됨
            ok = ok and (ann == (sl == s_) or fade_ok)
        bad += not ok
        out.append(dict(cut=f"{pa}→{pb}", frame=k, plan_cut=kc, t=round(k / FPS, 3), slide=int(sl), sub=sub, announcer=ann, ok=bool(ok)))
    if pb in FIN:   # 등장 판정 프레임(컷 + fade_in/2): 아나운서 보여야 함
        k = kc + round(FIN[pb] / 2 * FPS); f = frame(k); x = ANN[pb]
        am = np.zeros((1080, 1920), bool); am[40:880, max(0, x + 150):x + A.anc_w - 150] = True
        ann = int((np.abs(f - Pb).max(2)[am] > 40).sum()) > 4000; bad += not ann
        out.append(dict(cut=f"{pa}→{pb}", frame=k, plan_cut=kc, t=round(k / FPS, 3), slide=int(pb), sub="페이드중간", announcer=ann, ok=bool(ann)))
# ④ 🆕오더 24 끝 검정·길이: 타임라인 ending.black 구간(마지막 0.9초) 프레임 3장 밝기 ≤ 3 · 영상 길이(컨테이너·영상 스트림) = total ±1프레임
#   (concat 맨 끝 반복 file 줄에 option framerate 없으면 마지막 패킷 PTS 역행 → 검정 대신 엔딩 카드 · 11 v5b·12~18 v3 실측 190)
TOT = tl["total"]; bk = tl.get("ending", {}).get("black", [TOT - 0.9, TOT])
def luma(t):
    b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", A.video, "-frames:v", "1", "-vf", "scale=64:36,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    return round(sum(b) / max(1, len(b)), 2) if b else None
end = []
for t in (bk[0] + 0.1, (bk[0] + bk[1]) / 2, bk[1] - 0.1):
    L = luma(t); okb = L is not None and L <= 3; bad += not okb; end.append(dict(t=round(t, 3), luma=L, ok=okb))
pr = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration:stream=duration", "-of", "json", A.video], capture_output=True, text=True).stdout
pj = json.loads(pr); dur_f = float(pj["format"]["duration"]); dur_v = float(pj["streams"][0].get("duration", dur_f))
okd = abs(dur_f - TOT) <= 1.5 / FPS and abs(dur_v - TOT) <= 1.5 / FPS; bad += not okd
end_res = dict(검정_프레임=end, 길이=dict(timeline_total=TOT, format=round(dur_f, 3), video=round(dur_v, 3), ok=okd))
print("끝 검정", [(e["t"], e["luma"]) for e in end], "· 길이", round(dur_f, 3), round(dur_v, 3), "/ total", TOT, "→", "통과" if all(e["ok"] for e in end) and okd else "걸림")
for o in out:
    if not o["ok"]: print("걸림", o)
n = len({o["cut"] for o in out})
res = dict(강=A.lec, video=A.video, timeline=A.timeline, 경계=n, 프레임=len(out), 끝=end_res, 걸림=bad, 판정="통과" if not bad else "걸림", 프레임별=out)
op = A.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), f"edge_{A.lec}_{os.path.splitext(os.path.basename(A.video))[0]}.json")
json.dump(res, open(op, "w"), ensure_ascii=False, indent=0)
print(f"{A.lec}강 경계 {n}곳 ±2프레임 + 끝 검정·길이", "통과" if not bad else f"걸림 {bad}(경계 프레임 + 끝 항목)", "→", op); sys.exit(1 if bad else 0)
