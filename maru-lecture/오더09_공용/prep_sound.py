# 오더09 #8 소리 재료: 인삿말 = 강의인삿말/audio_(N-1) 0.9배(atempo, 피치 유지) · 끝인사 = v090.wav 마지막 장(마무리 멘트) 구간
# 실행(강 폴더 _작업/NN강 에서): python3 ../오더09_공용/prep_sound.py NN <타임라인.json>
import sys, json, glob, subprocess, numpy as np, librosa, soundfile as sf
N = int(sys.argv[1]); tl = json.load(open(sys.argv[2]))
R = "../.."
g = glob.glob(f"{R}/강의인삿말/audio_{N-1}_*.mp3"); assert len(g) == 1, g
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", g[0], "-af", "atempo=0.9", "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
                f"work/greet_a{N-1}_090.wav"], check=True)
# 마지막 장 앞 장의 v090 끝 → 그 뒤 첫 말 ~ v090 마지막 말
body = [a for a in tl["audio"] if "src_from" in a and not a.get("src")]
prev_to = max(a["src_to"] for a in body)
y, sr = librosa.load("work/v090.wav", sr=16000, mono=True)
H = 160; fr = librosa.util.frame(np.pad(y, (0, H)), frame_length=H, hop_length=H)
d = 20 * np.log10(np.sqrt((fr ** 2).mean(0)) + 1e-7)
i0 = int((prev_to + 0.2) * 100); on = np.where(d[i0:] > -40)[0] + i0
s, e = on[0] / 100, (on[-1] + 1) / 100
a, b = round(max(prev_to + 0.05, s - 0.30), 3), round(e + 0.30, 3)
yy, _ = librosa.load("work/v090.wav", sr=48000, mono=True, offset=a, duration=b - a)
sf.write("work/bye_tc_090.wav", yy, 48000, subtype="PCM_16")
info = dict(lecture=N, greet_src=g[0].split("/")[-1], greet_dur=round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"work/greet_a{N-1}_090.wav"], capture_output=True, text=True).stdout), 3),
            bye_v090=[a, b], bye_speech=[round(s, 3), round(e, 3)], prev_slide_src_to=prev_to)
json.dump(info, open("work/sound09.json", "w"), ensure_ascii=False, indent=1); print(info)
