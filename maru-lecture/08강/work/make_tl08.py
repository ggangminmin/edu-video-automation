# 08강 타임라인_v1 — 11~20강 최종 방식을 한 번에(오더45)
#  = 오더15 fix15_tl.py(표지 인삿말 소리 = 강의인삿말/0.9배/인삿말_08강_090 · 끝인사 소리 = v090 마무리 · BGM −20dB 실측)
#  + 오더23 fix23_tl.py(규칙7: 문장 끝 쉼 ≥1.505 · 넘김 말끝→1.71→컷→0.09→말 · 확인문제 5.5 · 스스로 3.0 · 장 첫 말/문장 시작이 쉼 안이면 무음 끝)
#  + 20강 make_tl_v4.py(아나운서 B = warp_s flow 클립 · 0.5초 페이드인 · 끝인사 bye_freeze)
#  줄 나눔 = align.py(line_break_check 허용 자리 + force_split.json) · 새 줄 시작 실소리 보정 = onset08.py(다음 단계)
# 실행(cwd = 08강/work): python3 make_tl08.py
import json, re, subprocess, numpy as np, librosa
N = 8; FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD, SELF_WAIT, HOLD_END, SENT_MIN, TURN, QUIZ_WAIT = 0.09, 3.0, 3.5, 1.505, 1.71, 5.5
v1 = json.load(open("../타임라인_초안.json")); NOTES = json.load(open("../notes_clean.json"))
L = max(s["slide"] for s in v1["slides"]); SELF = v1["params"]["SELF"][0]
LOUD = dict(voice=-16.1, greet=-18.1, bgm=-16.3, bgm_dur=359.72)   # ebur128 Integrated 실측(v090 · greet_tc_090 · BGM/Clear Focus.mp3)
import os, subprocess as _sp
def _warp(k, dry):
    f = f"../아나운서B/08_{k}_flow.json"
    if os.path.exists(f): return json.load(open(f))
    d = json.load(open(f"../아나운서B/dry/{k}_{dry}.json")); cs_, ce_ = d["clip_speech"]; ts_, te_ = d["target_speech"]   # 임시(실제 warp 전): warp_s 와 같은 식
    cd = float(_sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"../아나운서/08_{k}_090.mp4"],capture_output=True,text=True).stdout)
    d.update(out_dur=round(cs_ + (te_ - ts_) + (cd - ce_), 3), target_at_out=round(cs_ - ts_, 4), provisional=True); print("⚠ 임시 warp 값", k); return d
GW = _warp("인삿말", "g14"); BW = _warp("끝인사", "g17")
assert GW["mode"] == BW["mode"] == "flow"

def db_frames(p):
    y, _ = librosa.load(p, sr=16000); fr = librosa.util.frame(np.pad(y, (0, 160)), frame_length=160, hop_length=160)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7)
def norm(s): return re.sub(r"[^가-힣0-9]", "", s)
NUMK = {"8": "팔", "9": "구"}
def line_onsets(wav, texts):
    """fix15 그대로: 줄마다 첫 단어 시작(받아쓰기) → 무음 안이면 소리 시작 · 단어 칸 안 0.08초+ 쉼이면 그 쉼 끝 · 말 붙은 자리는 골짜기 뒤 +6dB"""
    W = json.load(open(wav.replace(".wav", "_words.json")))["words"]; d = db_frames(wav)
    flat = []; pos = 0
    for w, a, b in W:
        t = norm(w)
        if t: flat.append((pos, a, b)); pos += len(t)
    full = "".join(norm(w) for w, _, _ in W)
    out, cur = [], 0
    for k, tx in enumerate(texts):
        nt = norm(tx); i = -1
        for a0 in (0, 1, 2, 3):
            i = full.find(nt[a0:a0 + 4], cur)
            if 0 <= i - a0 and i >= 0: i -= a0; break
            i = -1
        if i < 0 and k == 0: i = 0
        assert i >= 0, (wav, tx)
        cur = i + max(1, len(nt) - 3)
        _, a, b = max((f for f in flat if f[0] <= i), key=lambda f: f[0])
        j, e = int(a * 100), int(b * 100)
        if d[j] < -40:
            while j < e and d[j] < -40: j += 1
        else:
            run, last = 0, None
            for jj in range(j, min(e, j + 250)):
                run = run + 1 if d[jj] < -40 else 0
                if run >= 8: last = jj
                if run == 0 and last is not None: j = jj; break
        ds = np.convolve(d, np.ones(3) / 3, "same")
        if j > 12 and ds[j - 12:j].mean() - ds[j:j + 15].mean() > -10:
            w0, w1 = max(0, j - 30), j + 60; kk = w0 + int(np.argmin(ds[w0:w1])); j = kk
            while j < w1 and ds[j] < ds[kk] + 6: j += 1
        out.append(round(j / 100, 3))
    out[0] = None
    return out

# ================= 1단계(fix15): 표지 · 본문 밀기 · 마지막 장 =================
t2 = {"slides": [], "subs": [], "audio": [], "anchors": []}
greet = "greet_tc_090.wav"; gdur = librosa.get_duration(path=greet)
toa = GW["target_at_out"]
ggain = round(10 ** ((LOUD["voice"] - LOUD["greet"]) / 20), 3)
t2["audio"].append(dict(slide=1, out=round(max(0.0, toa), 4), src_from=round(max(0.0, -toa), 4), src_to=round(gdur, 4), src="work/greet_tc_090.wav", gain=ggain))
t2["anchors"].append({"name": "인삿말", "in": 0.0, "clip": "../아나운서B/08_인삿말_flow.mp4", "clip_t0": 0.0})
cut = q(GW["out_dur"])
G = [x["text"] for x in v1["subs"] if x.get("part") == "인삿말"]
on = line_onsets(greet, G); on[0] = GW["target_speech"][0]
for t, txt in zip(on, G):
    t2["subs"].append(dict(slide=1, start=q(toa + t - LEAD), voice_on=round(toa + t, 3), text=txt, part="인삿말"))
t2["slides"].append(dict(slide=1, start=0.0, end=cut, voice_start=round(toa + GW["target_speech"][0], 3), voice_end=round(toa + GW["target_speech"][1], 3),
                         note="표지 + 인삿말 아나운서(flow) · 소리 강의인삿말/0.9배/인삿말_08강_090"))
S1 = {s["slide"]: s for s in v1["slides"]}
Dl = cut - S1[2]["start"]
A1 = {a["slide"]: a for a in v1["audio"] if a["slide"] not in (1, L)}
for sn in range(2, L):
    s = dict(S1[sn])
    for k in ("start", "end", "voice_start", "voice_end", "src_offset"):
        if k in s and s[k] is not None: s[k] = round(s[k] + Dl, 4)
    s["start"] = cut
    subs = [dict(x) for x in v1["subs"] if x["slide"] == sn]
    for x in subs:
        x["start"] = q(x["start"] + Dl); x["voice_on"] = round(x["voice_on"] + Dl, 3); x.pop("end", None); x.pop("n", None)
    subs[0]["start"] = cut
    a = dict(A1[sn]); a["out"] = round(a["out"] + Dl, 4); t2["audio"].append(a)
    s["end"] = q(s["end"]); s["gap_after_voice"] = round(s["end"] - s["voice_end"], 3)
    t2["slides"].append(s); t2["subs"] += subs; cut = s["end"]
SND = json.load(open("sound09.json")); bye = "bye_tc_090.wav"; bdur = librosa.get_duration(path=bye)
ts, te = BW["target_speech"]; cs = BW["clip_speech"][0]
start = cut; off = start + LEAD - ts
s0 = max(0.0, ts - 0.05); ba = SND["bye_v090"][0]
s0 = round(np.floor((ba + s0) / 0.02 + 1e-6) * 0.02 - ba, 3)   # v090 20ms 칸(announcer_audio_check 칸 어긋남 오검출 방지)
t2["audio"].append(dict(slide=L, out=round(off + s0, 4), src_from=round(s0, 4), src_to=round(bdur, 4), src="work/bye_tc_090.wav", gain=1.0))
end = q(off + te + HOLD_END)
bsubs = [x for x in v1["subs"] if x["slide"] == L]
bon = line_onsets(bye, [x["text"] for x in bsubs]); bon[0] = ts
for j, (x, t) in enumerate(zip(bsubs, bon)):
    t2["subs"].append(dict(slide=L, start=start if j == 0 else q(off + t - LEAD), voice_on=round(off + t, 3), text=x["text"], part="끝인사"))
c0 = round(off + ts - cs, 4)
t2["anchors"].append({"name": "끝인사", "in": start, "clip": "../아나운서B/08_끝인사_flow.mp4", "clip_t0": c0, "out": q(c0 + BW["out_dur"])})
t2["slides"].append(dict(slide=L, start=start, end=end, voice_start=round(off + ts, 3), voice_end=round(off + te, 3), gap_after_voice=round(end - (off + te), 3),
                         gap_before_voice=LEAD, wait="마지막", src_offset=round(off, 4), note="끝인사 클립(flow) · 소리 = 타입캐스트 마무리 v090 %.2f~%.2f" % tuple(SND["bye_v090"])))
for i, x in enumerate(t2["subs"]):
    x["n"] = i + 1; x["end"] = t2["subs"][i + 1]["start"] if i + 1 < len(t2["subs"]) else end
v2 = t2
for s_ in v2["slides"]:
    if s_.get("wait") == "문제": s_["quiz_wait"] = True
    if s_.get("wait") == "스스로": s_["self_check_wait"] = True
v2["total"] = round(end + 9.70, 3)
json.dump(v2, open("../타임라인_v1_1단계.json", "w"), ensure_ascii=False, indent=1)   # gap_check 비교 기준(문장 안 쉼 = 이 판과 같아야)

# ================= 2단계(fix23): 문장 텀 · 넘김 1.71/0.09 =================
S2 = {s["slide"]: s for s in v2["slides"]}
AU2 = {}
for a in v2["audio"]: AU2.setdefault(a["slide"], []).append(a)
assert all(len(v) == 1 for v in AU2.values())
AU2 = {k: dict(v[0]) for k, v in AU2.items()}
SPLIT_MAN = {}   # 장 사이 조각 경계 손값(경계 훑기에서 걸리면 여기)
END_MAN = {}; FIRST_MAN = {}
for k, t in SPLIT_MAN.items(): AU2[k]["src_to"] = t; AU2[k + 1]["src_from"] = t
def sent_starts(s):
    ls = [x for x in v2["subs"] if x["slide"] == s]; ns = re.sub(r"\s", "", " ".join(NOTES[s - 1])); pos = 0; out = []
    for j, x in enumerate(ls):
        tx = re.sub(r"\s", "", x["text"]); k = pos; i = 0
        while i < len(tx):
            if ns[k] == tx[i]: i += 1; k += 1
            elif ns[k] in ".?!": k += 1
            else: raise SystemExit(f"메모 대조 실패 {s}번 {x['text']} @{ns[k:k+10]}")
        if j > 0 and ns[pos - 1] in ".?!": out.append(x["n"])
        while k < len(ns) and ns[k] in ".?!": k += 1
        pos = k
    return set(out)
o = subprocess.run(["ffmpeg", "-i", "v090.wav", "-af", "silencedetect=n=-40dB:d=0.04", "-f", "null", "-"], capture_output=True, text=True).stderr
SIL = list(zip([float(x) for x in re.findall(r"silence_start: ([0-9.]+)", o)], [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", o)]))
tl = {"slides": [], "subs": [], "audio": [], "anchors": [], "pauses": [], "skipped": [], "fixed_on": []}
FIX = {}
tl["slides"].append(S2[1]); tl["subs"] += [dict(x) for x in v2["subs"] if x["slide"] == 1]
tl["audio"].append(AU2[1]); tl["anchors"].append(next(a for a in v2["anchors"] if a["name"] == "인삿말"))
cut = S2[2]["start"]
for s in range(2, L):
    ls = [x for x in v2["subs"] if x["slide"] == s]; sv = S2[s]; off2 = sv["src_offset"]; au = AU2[s]
    a = sv["voice_start"] - off2; b = sv["voice_end"] - off2
    if s in END_MAN: tl["fixed_on"].append(dict(slide=s, end_old=round(b, 3), end_new=END_MAN[s])); b = END_MAN[s]
    if s in FIRST_MAN:
        v0 = FIRST_MAN[s]; tl["fixed_on"].append(dict(slide=s, n=ls[0]["n"], old=round(a, 3), new=v0, text=ls[0]["text"], first=True, manual=True)); FIX[ls[0]["n"]] = v0 + off2; a = v0
    else:
        for u0, v0 in SIL:
            if u0 <= a < v0 - 0.12 and v0 - u0 >= 0.3 and v0 - a <= 1.2:
                tl["fixed_on"].append(dict(slide=s, n=ls[0]["n"], old=round(a, 3), new=round(v0, 3), text=ls[0]["text"], first=True)); FIX[ls[0]["n"]] = v0 + off2; a = v0; break
    starts = sent_starts(s); ins = []
    for x in ls:
        if x["n"] not in starts: continue
        on = x["voice_on"] - off2
        for u0, v0 in SIL:
            if u0 <= on < v0 - 0.12 and v0 - u0 >= 0.3 and v0 - on <= 1.2 and u0 > a:
                tl["fixed_on"].append(dict(slide=s, n=x["n"], old=round(on, 3), new=round(v0, 3), text=x["text"])); FIX[x["n"]] = v0 + off2; on = v0; break
        if on >= b - 0.05:
            tl["skipped"].append(dict(slide=s, n=x["n"], why="말 끝 뒤 줄(음성 없음)", text=x["text"])); continue
        c = [(u, v) for u, v in SIL if on - 0.35 <= v <= on + 0.12 and u > a]
        if not c:
            tl["skipped"].append(dict(slide=s, n=x["n"], why="앞 쉼 못 찾음", text=x["text"])); continue
        u, v = max(c, key=lambda z: z[1] - z[0]); g = v - u; add = max(0.0, SENT_MIN - g)
        p = (u + v) / 2; assert au["src_from"] < p < au["src_to"]
        ins.append((p, add)); tl["pauses"].append(dict(slide=s, n=x["n"], before=round(g, 3), after=round(g + add, 3)))
    ins.sort()
    start = cut; off = start + LEAD - a
    def mp(t): return t + off + sum(d for p, d in ins if p <= t)
    prev = au["src_from"]
    for p, d in ins + [(au["src_to"], 0.0)]:
        tl["audio"].append(dict(slide=s, out=round(mp(prev), 4), src_from=round(prev, 4), src_to=round(p, 4))); prev = p
    for j, x in enumerate(ls):
        on = mp(FIX.get(x["n"], x["voice_on"]) - off2); y = dict(x)
        y.update(start=start if j == 0 else q(on - LEAD), voice_on=round(on, 3), sent_start=x["n"] in starts); y.pop("end", None)
        tl["subs"].append(y)
    wait = QUIZ_WAIT if sv.get("wait") == "문제" else (SELF_WAIT if sv.get("wait") == "스스로" else TURN)
    end = q(mp(b) + wait)
    ns = dict(sv); ns.update(start=start, end=end, voice_start=round(mp(a), 3), voice_end=round(mp(b), 3), gap_after_voice=round(end - mp(b), 3),
                             gap_before_voice=round(mp(a) - start, 3), src_offset=round(off, 4), inserts=[[round(p, 4), round(d, 4)] for p, d in ins])
    tl["slides"].append(ns); cut = end
D = cut - S2[L]["start"]; sl = dict(S2[L])
for k in ("end", "voice_start", "voice_end", "src_offset"): sl[k] = round(sl[k] + D, 4)
sl["start"] = cut; sl["end"] = q(S2[L]["end"] + D); tl["slides"].append(sl)
tl["subs"] += [dict(x, start=(cut if i == 0 else q(x["start"] + D)), voice_on=round(x["voice_on"] + D, 3)) for i, x in enumerate(x for x in v2["subs"] if x["slide"] == L)]
tl["audio"].append(dict(AU2[L], out=round(AU2[L]["out"] + D, 4)))
an = dict(next(a for a in v2["anchors"] if a["name"] == "끝인사")); an["in"] = cut; an["clip_t0"] = round(an["clip_t0"] + D, 4); an["out"] = q(an["out"] + D)
tl["anchors"].append(an)
T = sl["end"]
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else T
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)], "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
bg_db = round(LOUD["voice"] - 20 - LOUD["bgm"], 2)
tl["bgm"] = dict(file="BGM/Clear Focus.mp3", gain_db=bg_db, song_lufs=LOUD["bgm"], voice_lufs=LOUD["voice"], loops=int(np.ceil(tl["total"] / (LOUD["bgm_dur"] - 3.0))),
                 crossfade=3.0, fade_out=5.836, rule="지금_규칙 10·23: 8강 = Clear Focus · 곡 LUFS + gain = 음성(v090) LUFS − 20 · 강 길이만큼 이어 붙임(이음매 3초 크로스페이드)")
# ================= 3단계(v4): 아나운서 가 =================
for a_ in tl["anchors"]: a_["fade_in"] = 0.5
for a_, (x0, y0) in zip(tl["anchors"], ((934, 40), (952, 36))): a_.setdefault("x", x0); a_.setdefault("y", y0)
tl["params"] = dict(v1["params"], LEAD=LEAD, SELF_WAIT=SELF_WAIT, SELF_SLIDE=SELF, HOLD_END=HOLD_END, voice="녹음_본문_04-20강/마루시공_-_08강.mp3 atempo=0.9",
                    greet=f"work/greet_tc_090.wav(강의인삿말/0.9배/인삿말_08강_090.wav 48k, gain {ggain})", bye="work/bye_tc_090.wav(v090 마무리 멘트)",
                    입싱크="warp_s flow(아나운서B/run_warp.sh 값) · 검산 anchor_sync_check", bgm=f"BGM/Clear Focus.mp3 {bg_db}dB",
                    문장텀="규칙7: 메모 문장 끝 뒤 쉼 ≥1.505(무음 삽입) · 넘김 말끝→컷 1.71 + 컷→말 0.09 · 확인문제 5.5 · 스스로 3.0",
                    v4_anchor="B flow 클립 · 등장 0.5초 알파 페이드인 · 끝인사 bye_freeze", 구조="표지+인삿말 클립(소리 타입캐스트) → 2 아나운서 없음 → 본문 → 26 끝인사 클립(소리 타입캐스트) → 엔딩")
json.dump(tl, open("../타임라인_v1초안.json", "w"), ensure_ascii=False, indent=1)
P = np.array([p["before"] for p in tl["pauses"]])
print("자막", len(tl["subs"]), "총", tl["total"], f"문장끝 {len(P)}곳 원래 최소 {P.min():.2f} 중앙 {np.median(P):.2f} · 조각 {len(tl['audio'])} · BGM {bg_db}dB loops {tl['bgm']['loops']}")
for k in tl["skipped"]: print("  건너뜀", k)
for k in tl["fixed_on"]: print("  시작고침", k)
for x in tl["subs"]:
    if x["slide"] in (1, L): print("  ", x["slide"], round(x["start"], 3), round(x["voice_on"], 3), x["text"])
print("끝인사 anchor", tl["anchors"][1], "slide L", tl["slides"][-1])
