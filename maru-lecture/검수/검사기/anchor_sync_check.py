# 아나운서(하이젠 인삿말·끝인사 클립) 입 싱크 + 매끈함 검사기 — 민석 11/3 「클로징 아나운서 싱크 안 맞음」 → 시안 B(부드럽게+광학흐름) 확정 · 「검수할 때 이것도 하도록」
#  ① 입 싱크: 클립 받아쓰기 단어 시작 ↔ 타입캐스트 단어 시작을 warp 지도로 옮겨 비교(오더09 lipcheck2) → 최대 ≤ 0.1초. **한 단어라도 넘으면 걸림**(13강 v3b 「견적」 0.156 이 통과로 올라간 구멍)
#  ② 소리 시작점(onsetcheck): 쉼 뒤 말 시작 ≤ 0.1초
#  ③ 매끈함: 50ms 배속 꺾임 최대 ≤ 0.55 (옛 warp2 13강 0.6·0.8 · 11강 0.76·0.78 「틱틱」 / 시안 B 0.18·0.5) · 배속 0.4~2.5 밖이면 걸림
#  ④ 방식: warp json mode = flow(광학흐름) 아니면 걸림(민석 11/3 확정. --allow-blend 로만 풀림)
# 실행(_작업 에서): ~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py NN [--timeline NN강/타임라인_vN.json] [--allow-blend]
#        또는 warp json 직접: … anchor_sync_check.py --warp a.json [b.json …]
#  받아쓰기는 <wav>_words.json 캐시를 쓰고 없으면 mlx_whisper(무거움 → heavy_run.sh asr 로 감쌀 것). 종료코드 0 통과 · 1 걸림.
import sys, os, json, glob, subprocess, argparse, numpy as np
W = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # _작업
L = os.path.join(W, "오더09_공용")
PY = os.path.expanduser("~/.venvs/tts/bin/python")
LIP_MAX, JERK_MAX, SP_LO, SP_HI = 0.1, 0.55, 0.4, 2.5   # 꺾임 = 50ms 배속 다음 50ms 배속과의 차 최대(지도가 0.001초 반올림이라 10ms 로 재면 잡음)
ap = argparse.ArgumentParser(); ap.add_argument("lec", nargs="?"); ap.add_argument("--timeline"); ap.add_argument("--warp", nargs="*"); ap.add_argument("--allow-blend", action="store_true")
a = ap.parse_args()

def find(p, base):
    for b in [base, W, os.path.join(W, a.lec + "강") if a.lec else W, os.path.join(W, a.lec + "강", "work") if a.lec else W]:
        q = os.path.normpath(os.path.join(b, p))
        if os.path.exists(q): return q
    return None
items = []
if a.warp: items = [os.path.abspath(x) for x in a.warp]
else:
    tlp = a.timeline or sorted(glob.glob(os.path.join(W, f"{a.lec}강", "타임라인_v*.json")), key=os.path.getmtime)[-1]
    tl = json.load(open(os.path.join(W, tlp) if not os.path.isabs(tlp) else tlp)); print("타임라인", tlp)
    for an in tl["anchors"]:
        c = find(an["clip"], os.path.join(W, f"{a.lec}강", "work"))
        j = c and os.path.splitext(c)[0] + ".json"
        items.append(j if j and os.path.exists(j) else f"!{an['name']}: warp json 없음 ({an['clip']})")
bad = []
for j in items:
    if j.startswith("!"): print("✗", j[1:]); bad.append(j); continue
    info = json.load(open(j)); jd = os.path.dirname(j); name = os.path.basename(j)
    cw = find(os.path.splitext(info["clip"])[0] + ".wav", jd); tw = find(info["target"], jd)
    m = np.array(info["map"])[::5]; sp = np.diff(m[:, 1]) / np.diff(m[:, 0]); jerk = float(np.abs(np.diff(sp)).max())
    lip = json.loads(subprocess.run([PY, os.path.join(L, "lipcheck2.py"), cw, tw, j], capture_output=True, text=True).stdout and open(j.replace(".json", "_lip2.json")).read() or "{}")
    on = subprocess.run(["python3", os.path.join(L, "onsetcheck.py"), cw, tw, j], capture_output=True, text=True).stdout.strip().splitlines()
    on = eval(on[-1].split(" ", 1)[1]) if on else {}
    mode = info.get("mode", "blend(옛 warp_clip2)")
    why = []
    if not lip or lip.get("max", 9) > LIP_MAX: why.append(f"입싱크 최대 {lip.get('max')} > {LIP_MAX} {lip.get('over')}")
    if on.get("max", 9) > LIP_MAX: why.append(f"소리시작 최대 {on.get('max')} {on.get('over_0_1')}")
    if jerk > JERK_MAX: why.append(f"배속 꺾임 {jerk:.2f} > {JERK_MAX}")
    if sp.min() < SP_LO - 0.01 or sp.max() > SP_HI + 0.01: why.append(f"배속 {sp.min():.2f}~{sp.max():.2f}")
    if mode != "flow" and not a.allow_blend: why.append(f"방식 {mode} ≠ flow(시안 B)")
    print(("✗ " if why else "✓ ") + f"{name} · 입싱크 중앙 {lip.get('median', 0):.3f} 최대 {lip.get('max', 0):.3f} · 소리시작 최대 {on.get('max')} · 배속 {sp.min():.2f}~{sp.max():.2f} · 꺾임 {jerk:.2f} · {mode}"
          + ("\n    걸림: " + " / ".join(why) if why else ""))
    if why: bad.append(name)
print("결과:", "통과" if not bad else f"걸림 {len(bad)}")
sys.exit(1 if bad else 0)
