# pS 11/3: scene_sub 보류·판정불가·너무빠름 줄 → 깨끗한 음성(타임라인대로 깐 소리, 출력 시각)에서 말 시작 실측 + 잘라 받아쓰기로 확인
#  말 시작 = 자막 −0.35~+0.45 안: −40dB 무음(≥0.03) 끝이 있으면 가장 늦은 「자막+0.45 이전」 무음 끝 · 없으면 음량 골짜기(30ms 평활) 뒤 +6dB
#  받아쓰기: 앞 = [말시작−1.0, 말시작] 끝에 이 줄 첫 2글자 없어야 · 뒤 = [말시작, +1.0] 가 첫 2글자로 시작해야 (오인 표기는 눈 대조)
#  자막→말 = 말시작 − 자막시작 · 기준 −0.017~0.177
# 실행: heavy_run.sh asr ~/.venvs/tts/bin/python 오더21/hold_raw.py  → 오더21/hold_raw.json
import json, re, subprocess, sys, os, numpy as np, mlx_whisper
SR = 16000; JOB = {12: ("v3c", "타임라인_v3c.json"), 13: ("v3b", "타임라인_v3.json"), 15: ("v3b", "타임라인_v3.json")}
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
nz = lambda t: re.sub(r"[^가-힣0-9]", "", t)
def asr(x):
    p = "/private/tmp/claude-501/hold_raw_tmp.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", p], input=x.astype(np.float32).tobytes())
    return mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip()
out = []
for N, (ver, tln) in JOB.items():
    tl = json.load(open(f"{N}강/{tln}")); ss = json.load(open(f"{N}강/검사_{ver}/scene_sub.json"))
    rows = {r["n"]: r for r in ss["sync"] if r["result"] != "OK"}
    T = tl["total"]; v = np.zeros(int((T + 1) * SR), np.float32); cache = {}
    for a in tl["audio"]:
        p = f"{N}강/" + a["src"] if a.get("src") else f"{N}강/work/v090.wav"
        if p not in cache: cache[p] = load(p)
        seg = cache[p][int(round(a["src_from"] * SR)):int(round(a["src_to"] * SR))] * a.get("gain", 1.0)
        i0 = int(round(a["out"] * 1000)) * SR // 1000; v[i0:i0 + len(seg)] += seg[:len(v) - i0]
    n10 = SR // 100; m = len(v) // n10; d = 20 * np.log10(np.sqrt((v[:m * n10].reshape(m, n10) ** 2).mean(1)) + 1e-9); ds = np.convolve(d, np.ones(3) / 3, "same")
    S = {x["n"]: x for x in tl["subs"]}
    for n, r in sorted(rows.items()):
        x = S[n]; t0 = x["start"]; a, b = int((t0 - 0.35) * 100), int((t0 + 0.45) * 100)
        ends = [i for i in range(a, b) if d[i - 1] < -40 and d[i] >= -40 and all(d[i - 3:i] < -40)]
        if ends: on = ends[-1] / 100; how = "무음 끝"
        else:
            k = a + int(np.argmin(ds[a:b])); j = k
            while j < b and ds[j] < ds[k] + 6: j += 1
            on = j / 100; how = f"골짜기({ds[k]:.0f}dB) +6"
        A = asr(v[int((on - 1.0) * SR):int(on * SR)]); B = asr(v[int(on * SR):int((on + 1.0) * SR)])
        head = nz(x["text"])[:2]; lead = round(on - t0, 3)
        ok_asr = (head not in nz(A)[-4:]) and nz(B).startswith(head)
        verdict = "정상" if -0.017 <= lead <= 0.177 else ("너무빠름" if lead > 0.177 else "늦음")
        out.append(dict(강=N, 판=ver, 줄=n, 자막=x["text"], 검사기=r["result"], 검사기_lead=r.get("lead"), 자막시작=round(t0, 3), 말시작=on, 방법=how, 자막_말=lead, 앞1초=A, 뒤1초=B, 받아쓰기맞음=ok_asr, 판단=verdict))
        print(out[-1], flush=True)
json.dump(out, open("오더21/hold_raw.json", "w"), ensure_ascii=False, indent=1)
