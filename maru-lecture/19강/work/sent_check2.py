# 오더15 · p9 판정: 문장 시작 자동 대응 안 된 슬라이드(긴 무음 수 ≠ 문장 수)의 문장 시작을 원음 첫 음소로 확인
#  각 문장 시작 t: [t, t+1.3] 받아쓰기 앞머리 ≈ 그 줄 첫 3글자(자모 ≥0.6) · [t−1, t] 끝에 그 줄 첫 2글자 없음 → OK
#  걸리면 후보(무음 끝 ≥0.05초 · 음량 골짜기 뒤 +6dB, t±1.2초) 중 조건 맞는 가장 이른 것 → sent_fix.json(줄번호: 시각)에 더함
# 실행: heavy_run.sh asr ~/.venvs/tts/bin/python sent_check2.py <슬라이드번호...>
import sys, os, json, re, subprocess, numpy as np
sys.argv_slides = [int(a) for a in sys.argv[1:]]
from fix_bound2_lib import tr, n, starts, has_head, DB, H
tl = json.load(open("../타임라인_초안.json")); off = {s["slide"]: s.get("src_offset", 0) for s in tl["slides"]}
BODY = [x for x in tl["subs"] if "part" not in x]
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "v090.wav", "-af", "silencedetect=n=-40dB:d=0.05", "-f", "null", "-"], capture_output=True, text=True).stderr
S5 = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]))
fix = {int(k): v for k, v in json.load(open("sent_fix.json")).items()} if os.path.exists("sent_fix.json") else {}
log = open("sent_check2.log", "w"); nok = nfix = nbad = 0
for sl in sys.argv_slides:
    for x in [y for y in BODY if y["slide"] == sl and y.get("how") == "문장시작"]:
        LI = BODY.index(x); t = round(x["voice_on"] - off[sl], 3); head = n(x["text"])[:3]
        af, bf = tr(t, t + 1.3), tr(max(0, t - 1.0), t)
        if starts(af, head) and not has_head(bf, head[:2]):
            nok += 1; msg = f"s{sl} #{x['n']} OK {t} | {x['text'][:16]} | 뒤:{af[:9]} 앞:{bf[-9:]}"
        else:
            prev_t = BODY[LI - 1]["voice_on"] - off[BODY[LI - 1]["slide"]] if LI else 0
            c = [e for s0, e in S5 if max(prev_t + 0.4, t - 1.2) <= e <= t + 1.2]
            a0 = int(max(prev_t + 0.4, t - 1.2) / H); b0 = int((t + 1.2) / H); seg = DB[a0:b0]
            for i in range(2, len(seg) - 2):
                if seg[i] == seg[i-2:i+3].min() and seg[i] < seg[max(0,i-20):i+20].max() - 6:
                    k = a0 + i
                    while k < a0 + i + 40 and DB[k] < DB[a0 + i] + 6: k += 1
                    c.append(round(k * H, 3))
            pick = None; rows = []
            for u in sorted(set(round(v, 3) for v in c)):
                a2, b2 = tr(u, u + 1.3), tr(max(0, u - 1.0), u); ok = starts(a2, head) and not has_head(b2, head[:2])
                rows.append((u, ok, a2[:8], b2[-8:]))
                if ok: pick = u; break
            if pick is not None and abs(pick - t) > 0.02: fix[LI] = pick; nfix += 1
            elif pick is None: nbad += 1
            else: nok += 1
            msg = f"s{sl} #{x['n']} 걸림 {t} → {pick} | {x['text'][:16]} | 뒤:{af[:9]} 앞:{bf[-9:]} | {rows}"
        print(msg, flush=True); log.write(msg + "\n")
log.close(); json.dump(fix, open("sent_fix.json", "w"), indent=1)
print(f"문장 시작 확인: OK {nok} · 고침 {nfix} · 못 고름 {nbad}")
