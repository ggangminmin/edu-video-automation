# 반장 공유(14강 방식) 검사: 슬라이드마다 긴 무음(≥0.6초) 수 = 문장 수−1 이면, 문장 시작을 긴 무음 끝에 순서대로 대응 → 지금 시각과 비교
import json, re, subprocess
D = json.load(open("../타임라인_초안.json")); V = json.load(open("../타임라인_v1.json"))
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "v090.wav", "-af", "silencedetect=n=-40dB:d=0.6", "-f", "null", "-"], capture_output=True, text=True).stderr
LS = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]))
off = {s["slide"]: s["src_offset"] for s in D["slides"] if "src_offset" in s}
body = [x for x in D["subs"] if "part" not in x]
fix = {}; rep = []
for s in sorted(off):
    ls = [x for x in body if x["slide"] == s]
    sent = [x for x in ls if x.get("how") == "문장시작"]
    a = ls[0]["voice_on"] - off[s]; b = [y for y in D["slides"] if y["slide"] == s][0]["voice_end"] - off[s]
    inner = [e for st, e in LS if a + 0.05 < e < b]
    srcs = [round(x["voice_on"] - off[s], 3) for x in sent[1:]]
    if len(inner) == len(srcs):
        d = [round(t - e, 3) for t, e in zip(srcs, inner)]
        bad = [(x["text"][:14], t, round(e, 3)) for x, t, e in zip(sent[1:], srcs, inner) if abs(t - e) > 0.03]
        rep.append(f"{s}: 문장 {len(sent)} · 긴무음 {len(inner)} 일치 · 어긋남 {len(bad)} {bad}")
        for x, e in zip(sent[1:], inner):
            if abs((x["voice_on"] - off[s]) - e) > 0.03: fix[x["text"]] = round(e, 3)
    else:
        rep.append(f"{s}: 문장 {len(sent)} · 긴무음 {len(inner)} ✗(수 다름 — 받아쓰기 대응 유지)")
print("\n".join(rep)); print("고칠 문장", len(fix)); json.dump(fix, open("sent_fix.json", "w"), ensure_ascii=False, indent=1)
