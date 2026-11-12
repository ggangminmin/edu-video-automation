# 문장 시작 검사(15강 sent_onset_check.py 방식 + 받아쓰기 확인) — cpp/mlx 가 1초 넘게 어긋난 문장이 많아서 추가
#  ① 슬라이드마다 긴 무음(≥0.6초) 수 = 문장 수−1 이면 문장 시작을 긴 무음 끝에 순서대로 대응 → 0.03초 넘게 다르면 후보
#  ② 후보마다 [t, t+1.3] 받아쓰기가 그 문장 첫 말로 시작하고 [t−1, t] 에 첫 말이 없으면 확정 → sent_fix.json(줄번호: 시각)
import json, re, subprocess, difflib, numpy as np, mlx_whisper
D = json.load(open("../타임라인_초안.json"))
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "v090.wav", "-af", "silencedetect=n=-40dB:d=0.6", "-f", "null", "-"], capture_output=True, text=True).stderr
LS = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", o)]))
off = {s["slide"]: s["src_offset"] for s in D["slides"] if "src_offset" in s}
body = [x for x in D["subs"] if "part" not in x]
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b): return re.sub(r"[^가-힣0-9]", "", mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
NUM = {"일":"1","이":"2","삼":"3","사":"4","오":"5"}
def head_ok(after, head):
    h2 = NUM.get(head[0], head[0]) + head[1:]
    return any(difflib.SequenceMatcher(None, after[:len(h)], h).ratio() >= 0.6 for h in (head, h2))
fix, rep, nm, same = {}, [], 0, 0
for s in sorted(off):
    ls = [(body.index(y), y) for y in body if y["slide"] == s]
    sent = [(i, y) for i, y in ls if y.get("how") == "문장시작"]
    a = ls[0][1]["voice_on"] - off[s]; b = [y for y in D["slides"] if y["slide"] == s][0]["voice_end"] - off[s]
    inner = [e for st, e in LS if a + 0.05 < e < b]
    if len(inner) != len(sent) - 1: nm += 1; rep.append(f"{s}: 문장 {len(sent)} · 긴무음 {len(inner)} 수 다름 → 대응 안 함"); continue
    for (i, y), e in zip(sent[1:], inner):
        t = round(y["voice_on"] - off[s], 3)
        if abs(t - e) <= 0.03: same += 1; continue
        head = n(y["text"])[:3]
        af_e, bf_e = tr(e, e + 1.3), tr(max(0, e - 1.0), e)
        ok = head_ok(af_e, head) and head[:2] not in bf_e[-3:]
        rep.append(f"{s} #{y['n']} {y['text'][:14]} 지금 {t} → 긴무음끝 {round(e,3)} | 뒤:{af_e[:8]} 앞:{bf_e[-8:]} → {'고침' if ok else '그대로(확인)'}")
        if ok: fix[i] = round(e, 3)
print("\n".join(rep)); print(f"일치 {same} · 고침 {len(fix)} · 대응 못한 슬라이드 {nm}")
json.dump(fix, open("sent_fix.json", "w"), indent=1)
