# sent_check2.py 가 쓰는 공용 함수(fix_bound2.py 에서 뗌)
import json, re, difflib, numpy as np, subprocess, mlx_whisper
DB = np.load("rmsdb.npy"); H = 0.005
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","v090_16k.wav","-f","s16le","-ac","1","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def tr(a, b):
    r = mlx_whisper.transcribe(x[int(a*16000):int(b*16000)], path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="ko", condition_on_previous_text=False)
    return re.sub(r"[^가-힣0-9]", "", r["text"])
def n(s): return re.sub(r"[^가-힣0-9]", "", s)
NUMK = {"0":"영","1":"일","2":"이","3":"삼","4":"사","5":"오","6":"육","7":"칠","8":"팔","9":"구"}
CHO = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"; JUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"; JONG = " ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"
def jamo(s):
    out = []
    for c in s:
        c = NUMK.get(c, c); o = ord(c[0]) - 0xAC00
        for ch in c:
            o = ord(ch) - 0xAC00
            if 0 <= o < 11172: out += [CHO[o // 588], JUNG[(o % 588) // 28]] + ([JONG[o % 28]] if o % 28 else [])
            else: out.append(ch)
    return out
def jr(a, b): return difflib.SequenceMatcher(None, jamo(a), jamo(b)).ratio()
def starts(after, head): return max(jr(after[:len(head) + k], head) for k in (-1, 0, 1)) >= 0.6
def has_head(before, head): return any(jr(before[-len(head) - k:][:len(head)], head) >= 0.8 for k in range(0, 5))
def ends_prev(before, tail): return max(jr(before[-len(tail) - k:], tail) for k in (0, 1, 2)) >= 0.5
