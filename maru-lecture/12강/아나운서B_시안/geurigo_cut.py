# 오더32 추가(팀장 결정 ㉡): 12강 인삿말 B클립에서 「그리고」 입 구간을 빼고, 타입캐스트 쉼(출력 12.08~12.50) 동안 입 다문 상태로.
#  출력 [UA, UB-BR) = 원본 클립의 말 없는 자리(작업, 끝 → 그리고 직전) 를 천천히 · [UB-BR, UB) = 그 끝 프레임 → B클립 UB 프레임을 광학흐름 보간 · 나머지 = B클립 그대로
# 실행(cwd=12강/아나운서B_시안): python3 geurigo_cut.py
import json, subprocess, numpy as np
FPS = 30000 / 1001; W, H = 1080, 1920; FS = W * H * 3
SRC = "../인삿말/12_인삿말_090.mp4"; B = "12_인삿말_flow.mp4"; OUT = "12_인삿말_flow_그리고컷.mp4"
info = json.load(open("12_인삿말_flow.json")); cs, ts = info["clip_speech"][0], info["target_speech"][0]
m = np.array(info["map"])
UA, UB = 12.08, 12.50            # 출력 시각: 타입캐스트 「작업,」 끝(11.69) ~ 「완료」 시작(12.11) → +cs−ts
C1 = 13.78                        # 원본 클립 「그리고」(13.84) 바로 전 — 말 없는 자리 끝
BR = 4                            # 이음매 보간 프레임 수
ka, kb = int(np.ceil(UA * FPS)), int(np.ceil(UB * FPS))
c0 = cs + float(np.interp(ka / FPS - cs, m[:, 0], m[:, 1]))   # UA 에서 B클립이 보던 원본 시각(이어짐)
print("frames", ka, kb, "clip", round(c0, 3), "→", C1)
def frames(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=FS); out = []
    while True:
        b = p.stdout.read(FS)
        if len(b) < FS: break
        out.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
    p.wait(); return out
# 원본 13.3~14.3 을 90fps 광학흐름으로
s0 = 13.4; src = frames(["ffmpeg", "-v", "error", "-ss", str(s0), "-i", SRC, "-t", "0.5", "-vf", "minterpolate=fps=90:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
def at(c): return src[min(len(src) - 1, max(0, round((c - s0) * 90)))]
bkb = frames(["ffmpeg", "-v", "error", "-i", B, "-vf", f"select=eq(n\\,{kb})", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])[0]
n_hold = kb - BR - ka
mid = [at(c0 + (C1 - c0) * i / max(1, n_hold - 1)) for i in range(n_hold)]
# 이음매: A=mid 끝 · B=bf[kb] → 광학흐름 보간 BR 장
A_, B_ = mid[-1], bkb
pair = b"".join([A_.tobytes(), A_.tobytes(), B_.tobytes(), B_.tobytes()])
r = subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "1", "-i", "-",
                    "-vf", f"minterpolate=fps={BR + 1}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                   input=pair, capture_output=True).stdout
interp = [np.frombuffer(r[i * FS:(i + 1) * FS], np.uint8).reshape(H, W, 3) for i in range(len(r) // FS)]
# A,A,B,B @1fps → BR+1 fps: 1초~2초 사이(A→B) 보간 프레임
bridge = interp[(BR + 1) + 1:(BR + 1) + 1 + BR]
assert len(bridge) == BR, len(interp)
repl = mid + bridge
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30000/1001", "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", B, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=FS); n = 0
while True:
    b = dec.stdout.read(FS)
    if len(b) < FS: break
    enc.stdin.write(repl[n - ka].tobytes() if ka <= n < kb else b); n += 1
enc.stdin.close(); enc.wait(); dec.wait()
assert len(repl) == kb - ka and n == info["out_frames"], (len(repl), kb - ka, n)
# 지도도 같이(검사기용): UA~UB 구간 c 를 새 값으로
tau = m[:, 0].copy(); cl = m[:, 1].copy()
ta, tb, tbr = ka / FPS - cs, kb / FPS - cs, (kb - BR) / FPS - cs
cb = float(np.interp(tb, tau, cl))
for i, t in enumerate(tau):
    if ta <= t < tbr: cl[i] = (c0 - cs) + (C1 - c0) * (t - ta) / (tbr - ta)
    elif tbr <= t < tb: cl[i] = (C1 - cs) + (cb - (C1 - cs)) * (t - tbr) / (tb - tbr)
info2 = dict(info); info2["map"] = [[round(float(a), 3), round(float(b), 3)] for a, b in zip(tau, cl)]
info2["cut"] = dict(out=[UA, UB], clip_hold=[round(c0, 3), C1], bridge_frames=BR, note="「그리고」 빼고 흐름 보간 이음매")
json.dump(info2, open(OUT.replace(".mp4", ".json"), "w"), ensure_ascii=False, indent=1)
print("ok", n)
