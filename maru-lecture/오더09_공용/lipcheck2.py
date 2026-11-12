# 입 싱크 검산 v2: lipcheck.py + 단어 시작 보정(whisper 가 무음 안에 찍은 시작 → 그 무음 끝 = 실제 소리 시작, 메모리 🩸11/2)
#  받아쓰기는 <wav>_words.json 캐시. 실행: ~/.venvs/tts/bin/python lipcheck2.py <clip.wav> <target.wav> <warp.json>
import sys, os, json, re, difflib, subprocess, numpy as np
cw, tw, wj = sys.argv[1:4]
info = json.load(open(wj)); cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
def words(p):
    c = p.replace(".wav", "_words.json")
    if not os.path.exists(c):
        import mlx_whisper
        r = mlx_whisper.transcribe(p, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", word_timestamps=True, condition_on_previous_text=False)
        json.dump(dict(text=r["text"], words=[(w["word"].strip(), round(w["start"], 3), round(w["end"], 3)) for s in r["segments"] for w in s["words"]]),
                  open(c, "w"), ensure_ascii=False, indent=0)
    d = json.load(open(c))
    y = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout, np.int16) / 32768.0
    H = 160; n = len(y) // H; fr = y[:n * H].reshape(n, H)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-7)
    out = []
    for w, a, b in d["words"]:
        t = re.sub(r"[^가-힣0-9]", "", w)
        if not t: continue
        i, k = int(a * 100), min(len(db), int(b * 100))
        if i < len(db) and db[i] < -40:                   # 무음 안 → 첫 소리 프레임으로
            j = i
            while j < k and db[j] < -40: j += 1
            a = j / 100
        out.append((t, a, b))
    return out, d["text"]
C, ctext = words(cw); T, ttext = words(tw)
sm = difflib.SequenceMatcher(None, [w[0] for w in C], [w[0] for w in T])
errs = []
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        c_t, t_t = C[a + k][1], T[b + k][1]
        if not (cs <= c_t <= ce and ts <= t_t <= te): continue
        u_voice = cs + (t_t - ts); u_mouth = cs + float(np.interp(c_t - cs, cl, tau))
        errs.append((C[a + k][0], round(u_mouth - u_voice, 3)))
e = np.array([x[1] for x in errs])
res = dict(clip_text=ctext, target_text=ttext, pairs=errs, median=float(np.median(np.abs(e))), max=float(np.abs(e).max()), n=len(errs), n_target=len(T),
           over=[x for x in errs if abs(x[1]) > 0.1])
json.dump(res, open(wj.replace(".json", "_lip2.json"), "w"), ensure_ascii=False, indent=1)
print(os.path.basename(wj), "짝", len(errs), "/", len(T), "중앙", round(res["median"], 3), "최대", round(res["max"], 3), res["over"])
