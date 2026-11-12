# 팀장 하이젠 모음(1.0배)에서 15강 인삿말·끝인사만 잘라 영상·소리 둘 다 0.9배.
# 자르는 점 = 모음 음성 무음(-40dB) 경계 기준, 11강 판(마루-아나운서)과 같은 여유(앞 1.10초 / 뒤 인삿말 0.71·끝인사 0.96초)
import subprocess, json
R = "../.."
CUT = {"인삿말": ("인삿말/홀수_인삿말_수정.mp4", 103.632, 117.014, 1.10, 0.71),   # 말 103.632~117.014 (무음 101.12~103.63 / 117.01~119.45)
       "끝인사": ("인삿말/홀수_끝인사.mp4",     122.927, 136.752, 1.10, 0.96)}   # 말 122.927~136.752 (무음 119.91~122.93 / 136.75~139.18)
meta = {}
for k, (src, a, b, pre, post) in CUT.items():
    ss, to = round(a - pre, 3), round(b + post, 3)
    out = f"../아나운서/15_{k}_090"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-to", str(to), "-i", f"{R}/{src}",
                    "-vf", "setpts=PTS/0.9", "-r", "22.5", "-af", "atempo=0.9", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", out + ".mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-to", str(to), "-i", f"{R}/{src}", "-vn",
                    "-af", "atempo=0.9", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out + ".wav"], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out + ".mp4"]))
    meta[k] = dict(src=src, src_from=ss, src_to=to, speech_src=[a, b], speech_out=[round(pre / 0.9, 3), round((b - ss) / 0.9, 3)], dur_out=round(d, 3))
    print(k, meta[k])
json.dump(meta, open("../아나운서/meta.json", "w"), ensure_ascii=False, indent=1)
