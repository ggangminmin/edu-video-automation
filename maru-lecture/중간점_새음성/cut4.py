# 오더36 ⓐ: 중간점_090.wav(= 11-19강/중간점 나레이션.wav atempo 0.9 · 48k 모노) → 4문장 자르기
#  경계 = 문장 사이 −50dB 쉼(5ms RMS) · 자르는 자리 = 말 시작 −0.02 / 말 끝 +0.04(쉼 안) · 앞 5ms · 끝 10ms 페이드
import numpy as np, wave, json
w = wave.open("중간점_090.wav"); sr = w.getframerate(); y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
H = sr // 200; db = 20 * np.log10(np.sqrt(np.mean((y / 32768)[:len(y) // H * H].reshape(-1, H) ** 2, 1)) + 1e-9)
SPEECH = [(0.055, 6.545), (6.71, 13.105), (13.33, 18.475), (18.7, 25.73)]   # 말 구간(쉼 run 경계 · find_gaps 결과)
NAMES = ["12_20장", "14_16장", "14_18장", "14_22장"]
OLD = {"12_20장": (665.98, 672.32), "14_16장": (603.45, 610.02), "14_18장": (646.84, 652.49), "14_22장": (719.41, 726.27)}   # 중간점_재생성목록.md 0.9배 원음 시각
TEXT = ["보고서에는 기본 정보·사용 자재·시공 방법·환경 측정값·사진 등을 기록합니다.", "견적은 자재비·시공비·부자재비·철거비·바닥 보정비·운반비 등으로 구성됩니다.",
        "시공·자재·환경·사용자 과실을 구분해야 비용 부담 주체가 정해집니다.", "견적서에는 공사 개요·수량·자재 명세·시공 방법·하자보증·결제 조건을 넣습니다."]
rows = []
for (a, b), nm, tx in zip(SPEECH, NAMES, TEXT):
    i0, i1 = int((a - 0.02) * sr), int((b + 0.04) * sr); seg = y[i0:i1].copy()
    fi, fo = int(0.005 * sr), int(0.010 * sr)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fo:] *= np.linspace(1, 0, fo)
    o = wave.open(f"{nm}.wav", "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(np.clip(seg, -32768, 32767).astype(np.int16).tobytes()); o.close()
    # 문장 안 쉼(중간점·쉼표 자리) 길이
    gaps = []; j = int(a * 200)
    while j < int(b * 200):
        if db[j] < -45:
            k = j
            while k < int(b * 200) and db[k] < -45: k += 1
            if k - j >= 12: gaps.append(round((k - j) * 0.005, 3))
            j = k
        else: j += 1
    ol = OLD[nm][1] - OLD[nm][0]
    rows.append(dict(file=f"{nm}.wav", src=[round(a - 0.02, 3), round(b + 0.04, 3)], speech=round(b - a, 3), file_len=round(len(seg) / sr, 3), old=round(ol, 3), diff=round((b - a) - ol, 3), inner_gaps=gaps, text=tx))
json.dump(rows, open("측정.json", "w"), ensure_ascii=False, indent=1)
for r in rows: print(r)
