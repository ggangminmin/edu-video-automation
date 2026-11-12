#!/bin/zsh
# master_check.sh [--screen 화면설정.json] <master.mp4> <dlg.wav> <tag>  — 전편: subbar_scan · 말구간 · scdet · capsync · blackdetect · GOP · 합격클립 대조 (읽기 전용)
# [검수기 모음 복사본 261019] 원본 = ~/Movies/kostat_R24/R28/QA2/master_check.sh. 바뀐 점: 스크립트는 형제 폴더에서 부르고, 결과는 OUT 폴더(기본 ~/Movies/video_qa/<tag>)에 쓴다. 합격 클립 폴더는 PASSED.
# 10/19: PASSED 기본값(kostat_R24/R26/passed) 없앰 — 꼭 지정. 안 주면 합격 대조만 건너뛰고 알린다. 화면 숫자는 화면 설정 json 으로 뺐다.
# 화면 설정(자막바 위치 · 색) 필수: 첫 인자 --screen <json> 또는 환경변수 QA_SCREEN. 없으면 아무것도 돌리기 전에 멈춘다.
[ "$1" = "--screen" ] && { export QA_SCREEN=${2:A}; shift 2; }
[ -n "$QA_SCREEN" ] && export QA_SCREEN=${QA_SCREEN:A}
if [ -z "$QA_SCREEN" ] || [ ! -f "$QA_SCREEN" ]; then
  echo "화면 설정이 없다(--screen <json> 또는 QA_SCREEN) — 자막바를 먼저 재라: python3 minstack/도구/자막바_재기.py <영상> <초> … --out <폴더>"; echo "  국가데이터처 = minstack/검수기/화면설정_예시_국가데이터처.json"; exit 2
fi
set -e; R=${0:A:h:h}; M=${1:A}; D=${2:A}; T=$3
SUB=$R/03_빈_자막바; SYN=$R/02_자막_싱크_늦게뜸_일찍꺼짐; PAS=$R/04_합격장면_그대로_들어갔나; CAP=$R/09_자막_글자_빠짐_바뀜_직전판과
OUT=${OUT:-$HOME/Movies/video_qa/$T}; [ -n "$PASSED" ] && PASSED=${PASSED:A}; mkdir -p "$OUT/fr"; cd "$OUT"; [ -n "$PREVMP4" ] && PREVMP4=${PREVMP4:A}; echo "결과 폴더: $OUT · 화면 설정: $QA_SCREEN"
echo "== subbar"; python3 "$SUB/subbar_scan.py" "$M" subbar_$T.json
echo "== runs";   python3 "$SYN/runs.py" "$D" runs_$T.json
echo "== scdet";  ffmpeg -v info -i "$M" -map 0:v:0 -vf scale=480:-1,scdet=threshold=14 -f null - 2> scd_$T.log
echo "== whisper"; ffmpeg -v error -y -i "$D" -ac 1 -ar 16000 dlg16k_$T.wav; whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -f dlg16k_$T.wav -ojf -of whisper_$T -ml 1 -sow -dtw large.v3.turbo > whisper_$T.log 2>&1
echo "== capsync"; python3 "$SYN/capsync.py" subbar_$T.json runs_$T.json scd_$T.log capsync_$T whisper_$T.json
echo "== blackdetect(전 프레임)"; ffmpeg -v info -i "$M" -map 0:v:0 -vf blackdetect=d=0.03:pic_th=0.98 -f null - 2> black_$T.log; grep black_start black_$T.log || echo "black 0"
echo "== GOP/I-frame"; ffprobe -v error -select_streams v:0 -show_entries frame=pict_type -of csv=p=0 "$M" | awk '{c[$1]++} END{for(k in c) print k,c[k]}'; ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,r_frame_rate,nb_frames,duration -of csv=p=0 "$M"; ffprobe -v error -show_entries stream=codec_type,codec_name,channels,sample_rate -of csv=p=0 "$M"
echo "== frame index + 합격클립 대조"; python3 "$PAS/frame_index.py" "$M" idx_$T.npz
if [ -n "$PASSED" ] && [ -d "$PASSED" ]; then python3 "$PAS/passed_match.py" idx_$T.npz "$PASSED" passed_$T.md; else echo "⚠️ 합격 클립 대조 건너뜀 — PASSED=<합격 클립 폴더> 를 지정하지 않았거나 폴더가 없다(${PASSED:-미지정}). 나머지 검사는 계속."; fi
 [ -n "$PREV" ] && { echo "== 직전 후보($PREV) 자막 글자 대조"; PD=${PREVDIR:-$HOME/Movies/video_qa/$PREV}; python3 "$CAP/capdiff.py" "$PD/idx_$PREV.npz" idx_$T.npz "$PD/subbar_$PREV.json" subbar_$T.json "$PREVMP4" "$M" capdiff_${PREV}_$T ${SEARCH:-720}; }
echo "== 말 있는데 자막 없음"; python3 - subbar_$T.json runs_$T.json <<'PY'
import sys,json,numpy as np
S=json.load(open(sys.argv[1]));bar=np.array(S['bar']);dark=np.array(S['dark']);FPS=S['fps'];R=json.load(open(sys.argv[2]))['runs']
txt=(bar>.4)&(dark>=200)
def ts(t): return f'{int(t//60)}:{t%60:05.2f}'
for a,b in R:
    if b-a<0.3: continue
    f0,f1=int(a*FPS),int(b*FPS); miss=(1-txt[f0:f1].mean())*(b-a)
    if miss>=0.4: print(ts(a),ts(b),round(float(miss),2))
PY
echo DONE $T
