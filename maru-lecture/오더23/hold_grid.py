# 오더23: hold 줄 말 시작 범위 = 자막 시작 기준 −0.05~+0.45(0.1 간격)에서 잘라 「앞 1.2초」 받아쓰기 끝에 그 줄 첫 말(2글자)이 있나 → 처음 나타나는 칸 사이가 말 시작
# 실행: heavy_run.sh asr ~/.venvs/tts/bin/python 오더23/hold_grid.py NN 타임라인 줄,… → 오더23/hold_grid_NN.json
import sys, json, re, subprocess, os, mlx_whisper
N, TLN, NS = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
tl = json.load(open(f"{N}강/{TLN}")); S = {x["n"]: x for x in tl["subs"]}; nz = lambda t: re.sub(r"[^가-힣0-9]", "", t)
def src(t):
    for a in tl["audio"]:
        a0 = a["out"]; a1 = a0 + a["src_to"] - a["src_from"]
        if a0 <= t <= a1 and not a.get("src"): return a["src_from"] + t - a0
def asr(a, b):
    p = f"/tmp/hg_{N}_{a:.3f}.wav"; subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f"{N}강/work/v090_16k.wav", p])
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False); os.remove(p)
    return nz("".join(s["text"] for s in r["segments"]))
res = []
for n in NS:
    x = S[n]; head = nz(x["text"])[:2]; prevtail = nz(S[n - 1]["text"])[-2:]; row = []
    for d in (-0.05, 0.05, 0.15, 0.25, 0.35, 0.45):
        c = src(x["start"] + d); A = asr(c - 1.2, c); row.append((d, A[-6:], head in A[-5:]))
    first = next((d for d, a, h in row if h), None); last_no = max((d for d, a, h in row if not h and (first is None or d < first)), default=None)
    r = dict(n=n, text=x["text"], head=head, prev_tail=prevtail, grid=row, onset_between=[last_no, first],
             판정=("너무빠름" if last_no is not None and last_no >= 0.177 else ("정상 범위" if first is not None and first <= 0.25 else "확인")))
    res.append(r); print(r)
json.dump(res, open(f"오더23/hold_grid_{N}.json", "w"), ensure_ascii=False, indent=1)
