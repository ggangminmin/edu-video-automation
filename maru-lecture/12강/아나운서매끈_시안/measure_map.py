# warp json → 출력 프레임마다 클립 프레임 위치 pos · 전진량 dpos(클립 프레임/출력 프레임) · 속도(1=원속)
import sys, json, numpy as np
d = json.load(open(sys.argv[1])); m = np.array(d["map"]); tau, cl = m[:,0], m[:,1]
cs, ce = d["clip_speech"]; ts, te = d["target_speech"]; spk = te-ts; FPS = 30000/1001; cf = d["used_fps"]
def c_of_u(u):
    if u < cs: return u
    if u < cs+spk: return cs+float(np.interp(u-cs, tau, cl))
    return ce+(u-cs-spk)
n = d["out_frames"]; pos = np.array([c_of_u(k/FPS)*cf for k in range(n)])
dp = np.diff(pos); sp = dp/(cf/FPS)             # 속도 1 = 원속(0.75 클립프레임/출력프레임)
rep = int((np.floor(pos[1:]+1e-6)==np.floor(pos[:-1]+1e-6)).sum())   # 같은 클립 프레임 다시(섞기 비율만 다름)
skip = int((np.floor(pos[1:]+1e-6)-np.floor(pos[:-1]+1e-6) >= 2).sum())
dsp = np.abs(np.diff(sp))
print(json.dumps(dict(frames=n, speed_min=round(sp.min(),2), speed_max=round(sp.max(),2),
  repeat_srcframe=rep, skip_srcframe=skip, max_speed_jump_per_frame=round(dsp.max(),2),
  n_speed_jump_gt_0_3=int((dsp>0.3).sum()), n_speed_lt_0_6=int((sp<0.6).sum()), n_speed_gt_1_6=int((sp>1.6).sum())), ensure_ascii=False))
np.save(sys.argv[2], np.vstack([np.arange(n-1)/FPS, sp]))
