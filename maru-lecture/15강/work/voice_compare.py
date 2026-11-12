# 끝인사 클립 목소리 vs 본문 타입캐스트(0.9배) — 음높이(F0 중앙·범위) · 말 속도(글자/초) · 음량(LUFS) 실측
import numpy as np, subprocess, re, json
def load(p, ss=0, t=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", p, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.int16).astype(np.float32) / 32768
def f0(x, sr=16000):
    fr, hop = 640, 160; out = []
    for i in range(0, len(x) - fr, hop):
        w = x[i:i+fr] * np.hanning(fr)
        if np.sqrt((w**2).mean()) < 0.02: continue
        ac = np.correlate(w, w, "full")[fr-1:]; lo, hi = sr // 400, sr // 70
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] / ac[0] > 0.45: out.append(sr / k)
    a = np.array(out); return np.median(a), np.percentile(a, 10), np.percentile(a, 90)
def lufs(p, ss=0, t=None):
    cmd = ["ffmpeg", "-hide_banner", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", p, "-af", "ebur128", "-f", "null", "-"]
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(cmd, capture_output=True, text=True).stderr)[-1])
tl = json.load(open("../타임라인_초안.json"))
notes = json.load(open("../notes_clean.json"))
nch = lambda s: len(re.sub(r"[^가-힣0-9A-Za-z]", "", s))
SEG = json.load(open("../../아나운서/segments.json"))["15"]
c0, c1 = [x / 0.9 for x in SEG["close"]]                       # 타입캐스트 클로징(0.9배 시간)
rows = {
  "본문 2~24번(타입캐스트 0.9배)": ("v090.wav", 0, c0, sum(nch(" ".join(p)) for p in notes[1:24])),
  "타입캐스트 클로징 25번(안 씀)": ("v090.wav", c0, c1 - c0, nch(notes[24][0])),
  "끝인사 클립(하이젠 0.9배)":    ("../아나운서/15_끝인사_090.wav", 0, None, nch(notes[24][0])),
  "인삿말 클립(하이젠 0.9배)":    ("../아나운서/15_인삿말_090.wav", 0, None, None),
}
B = json.load(open("../아나운서/meta.json"))
for k, (p, ss, t, n) in rows.items():
    x = load(p, ss, t); m, lo, hi = f0(x)
    # 말 속도 = 글자 / 실제 말 길이(무음 0.25초 넘는 곳 뺌)
    o = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", p, "-af", "silencedetect=n=-40dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", o)]; en = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", o)]
    tot = len(x) / 16000; sil = sum(e - s for s, e in zip(st, en))
    rate = f"{n / (tot - sil):.2f}" if n else "-"
    print(f"{k} | F0 중앙 {m:.0f}Hz (10~90% {lo:.0f}~{hi:.0f}) | 말 속도 {rate} 글자/초 | 음량 {lufs(p, ss, t):.1f} LUFS")
