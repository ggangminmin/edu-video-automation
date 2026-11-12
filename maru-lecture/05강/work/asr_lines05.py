# 05강 모든 자막 줄 시작 받아쓰기 확인(오더44 · newline_onset_check --asr 와 같은 잣대를 판정불가 줄 포함 전부에):
#  깨끗한 음성(타임라인 audio 대로) [시작+0.09−0.03, +1.3] 이 그 줄 첫 어절 앞 2글자로 시작 · [−0.9, −0.03] 끝 4글자에 그 2글자 없음
# 실행(work): heavy_run asr ~/.venvs/tts/bin/python asr_lines05.py v1
import sys, json, re, subprocess, numpy as np, mlx_whisper
VER = sys.argv[1]; SR = 16000
tl = json.load(open(f"../타임라인_{VER}.json"))
def load(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
C = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src") or "work/v090.wav"
    if k not in C: C[k] = load("../" + k)
    y = C[k][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y
def asr(a, b):
    y = V[max(0, int(a * SR)):int(b * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip() if len(y) > SR * 0.2 else ""
NUM = {"1": "일", "2": "이", "3": "삼", "4": "사", "5": "오", "10": "십"}
def kn(t):
    t = re.sub(r"\d+", lambda m: NUM.get(m.group(), m.group()), t)
    return re.sub(r"[^가-힣A-Za-z]", "", t)
rows = []
for x in tl["subs"]:
    t = x["start"] + 0.09
    aft, bef = asr(t - 0.03, t + 1.3), asr(t - 0.9, t - 0.03)
    w0 = kn(x["text"].split()[0])[:2]; A, B = kn(aft), kn(bef)
    ok = A.startswith(w0) and w0 not in B[-4:]
    rows.append(dict(n=x["n"], slide=x["slide"], start=round(x["start"], 3), text=x["text"], ok=ok, after=aft, before=bef))
    print(("✓" if ok else "?"), x["n"], round(x["start"], 2), x["text"][:18], "| 뒤:", aft[:14], "| 앞:", bef[-10:], flush=True)
json.dump(rows, open(f"../검사_{VER}/asr_lines.json", "w"), ensure_ascii=False, indent=1)
print("확인 필요", sum(not r["ok"] for r in rows), "/", len(rows))
