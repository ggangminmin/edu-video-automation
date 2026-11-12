# 08강 새 줄 시작 실소리 보정(18강 onset_v4 · 20강 make_tl_v4c 방식) — newline_onset_check --all 결과(json)를 받아
#  ① 걸림(늦음·너무빠름) 줄: 검사기가 잰 실소리(쉼 끝 −50dB 30ms 상승) 와 다른 후보들 중
#     [t−0.9, t] 받아쓰기 끝에 첫 어절 없음 + [t, t+1.3] 첫 어절로 시작 하는 가장 이른 후보 → 자막 시작 = t − 0.09
#  ② 판정불가(이어진 말) 줄: 지금 시작으로 받아쓰기 확인만(✓면 그대로)
#  ③ MAN = 손 실측값(받아쓰기 자르기로 확인한 것)
# 실행(cwd = 08강/work): heavy_run.sh asr ~/.venvs/tts/bin/python onset08.py <in 타임라인> <checker json> <out 타임라인> <report json>
import sys, json, re, subprocess, numpy as np, mlx_whisper
tin, cj, tout, rep = sys.argv[1:5]
tl = json.load(open(tin)); ck = json.load(open(cj)); SR = 16000
MAN = json.load(open("onset_man.json")) if __import__("os").path.exists("onset_man.json") else {}
def load(f): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
cache = {}; V = np.zeros(int((tl["total"] + 1) * SR), np.float32)
for s in tl["audio"]:
    k = s.get("src"); f = "v090.wav" if k is None else k.replace("work/", "")
    if f not in cache: cache[f] = load(f)
    y = cache[f][int(s["src_from"] * SR):int(s["src_to"] * SR)] * float(s.get("gain", 1.0)); o = int(round(s["out"] * SR)); V[o:o + len(y)] += y[:max(0, len(V) - o)]
def asr(t0, t1):
    y = V[max(0, int(t0 * SR)):int(t1 * SR)]
    return mlx_whisper.transcribe(y, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"].strip() if len(y) > SR * 0.2 else ""
def kn(t): return re.sub(r"[^가-힣0-9A-Za-z]", "", t)
NUM = {"일": "1", "이": "2", "삼": "3", "사": "4", "오": "5"}
def heads(text):
    w = kn(text.split()[0]); h = {w[:2]}
    if w[0] in NUM: h.add(NUM[w[0]] + w[1:2])
    return h
def check(on, text):
    aft, bef = kn(asr(on - 0.03, on + 1.3)), kn(asr(on - 0.9, on - 0.03))
    hs = heads(text)
    return any(aft.startswith(h) for h in hs) and not any(h in bef[-4:] for h in hs), aft[:10], bef[-8:]
S = tl["subs"]; byn = {s["n"]: s for s in S}; out = []
for r in ck["rows"]:
    s = byn[r["n"]]; k = S.index(s)
    if s["text"] in MAN:
        t = MAN[s["text"]]; ok, aft, bef = check(t, s["text"])
        out.append(dict(n=r["n"], text=s["text"], was=round(s["start"], 3), now=round(t - 0.09, 3), why="손 실측", asr_ok=ok, after=aft, before=bef))
        s["start"] = t - 0.09; s["voice_on"] = round(t, 3); S[k - 1]["end"] = s["start"]; s["how"] = "onset08 손 실측"; continue
    if r["result"] == "OK": continue
    if r["result"] == "판정불가":
        ok, aft, bef = check(s["start"] + 0.09, s["text"])
        out.append(dict(n=r["n"], text=s["text"], was=round(s["start"], 3), now=round(s["start"], 3), why="판정불가 → 받아쓰기 확인만", asr_ok=ok, after=aft, before=bef)); continue
    cs = []
    if r["onset"] is not None: cs.append((r["onset"], "검사기"))
    cs += [(c["onset"], "다른후보 " + c["how"]) for c in r.get("alt", [])]
    best = None; tried = []
    for t, why in sorted(cs):
        ok, aft, bef = check(t, s["text"]); tried.append(dict(t=t, why=why, ok=ok, after=aft, before=bef))
        if ok and best is None: best = (t, why)
    row = dict(n=r["n"], text=s["text"], was=round(s["start"], 3), result=r["result"], tried=tried)
    if best is None:
        row.update(now=None, why="후보 전부 받아쓰기 ✗ → 손으로"); out.append(row); continue
    t, why = best
    if k > 0 and t - 0.09 <= S[k - 1]["start"] + 0.5:
        row.update(now=None, why="앞 줄과 0.5초 안 → 손으로"); out.append(row); continue
    s["start"] = t - 0.09; s["voice_on"] = round(t, 3); S[k - 1]["end"] = s["start"]; s["how"] = f"onset08({why} · 받아쓰기✓)"
    row.update(now=round(t - 0.09, 3), why=why); out.append(row)
for a, c in zip(S, S[1:]): assert a["end"] <= c["start"] + 1e-6 and c["start"] > a["start"] + 0.3, (a["n"], c["n"])
json.dump(tl, open(tout, "w"), ensure_ascii=False, indent=1); json.dump(out, open(rep, "w"), ensure_ascii=False, indent=1)
for o in out: print({k: v for k, v in o.items() if k != "tried"}, *[f"\n     후보 {x['t']} {x['why']} {'✓' if x['ok'] else '✗'} 앞「{x['before']}」 뒤「{x['after']}」" for x in o.get("tried", [])])
print("고침", sum(1 for o in out if o.get("now") is not None and o.get("now") != o.get("was")), "· 손으로", sum(1 for o in out if o.get("now") is None))
