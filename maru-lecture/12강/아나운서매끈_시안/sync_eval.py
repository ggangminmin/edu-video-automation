# 입 싱크 평가(받아쓰기 다시 안 함): ①단어 짝(캐시 words, lipcheck 와 같은 식) ②국소 소리 포락선 lag(단어마다 ±0.5초 창, 인계 교훈4)
import sys, json, re, difflib, numpy as np, librosa
B = "../인삿말"; CW, TW = f"{B}/12_끝인사_090_words.json", "../work/bye_tc_090_words.json"
CWAV, TWAV = f"{B}/12_끝인사_090.wav", "../work/bye_tc_090_wav" 
def load_words(p):
    return [(re.sub(r"[^가-힣0-9]", "", w[0]), w[1], w[2]) for w in json.load(open(p))["words"] if re.sub(r"[^가-힣0-9]", "", w[0])]
def evaluate(info):
    cs, ce = info["clip_speech"]; ts, te = info["target_speech"]
    m = np.array(info["map"]); tau, cl = m[:, 0], m[:, 1]
    C, T = load_words(CW), load_words(TW)
    sm = difflib.SequenceMatcher(None, [w[0] for w in C], [w[0] for w in T]); errs = []
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            c_t, t_t = C[a+k][1], T[b+k][1]
            if not (cs <= c_t <= ce and ts <= t_t <= te): continue
            errs.append((C[a+k][0], round(cs + float(np.interp(c_t - cs, cl, tau)) - (cs + t_t - ts), 3)))
    # 국소 포락선 lag
    SR, H = 16000, 160
    yc = librosa.load(f"{B}/12_끝인사_090.wav", sr=SR)[0]; yt = librosa.load("../work/bye_tc_090.wav", sr=SR)[0]
    def env(y):
        fr = librosa.util.frame(np.pad(y, (0, H)), frame_length=H, hop_length=H); e = np.sqrt((fr**2).mean(0)); return np.log(e + 1e-4)
    ec, et = env(yc), env(yt); spk = te - ts
    us = np.arange(0, spk, 0.01)
    w = np.array([ec[min(len(ec)-1, int((cs + float(np.interp(u, tau, cl))) * 100))] for u in us])   # 화면(입)이 내는 소리 포락선
    t = np.array([et[min(len(et)-1, int((ts + u) * 100))] for u in us])
    lags = []
    for _, t_t, _e in T:
        u0 = t_t - ts
        if not (0.3 <= u0 <= spk - 0.3): continue
        i0, i1 = int((u0 - 0.5) * 100), int((u0 + 0.5) * 100); i0 = max(i0, 15); i1 = min(i1, len(us) - 15)
        best = max(range(-15, 16), key=lambda s: np.corrcoef(w[i0+s:i1+s], t[i0:i1])[0, 1])
        lags.append(round(best * 0.01, 2))   # + = 입이 소리보다 늦음
    e = np.abs([x[1] for x in errs]); L = np.abs(lags)
    return dict(word_n=len(errs), word_med=round(float(np.median(e)), 3), word_max=round(float(e.max()), 3), word_over=[x for x in errs if abs(x[1]) > 0.1],
                lag_n=len(L), lag_med=round(float(np.median(L)), 3), lag_max=round(float(L.max()), 3), lag_over=int((L > 0.1).sum()), lags=lags)
if __name__ == "__main__":
    r = evaluate(json.load(open(sys.argv[1]))); print(json.dumps({k: v for k, v in r.items()}, ensure_ascii=False))
