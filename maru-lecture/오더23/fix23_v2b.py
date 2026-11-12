# 오더23(fix15_tl.py 복사) — warp 판 = 팀장 결정표(WV) · 출력 타임라인_v2b.json
# 오더15 — 16~20강 타임라인_초안 → 타임라인_v2 (렌더 X) · 오더09 fix09_tl.py 복사, 경로만 바꿈
#  #8  표지 인삿말 소리 = 강의인삿말/audio_(N-1) 0.9배(work/greet_aXX_090.wav) · 마지막 장 = 타입캐스트 마무리 멘트(work/bye_tc_090.wav, v090 구간)
#      하이젠 클립 소리 뺌. 클립 영상은 warp_clip.py(11강 p6 방식)로 새 소리에 맞춘 *_warp.mp4
#  규칙17 「스스로 떠올리기」 장 = 낭독 뒤 3초 · 확인문제 5.5초 그대로
#  인삿말 자막 = 새 소리 받아쓰기 + 강의인삿말 파일 이름 표기 대조 · 끝인사 자막 = 메모 그대로(글 v1 유지), 시각만 새 소리로
#  규칙10 BGM 강별 곡 · 음성 대비 −20dB(곡·음성 LUFS 실측) · 강 길이만큼 이어 붙이기(이음매 크로스페이드)
#  나머지(본문 장면·자막·텀)는 v1 그대로 시각만 민다.
# 실행(_작업 에서): python3 오더15_16-20/fix15_tl.py NN
import sys, json, glob, re, numpy as np, librosa
N = int(sys.argv[1]); D = f"{N}강"
FPS = 30000 / 1001
def q(t): return round(t * FPS) / FPS
LEAD, SELF_WAIT, HOLD_END = 0.09, 3.0, 3.5
CFG = json.load(open("오더15_16-20/cfg15.json"))[str(N)]
v1 = json.load(open(f"{D}/{CFG['tl_v1']}"))
ANN = CFG["ann"]                                         # 클립 폴더(강 폴더 기준)
L = max(s["slide"] for s in v1["slides"]); SELF = CFG["self_slide"]
LOUD = json.load(open("오더15_16-20/loud15.json"))

def db_frames(p):
    y, _ = librosa.load(p, sr=16000); fr = librosa.util.frame(np.pad(y, (0, 160)), frame_length=160, hop_length=160)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7)
def norm(s): return re.sub(r"[^가-힣0-9]", "", s)
def line_onsets(wav, texts):
    """줄마다 첫 단어 시작(받아쓰기) → 무음 안이면 소리 시작으로 · 단어 칸 안 0.08초+ 쉼이 있으면 그 쉼 끝(문장 시작 = 무음 끝)."""
    W = json.load(open(wav.replace(".wav", "_words.json")))["words"]; d = db_frames(wav)
    flat = []; pos = 0
    for w, a, b in W:
        t = norm(w)
        if t: flat.append((pos, a, b)); pos += len(t)
    full = "".join(norm(w) for w, _, _ in W)
    out, cur = [], 0
    for k, tx in enumerate(texts):
        nt = norm(tx); i = -1
        for a0 in (0, 1, 2, 3):                           # 받아쓰기 오자(보완→보안 등) 대비: 앞 글자 몇 개 건너뛰고 찾기
            i = full.find(nt[a0:a0 + 4], cur)
            if 0 <= i - a0 and i >= 0: i -= a0; break
            i = -1
        if i < 0 and k == 0: i = 0                      # 오더15: 첫 줄은 어차피 말 시작으로 고정(18강 「전에」→받아쓰기 「전의」)
        assert i >= 0, (wav, tx)
        cur = i + max(1, len(nt) - 3)                     # 줄 글자 수만큼 앞으로(「제12강에」 뒤 「12강에서는」 같은 자리 중복 방지)
        _, a, b = max((f for f in flat if f[0] <= i), key=lambda f: f[0])
        j, e = int(a * 100), int(b * 100)
        if d[j] < -40:
            while j < e and d[j] < -40: j += 1
        else:
            run, last = 0, None
            for jj in range(j, min(e, j + 250)):            # 오더15: 0.9초 창은 긴 쉼(20강 「끝까지」 앞 1.0초)을 놓침 → 2.5초
                run = run + 1 if d[jj] < -40 else 0
                if run >= 8: last = jj
                if run == 0 and last is not None: j = jj; break
        ds = np.convolve(d, np.ones(3) / 3, "same")
        if j > 12 and ds[j - 12:j].mean() - ds[j:j + 15].mean() > -10:   # 앞뒤 대비 약함 = 말 이어지는 자리 → 음량 골짜기 뒤 +6dB(11강 fix_bound 방식)
            w0, w1 = max(0, j - 30), j + 60; kk = w0 + int(np.argmin(ds[w0:w1])); j = kk
            while j < w1 and ds[j] < ds[kk] + 6: j += 1
        out.append(round(j / 100, 3))
    out[0] = None
    return out

def norm_slide(s):
    s = dict(s)
    for a, b in (("hold_after_voice", "gap_after_voice"), ("lead_before_voice", "gap_before_voice"), ("lead_after_cut", "gap_before_voice")):
        if a in s: s[b] = s.pop(a)
    for k in ("announcer", "clip_offset", "note"): s.pop(k, None)
    return s

tl = {"slides": [], "subs": [], "audio": [], "anchors": []}
# ---------- 1. 표지 + 인삿말
WV = json.load(open("오더23/warp_pick.json"))[str(N)]   # 오더23 팀장 결정표 [인삿말판, 끝인사판]
GW = WV[0]   # 🆕오더13: warp_clip2(실제 fps·프레임 섞기) · 12강 인삿말 = 「그리고」 건너뛴 편집안
gw = json.load(open(f"{D}/{ANN}/{N}_인삿말_{GW}.json"))
greet = glob.glob(f"{D}/work/greet_a{N-1}_090.wav")[0]
gdur = librosa.get_duration(path=greet)
toa = gw["target_at_out"]                                # 소리 0초가 놓이는 출력 시각(= 클립 말 시작 − 소리 말 시작)
ggain = round(10 ** ((LOUD["voice"][str(N)] - LOUD["greet"][str(N)]) / 20), 3)
tl["audio"].append(dict(slide=1, out=round(max(0.0, toa), 4), src_from=round(max(0.0, -toa), 4), src_to=round(gdur, 4),
                        src=f"work/greet_a{N-1}_090.wav", gain=ggain))
tl["anchors"].append({"name": "인삿말", "in": 0.0, "clip": f"../{ANN}/{N}_인삿말_{GW}.mp4", "clip_t0": 0.0})
cut = q(gw["out_dur"])                                   # 클립 끝 = 표지→2 컷(정지 화면 금지, 11강 v3 방식)
G = CFG["greet_lines"]
on = line_onsets(greet, G); on[0] = gw["target_speech"][0]
for t, txt in zip(on, G):
    tl["subs"].append(dict(slide=1, start=q(toa + t - LEAD), voice_on=round(toa + t, 3), text=txt, part="인삿말"))
tl["slides"].append(dict(slide=1, start=0.0, end=cut, voice_start=round(toa + gw["target_speech"][0], 3),
                         voice_end=round(toa + gw["target_speech"][1], 3), note="표지 + 인삿말 아나운서(warp) · 소리 audio_%d 0.9배" % (N - 1)))

# ---------- 2. 본문(2 ~ L-1): v1 그대로 시각만 민다 · 스스로 떠올리기 장 = 낭독 뒤 3초
S1 = {s["slide"]: s for s in v1["slides"]}
Dl = cut - S1[2]["start"]
A1 = {a["slide"]: a for a in v1["audio"] if a["slide"] not in (1, L)}
for sn in range(2, L):
    s = norm_slide(S1[sn])
    for k in ("start", "end", "voice_start", "voice_end", "src_offset"):
        if k in s and s[k] is not None: s[k] = round(s[k] + Dl, 4)
    s["start"] = cut
    subs = [dict(x) for x in v1["subs"] if x["slide"] == sn]
    for x in subs:
        x["start"] = q(x["start"] + Dl); x["voice_on"] = round(x["voice_on"] + Dl, 3); x.pop("end", None); x.pop("n", None)
    subs[0]["start"] = cut
    a = dict(A1[sn]); a["out"] = round(a["out"] + Dl, 4); tl["audio"].append(a)
    if sn == SELF:
        new_end = q(s["voice_end"] + SELF_WAIT); Dl += new_end - s["end"]; s["end"] = new_end; s["self_check_wait"] = True
    s["end"] = q(s["end"]); s["gap_after_voice"] = round(s["end"] - s["voice_end"], 3)
    tl["slides"].append(s); tl["subs"] += subs; cut = s["end"]

# ---------- 3. 마지막 장 = 끝인사 클립(warp) + 타입캐스트 마무리 멘트
bw = json.load(open(f"{D}/{ANN}/{N}_끝인사_{WV[1]}.json"))
bye = f"{D}/work/bye_tc_090.wav"; bdur = librosa.get_duration(path=bye)
ts, te = bw["target_speech"]; cs = bw["clip_speech"][0]
start = cut; off = start + LEAD - ts                      # 출력 = 소리 시각 + off
s0 = max(0.0, ts - 0.05)
ba = json.load(open(f"{D}/work/sound09.json"))["bye_v090"][0]
s0 = round(np.floor((ba + s0) / 0.02 + 1e-6) * 0.02 - ba, 3)   # v090 기준 20ms 칸에 맞춤(announcer_audio_check 포락선 칸 어긋남 오검출 방지 · 소리 내용 같음)
tl["audio"].append(dict(slide=L, out=round(off + s0, 4), src_from=round(s0, 4), src_to=round(bdur, 4), src="work/bye_tc_090.wav", gain=1.0))
end = q(off + te + HOLD_END)
bsubs = [x for x in v1["subs"] if x["slide"] == L]
bon = line_onsets(bye, [x["text"] for x in bsubs]); bon[0] = ts
for j, (x, t) in enumerate(zip(bsubs, bon)):
    tl["subs"].append(dict(slide=L, start=start if j == 0 else q(off + t - LEAD), voice_on=round(off + t, 3), text=x["text"], part="끝인사"))
c0 = round(off + ts - cs, 4)                              # warp 클립 말 시작(cs) = 소리 말 시작(ts)
tl["anchors"].append({"name": "끝인사", "in": start, "clip": f"../{ANN}/{N}_끝인사_{WV[1]}.mp4", "clip_t0": c0, "out": q(c0 + bw["out_dur"])})
tl["slides"].append(dict(slide=L, start=start, end=end, voice_start=round(off + ts, 3), voice_end=round(off + te, 3),
                         gap_after_voice=round(end - (off + te), 3), gap_before_voice=LEAD, quiz_wait=False, src_offset=round(off, 4),
                         note="끝인사 클립(warp) · 소리 = 타입캐스트 마무리 멘트 v090 %.2f~%.2f" % tuple(json.load(open(f"{D}/work/sound09.json"))["bye_v090"])))
cut = end
import os                                                 # 🆕오더13: scene_sub_check 로 잡혀 음성 확인된 줄 시작 고침(fix_subs09.py → sub_fix_NN.json)
SF = json.load(open(f"오더09_공용/sub_fix_{N}.json")) if os.path.exists(f"오더09_공용/sub_fix_{N}.json") else {}
for x in tl["subs"]:
    if x["text"] in SF: x["voice_on"] = SF[x["text"]]; x["start"] = q(SF[x["text"]] - LEAD); x["how"] = "scene_sub 고침"
for i, x in enumerate(tl["subs"]):
    x["n"] = i + 1; x["end"] = tl["subs"][i + 1]["start"] if i + 1 < len(tl["subs"]) else cut
T = cut
tl["ending"] = {"zoom_blur": [T, round(T + 0.67, 3)], "card": [round(T + 0.67, 3), round(T + 8.80, 3)],
                "black": [round(T + 8.80, 3), round(T + 9.70, 3)], "logo_off": round(T + 1.17, 3)}
tl["total"] = round(T + 9.70, 3)
song = CFG["bgm"]; bg_db = round(LOUD["voice"][str(N)] - 20 - LOUD["bgm"][song], 2)
tl["bgm"] = dict(file=f"BGM/{song}.mp3", gain_db=bg_db, song_lufs=LOUD["bgm"][song], voice_lufs=LOUD["voice"][str(N)],
                 loops=int(np.ceil(tl["total"] / (LOUD["bgm_dur"][song] - 3.0))), crossfade=3.0, fade_out=5.836,
                 rule="지금_규칙 10: 곡 LUFS + gain = 음성(v090) LUFS − 20 · 강 길이만큼 이어 붙임(이음매 3초 크로스페이드)")
P1 = {k: v for k, v in v1.get("params", {}).items() if k not in ("구조", "v1", "draft", "announcer", "greet", "bye", "rule")}
tl["params"] = dict(P1, 구조="민석 확정: 표지 = 팀장 인삿말 클립(영상만, 소리 = audio_(N-1) 0.9배) · 2번 아나운서 없음 · 마지막 장 = 팀장 끝인사 클립(영상만, 소리 = 타입캐스트 마무리 멘트)", LEAD=LEAD, SELF_WAIT=SELF_WAIT, SELF_SLIDE=SELF, HOLD_END=HOLD_END,
                    greet=f"work/greet_a{N-1}_090.wav(audio_{N-1} 0.9배, gain {ggain})", bye="work/bye_tc_090.wav(v090 마무리 멘트)",
                    입싱크="warp_clip2.py(11강 p6 warp_clip + 실제 fps·프레임 섞기) → *_warp2.mp4 · 검산 lipcheck2/onsetcheck", bgm=f"BGM/{song}.mp3 {bg_db}dB",
                    v2="오더09: #8 소리 교체 · 스스로 떠올리기 3초 · 인삿말 자막 새 소리 · BGM 강별 곡")
import os                                                   # 오더16·규칙20: place16_15.py 실측(검사_v2/배치16.json) — 초안은 align.py 다시 돌리면 지워지므로 여기서 읽음
PL = json.load(open(f"{D}/검사_v2/배치16.json")) if os.path.exists(f"{D}/검사_v2/배치16.json") else {}
for a, (x0, y0) in zip(tl["anchors"], ((934, 40), (952, 36))):
    r = PL.get(a["name"], {}); a["x"] = r["x_new"] if r.get("overlap_now", 0) > 0 and r.get("fits") else x0; a["y"] = y0
    a["place"] = "지적 #9·규칙 20: " + ("빈 공간 가운데로 옮김" if a["x"] != x0 else "안 가림 → 그대로")
json.dump(tl, open(f"{D}/타임라인_v2b.json", "w"), ensure_ascii=False, indent=1)
print(N, "자막", len(tl["subs"]), "총", tl["total"], "v1총", v1["total"], "표지끝", round(tl["slides"][0]["end"], 3), "BGM", song, bg_db)
for x in tl["subs"]:
    if x["slide"] in (1, L): print("  ", x["slide"], round(x["start"], 3), round(x["voice_on"], 3), x["text"])
s = next(s for s in tl["slides"] if s["slide"] == SELF); print("  스스로", SELF, round(s["voice_end"], 3), round(s["end"], 3), s["gap_after_voice"])
