# 오더23: scene_sub 「보류(hold)」·지정 줄 → 깨끗한 음성(v090)을 자막 시작 기준 두 곳에서 잘라 받아쓰기(mlx, heavy_run asr 로 실행)
#  ① 자막+0.177(허용 최대 선행) 앞 1.3초 끝에 그 줄 첫 말(2글자)이 들어 있나 → 없으면 「너무 빠름」 의심
#  ② 자막−0.017 뒤 1.0초가 그 줄 첫 말로 시작하나 · 앞쪽에 첫 말이 이미 있나 → 있으면 「늦음」 의심
# 실행: heavy_run.sh asr ~/.venvs/tts/bin/python 오더23/hold_check.py NN 타임라인_xx.json 줄번호,…  → 오더23/hold_NN.json
import sys, json, re, subprocess, os, mlx_whisper
N, TLN, NS = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
tl = json.load(open(f"{N}강/{TLN}")); S = {x["n"]: x for x in tl["subs"]}; nz = lambda t: re.sub(r"[^가-힣0-9]", "", t)
def src(t):
    for a in tl["audio"]:
        a0 = a["out"]; a1 = a0 + a["src_to"] - a["src_from"]
        if a0 <= t <= a1 and not a.get("src"): return a["src_from"] + t - a0
def asr(a, b):
    p = f"/tmp/hold_{N}_{a:.3f}_{b:.3f}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", f"{N}강/work/v090_16k.wav", p])
    r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    os.remove(p); return nz("".join(s["text"] for s in r["segments"]))
out = []
for n in NS:
    x = S[n]; head = nz(x["text"])[:2]; s1 = src(x["start"] + 0.177); s2 = src(x["start"] - 0.017)
    if s1 is None or s2 is None: out.append(dict(n=n, why="소리 조각 밖")); continue
    A1, B2 = asr(s1 - 1.3, s1), asr(s2, s2 + 1.0); A2 = asr(s2 - 1.3, s2)
    early = head not in A1[-6:]; late = head in A2[-4:]
    out.append(dict(n=n, text=x["text"], head=head, before_max=A1[-10:], after_min=B2[:10], before_min=A2[-10:], 너무빠름_의심=early, 늦음_의심=late))
    print(out[-1])
json.dump(out, open(f"오더23/hold_{N}.json", "w"), ensure_ascii=False, indent=1)
