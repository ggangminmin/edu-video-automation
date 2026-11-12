#!/bin/zsh
# preview_check.sh [--screen 화면설정.json] <preview.mp4> <tag> — 미리보기(자체 오디오) 자막 싱크·검은 프레임·바 깜박임 (읽기 전용). 인코딩 중이면 moov 생길 때까지 대기.
# [검수기 모음 복사본 261019] 원본 = ~/Movies/kostat_R24/R28/QA2/preview_check.sh. 스크립트는 형제 폴더에서, 결과는 OUT(기본 ~/Movies/video_qa/<tag>)에.
# 화면 설정(자막바 위치 · 색) 필수: 첫 인자 --screen <json> 또는 환경변수 QA_SCREEN. 없으면 아무것도 돌리기 전에 멈춘다.
[ "$1" = "--screen" ] && { export QA_SCREEN=${2:A}; shift 2; }
[ -n "$QA_SCREEN" ] && export QA_SCREEN=${QA_SCREEN:A}
if [ -z "$QA_SCREEN" ] || [ ! -f "$QA_SCREEN" ]; then
  echo "화면 설정이 없다(--screen <json> 또는 QA_SCREEN) — 자막바를 먼저 재라: python3 minstack/도구/자막바_재기.py <영상> <초> … --out <폴더>"; echo "  국가데이터처 = minstack/검수기/화면설정_예시_국가데이터처.json"; exit 2
fi
R=${0:A:h:h}; P=${1:A}; T=$2; n=0; SUB=$R/03_빈_자막바; SYN=$R/02_자막_싱크_늦게뜸_일찍꺼짐
OUT=${OUT:-$HOME/Movies/video_qa/$T}; mkdir -p "$OUT"; cd "$OUT"; echo "결과 폴더: $OUT"
until ffprobe -v error -show_entries format=duration -of csv=p=0 "$P" >/dev/null 2>&1; do sleep 5; n=$((n+1)); [ $n -gt 120 ] && { echo "timeout: no moov"; exit 1; }; done
s1=$(stat -f %z "$P"); sleep 5; s2=$(stat -f %z "$P"); [ "$s1" = "$s2" ] || sleep 10
ffprobe -v error -show_entries stream=codec_type,codec_name,nb_frames,duration -of csv=p=0 "$P"
python3 "$SUB/subbar_scan.py" "$P" subbar_$T.json && python3 "$SYN/runs.py" "$P" runs_$T.json 1 && ffmpeg -v info -i "$P" -map 0:v:0 -vf scale=480:-1,scdet=threshold=14 -f null - 2> scd_$T.log
ffmpeg -v error -y -i "$P" -map 0:a:0 -ac 1 -ar 16000 dlg16k_$T.wav && whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -f dlg16k_$T.wav -ojf -of whisper_$T -ml 1 -sow -dtw large.v3.turbo > whisper_$T.log 2>&1
python3 "$SYN/capsync.py" subbar_$T.json runs_$T.json scd_$T.log capsync_$T whisper_$T.json; sed -n '1,40p' capsync_$T.md
echo "== black"; if ffmpeg -v info -i "$P" -map 0:v:0 -vf blackdetect=d=0.03:pic_th=0.98 -f null - 2> black_$T.log; then grep black_start black_$T.log || echo "black 0"; else echo "ERROR 검은 화면 검사 실패(검사 안 함) — black_$T.log 확인"; tail -3 black_$T.log; exit 1; fi
echo "== segs/gaps"; python3 - $T <<'PY'
import json,sys,numpy as np
T=sys.argv[1]; S=json.load(open(f'subbar_{T}.json'));bar=np.array(S['bar']);dark=np.array(S['dark']);FPS=S['fps']
J=json.load(open(f'capsync_{T}.json'));segs=[(r['f0'],r['f1']) for r in J['segs']]
W=json.load(open(f'whisper_{T}.json'))['transcription']; tok=[]
for s in W:
    for t in s.get('tokens',[]):
        if t['text'].startswith('[') or t['text'].startswith('<|'): continue
        tok.append((t['t_dtw']*0.01-0.12 if t.get('t_dtw',-1)>=0 else s['offsets']['from']/1000,t['text']))
tok.sort()
def ts(t): return f'{int(t//60)}:{t%60:05.2f}'
for r in J['segs']: print('seg',ts(r['t0']),ts(r['t1']),'on',r['s_on'],'off',r['s_off'],'tail',r.get('tail'),r['text'][:30])
for (a,b),(c,d) in zip(segs,segs[1:]):
    if c!=b:
        g=bar[b:c]; off=int((g<=.4).sum()); e=int(((g>.4)&(dark[b:c]<200)).sum()); t=c/FPS
        near=' '.join(f'{x}({a2-t:+.2f})' for a2,x in tok if t-0.9<=a2<=t+0.4)
        print(('⚠️짧은바꺼짐' if 0<off<=15 else '빈바' if e else 'gap'),ts(b/FPS),'→',ts(t),c-b,'f off',off,'empty',e,'| 뒤자막 켜짐 근처 단어:',near)
PY
echo DONE $T
