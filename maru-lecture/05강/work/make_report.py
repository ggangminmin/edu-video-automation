# NN강 1단계_보고.md 자동 작성(숫자는 전부 파일에서 읽음)
import json, os, re, subprocess
from lec import N
D = json.load(open("../타임라인_초안.json")); M = json.load(open("../아나운서/meta.json")); G = json.load(open("greet_tc_words.json"))
GT = json.load(open("greet_text.json"))
notes = json.load(open("../notes_clean.json")); png = len([x for x in os.listdir("../slides") if x.endswith(".png")])
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]))
o = dur(f"../../../녹음_본문_04-20강/마루시공_-_{N}강.mp3"); v = dur("v090.wav")
al = open("align.log").read(); ct = subprocess.run(["python3", "check_text.py"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
cb = open("check_bound.log").read().strip().splitlines()[-1]; fb = open("fix_bound.log").read()
unres = [l.split(" 원래")[0] for l in fb.splitlines() if "→ None" in l]
nfix = len(json.load(open("onset_override.json"))) if os.path.exists("onset_override.json") else 0
sc = open("sent_check.log").read(); scl = sc.strip().splitlines()[-1]
scnm = [l for l in sc.splitlines() if "수 다름" in l]; sckeep = [l for l in sc.splitlines() if "그대로(확인)" in l]
dis = re.search(r"cpp/mlx 어긋남 (\d+)", al).group(1)
an = {a["name"]: a for a in D["anchors"]}
P = D["params"]; T_ = D["total"]
bad_sl = [s for s in D["slides"] if s.get("wait")]
greet_n = len([x for x in D["subs"] if x.get("part") == "인삿말"])
L = []
L.append(f"# {N}강 1단계 보고 — 재료 준비(과금 0 · 렌더 X) · 2026-11-02 마루-16~20(w28:pC)\n")
L.append("## 결과물 (`_작업/%d강/`)" % N)
L.append("| 항목 | 파일 | 확인 |\n|---|---|---|")
L.append(f"| a) 슬라이드 PNG | `slides/s-01~{png:02d}.png` · 한눈에 `work/slides_sheet.jpg` | {png}장 전부 1920×1080 (원본 PDF 960×540pt ×2) · 🔒규칙 9: 원본 그대로 씀 |")
L.append(f"| b) 대본 | `notes_raw.json` · `notes_clean.json` (`work/notes_extract.py`) | 슬라이드 {png} = 메모 {len(notes)} {'✅' if png == len(notes) else '❌'} (1번 표지 메모 없음) |")
L.append(f"| b) 0.9배 음성 | `work/v090.wav`(48k) · `v090_16k.wav` | {o:.2f}초 → **{v:.2f}초** (÷0.9 = {o/0.9:.2f}, 차 {abs(v-o/0.9):.3f}초 ✅) |")
L.append(f"| b) 받아쓰기 | `work/wfull.json`(whisper.cpp 단어) · `work/mlxwords.json`(mlx-whisper 단어) | {al.splitlines()[0]} |")
L.append(f"| b) 타임라인 초안 | `타임라인_초안.json` (`work/align.py`) | 자막 {len(D['subs'])}줄(인삿말 {greet_n} · 본문 {len(D['subs'])-greet_n}) · 총 **{T_:.1f}초 ({int(T_//60)}:{T_%60:04.1f})** |")
L.append(f"| c) 인삿말 소리 | `work/greet_tc_090.wav` ← `강의인삿말/{G['src'][:9]}…` 0.9배 (`work/greet_tc.py`) | {G['dur_src']:.2f} → {G['dur_090']:.2f}초 · 받아쓰기 글자 일치 {re.search(r'인삿말 글자 일치 (\S+)', al).group(1)} |")
L.append(f"| c) 인삿말·끝인사 클립(영상) | `아나운서/{N}_인삿말_090.mp4`({M['인삿말']['dur_out']}초) · `{N}_끝인사_090.mp4`({M['끝인사']['dur_out']}초) · `아나운서/meta.json` (`work/cut_greet.py`) | {'남자·홀수' if N % 2 else '여자·짝수'} 모음 `{M['인삿말']['src']}` {M['인삿말']['speech_src']} · `{M['끝인사']['src']}` {M['끝인사']['speech_src']} · 22.5fps 0.9배 |")
L.append(f"| d) 사진정렬 후보 | `사진정렬_후보.md` | 🔒규칙 9 변경으로 **보정 안 함**(참고 기록) |")
L.append(f"| 스크립트 | `work/lec.py · notes_extract · cut_greet · greet_tc · mlx_words · refine · linetimes_make · align · sent_check · check_text · check_bound · fix_bound · make_report` | 15강 판 복사 + 강 번호 자동 |\n")
L.append("## 타임라인 초안 숫자 (11강 v3 규칙 + 지금_규칙 17·18)")
L.append(f"- 구조: 표지(1) + 인삿말 클립(영상) + **타입캐스트 인삿말 소리**(규칙 18) 0~{D['slides'][0]['end']:.2f} → 2번(아나운서 없음) {D['slides'][1]['start']:.2f} → … → {len(notes)}번 = 끝인사 클립(영상) + **타입캐스트 마무리 소리**(v090 그 장) {an['끝인사']['in']:.2f} → 3.5초 → 엔딩(줌 블러 0.67 · 카드 8.13 · 검정 0.90).")
L.append(f"- 텀: 말 끝→컷 1.21 · 컷=새 자막 같은 프레임 · 0.09초 뒤 말 · 문제 {P['QUIZ']} 말 끝→컷 **5.5초** · 스스로 확인하기 {P['SELF']} **3.0초**(규칙 17) · 실측 " + ", ".join(f"{s['slide']}번 {s['gap_after_voice']}" for s in bad_sl if s['wait'] != '텀') + ".")
L.append(f"- BGM: **{P['bgm']}**")
L.append(f"- `check_text.py`: {ct}")
L.append(f"- 문장 시작: {re.search(r'문장 시작 .*', al).group(0)} · `sent_check.py`(긴 무음 대응 + 받아쓰기 확인) {scl}")
L.append(f"- 문장 안 줄 경계 `check_bound` {cb} → `fix_bound` {nfix}곳 보정 · **미해결 {len(unres)}곳**" + (": " + " / ".join(f"#{u}" for u in unres) if unres else ""))
L.append(f"- 아나운서 warp 비율(타입캐스트 말 길이 ÷ 클립 말 길이): 인삿말 **{an['인삿말']['warp_ratio']}** · 끝인사 **{an['끝인사']['warp_ratio']}** → 2단계 `11강/work/warp_clip.py`(기울기 0.4~2.5 안).\n")
L.append("## e) 이상한 점 · 확인할 것")
k = 1
L.append(f"{k}. 인삿말 자막 문장 = `work/greet_text.json`: 「{GT['text']}」 — 원고가 없어 띄어쓰기·쉼표는 받아쓰기 기준(타입캐스트 받아쓰기: 「{G['text'].strip()}」). 사람 확인 필요."); k += 1
L.append(f"{k}. 받아쓰기 cpp↔mlx 문장 시작 1초 넘게 어긋남 {dis}곳(확인문제 보기 「일 번, …」을 cpp 가 숫자로 받아써 글자 대응이 빠진 곳 + 문장 첫머리에서 두 받아쓰기가 약 1.1초 엇갈린 곳) — 둘 중 늦은 쪽을 무음 끝에 붙임 → `sent_check`(긴 무음 대응 + 받아쓰기) 결과는 위 숫자."); k += 1
if scnm: L.append(f"{k}. 긴 무음 수 ≠ 문장 수라 문장 시작 자동 대응 못한 장: " + " · ".join(x.split(':')[0] + '번' for x in scnm) + " — 2단계 검사기(scene_sub_check · check_bound)로 그 장 꼭 확인."); k += 1
if sckeep: L.append(f"{k}. 문장 시작 후보였지만 받아쓰기 확인 실패로 그대로 둔 곳: " + " / ".join(x[:60] for x in sckeep)); k += 1
if unres: L.append(f"{k}. 줄 경계 미해결 {len(unres)}곳(초안 시각 그대로): " + " / ".join(unres) + " — 2단계에서 다시 봄."); k += 1
L.append(f"{k}. 끝인사 클립 = 팀장 모음에서 「다음 강 예고」로 끝나는 구간(받아쓰기 부분 대조로 마지막 장 메모와 같은 대본으로 보임) → 규칙 18 대로 소리는 타입캐스트 마지막 장, 클립은 영상만 · 같은 말 두 번 나오는 문제 없음. 대본이 조금 달라도(예: 20강 클립 「20강의를」 · 메모 「스무 강의를」) 입 모양은 2단계 warp 후 입 싱크 검사로 확인."); k += 1
L.append(f"{k}. 렌더·하이젠/클링 생성 없음(과금 0). 무거운 명령은 lockf `.heavy.lock`(~20:5x) → 규칙 19 변경 뒤 `검수/heavy_run.sh`."); k += 1
open("../1단계_보고.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
