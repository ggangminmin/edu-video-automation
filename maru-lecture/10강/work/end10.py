# 10강: 장마다 실제 말끝(깨끗한 음성 10ms RMS > −40dB 가 30ms 이상 이어진 마지막 자리 끝) vs 타임라인 voice_end · 대기 실측
#  (silencedetect 는 무음 안 1샘플 블립에 무음을 둘로 갈라 말끝을 늦게 잡음 — 23장 768.84 vs 769.62)
import sys, json, subprocess, numpy as np
tl = json.load(open(sys.argv[1])); SR = 16000
def ld(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {None: ld("v090.wav")}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src")
    if k not in cache: cache[k] = ld(k.replace("work/", ""))
    y = cache[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
H = 160; db = 20 * np.log10(np.sqrt(np.mean(V[:len(V) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
L = max(s["slide"] for s in tl["slides"]); out = []
for s in tl["slides"]:
    a, b = int(s["start"] * 100), int(s["end"] * 100); loud = db[a:b] > -40; j = len(loud) - 1
    while j >= 2 and not (loud[j] and loud[j - 1] and loud[j - 2]): j -= 1
    real = (a + j + 1) / 100
    kind = "표지" if s["slide"] == 1 else "마지막" if s["slide"] == L else "문제" if s.get("wait") == "문제" or s.get("quiz_wait") else "스스로" if s.get("wait") == "스스로" or s.get("self_check_wait") else "넘김"
    want = {"문제": 5.5, "스스로": 3.0, "넘김": 1.71, "마지막": 3.5, "표지": None}[kind]
    ve = s.get("voice_end"); r = dict(slide=s["slide"], kind=kind, voice_end=ve and round(ve, 3), real_end=real, late=ve and round(ve - real, 3), wait_real=round(s["end"] - real, 3), want=want)
    r["bad"] = want is not None and abs(r["wait_real"] - want) > 0.05
    out.append(r); print(("✗" if r["bad"] else "✓"), r)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
