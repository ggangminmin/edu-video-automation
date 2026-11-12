# 팀장 하이젠 모음(1.0배)에서 NN강 인삿말·끝인사 영상만 잘라 0.9배(22.5fps, 11·15강 판과 같음).
# 🔒지금_규칙 18: 이 클립 소리는 최종에 안 쓴다(입 모양 기준 소리로만 보관 → 2단계 warp_clip.py 가 타입캐스트에 맞춤).
# 자르는 점 = 모음 음성 무음(-40dB, 1.2초 이상) 경계 · 여유 앞 1.10초 / 뒤 인삿말 0.71·끝인사 0.96초(11·15강과 같음)
# 구간은 모음 whisper.cpp 받아쓰기(아나운서/11강/work/greet_all·bye_all, 12강/인삿말/인삿말_all·끝인사_all)로 강 번호 확인
import subprocess, json
from lec import N
R = "../.."
TAB = {4: {"인삿말": ("인삿말/짝수_인삿말.mp4", 16.903, 29.800), "끝인사": ("인삿말/짝수_끝인사.mp4", 22.783, 37.862)},   # 04강: moum_asr.py 받아쓰기 「제4강」·28장 메모 ✓ + silencedetect −40dB 1.2초
       6: {"인삿말": ("인삿말/짝수_인삿말.mp4", 31.707, 45.631), "끝인사": ("인삿말/짝수_끝인사.mp4", 39.712, 54.482)},
       8: {"인삿말": ("인삿말/짝수_인삿말.mp4", 47.545, 62.375), "끝인사": ("인삿말/짝수_끝인사.mp4", 56.388, 72.315)},
       16: {"인삿말": ("인삿말/짝수_인삿말.mp4", 113.060, 127.461), "끝인사": ("인삿말/짝수_끝인사.mp4", 127.722, 142.761)},
       17: {"인삿말": ("인삿말/홀수_인삿말_수정.mp4", 119.450, 132.948), "끝인사": ("인삿말/홀수_끝인사.mp4", 139.185, 154.648)},
       18: {"인삿말": ("인삿말/짝수_인삿말.mp4", 130.523, 146.925), "끝인사": ("인삿말/짝수_끝인사.mp4", 144.621, 161.679)},
       19: {"인삿말": ("인삿말/홀수_인삿말_수정.mp4", 135.823, 150.207), "끝인사": ("인삿말/홀수_끝인사.mp4", 157.038, 167.285)},
       20: {"인삿말": ("인삿말/짝수_인삿말.mp4", 149.474, 166.367), "끝인사": ("인삿말/짝수_끝인사.mp4", 163.589, 193.650)}}
PAD = {"인삿말": (1.10, 0.71), "끝인사": (1.10, 0.96)}
meta = {}
for k, (src, a, b) in TAB[N].items():
    pre, post = PAD[k]; ss, to = round(a - pre, 3), round(b + post, 3)
    out = f"../아나운서/{N:02d}_{k}_090"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-to", str(to), "-i", f"{R}/{src}",
                    "-vf", "setpts=PTS/0.9", "-r", "22.5", "-af", "atempo=0.9", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", out + ".mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-to", str(to), "-i", f"{R}/{src}", "-vn",
                    "-af", "atempo=0.9", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out + ".wav"], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out + ".mp4"]))
    meta[k] = dict(src=src, src_from=ss, src_to=to, speech_src=[a, b], speech_out=[round(pre / 0.9, 3), round((b - ss) / 0.9, 3)], dur_out=round(d, 3),
                   audio_note="클립 소리 = 입 모양 기준(warp용) · 최종 소리 아님(규칙 18)")
    print(k, meta[k])
json.dump(meta, open("../아나운서/meta.json", "w"), ensure_ascii=False, indent=1)
