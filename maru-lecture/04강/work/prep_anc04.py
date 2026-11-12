# 04강 아나운서 준비(08·09강 prep_anc 방식): 끝인사 소리 = v090 마지막 장(L=28) 구간 → bye_tc_090.wav · sound09.json
#  + warp_s 가 읽는 받아쓰기 캐시 [단어, 시작, 끝] 형식(클립 2개 · greet_tc_090 · bye_tc_090 = mlxwords 그 구간)
import subprocess, json, shutil, os
tl = json.load(open("../타임라인_초안.json")); S = {s["slide"]: s for s in tl["slides"]}; L = max(S)
e25 = S[L-1]["voice_end"] - S[L-1]["src_offset"]; s26 = S[L]["voice_start"] - S[L]["src_offset"]
e25, s26 = 869.49, 870.457   # 🆕04강: 초안 경계가 27장 「합니다」 꼬리(869.24) 안이라 손값 = 실측 무음 869.49~870.457(−40dB · 받아쓰기 앞 「작업해야 합니다」/뒤 「문제를 찾았다면」 ✓)
A = round(round(((e25 + s26) / 2) / 0.02) * 0.02, 2)   # L-1장 말끝 ~ L장 말시작 쉼 가운데(20ms 칸)
DUR = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "v090.wav"])); B = round(DUR, 3)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "v090.wav", "-ss", str(A), "-to", str(B), "-c:a", "pcm_s16le", "bye_tc_090.wav"], check=True)
e26 = S[L]["voice_end"] - S[L]["src_offset"]
json.dump(dict(lecture=4, greet_src="강의인삿말/0.9배/인삿말_04강_090.wav", bye_v090=[A, B], bye_speech=[round(s26, 4), round(e26, 4)], prev_slide_voice_end=round(e25, 4)), open("sound09.json", "w"), ensure_ascii=False, indent=1)
M = json.load(open("mlxwords.json"))
json.dump(dict(text="v090 mlxwords %.2f~%.2f" % (A, B), words=[[w.strip(), round(max(0, a - A), 3), round(b - A, 3)] for a, b, w in M if A - 0.05 <= a < B]), open("bye_tc_090_words.json", "w"), ensure_ascii=False, indent=0)
g = json.load(open("greet_tc_words.json")); json.dump(dict(text=g["text"], words=[[w.strip(), a, b] for a, b, w in g["words"]]), open("greet_tc_090_words.json", "w"), ensure_ascii=False, indent=0)
for k in ("인삿말", "끝인사"):
    f = f"../아나운서/04_{k}_090_words.json"; d = json.load(open(f))
    if d["words"] and not isinstance(d["words"][0][0], str):
        shutil.copy(f, f.replace("_words.json", "_words_raw.json")); json.dump(dict(text=d["text"], words=[[w.strip(), a, b] for a, b, w in d["words"]]), open(f, "w"), ensure_ascii=False, indent=0)
print("bye", A, B, "e25", round(e25, 3), "s26", round(s26, 3), "e26", round(e26, 3))
