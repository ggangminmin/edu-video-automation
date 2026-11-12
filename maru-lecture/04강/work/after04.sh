#!/bin/zsh
# 04강 렌더 뒤 검사대(지금_규칙 24 전부) — 20강 after_render_v4c.sh 방식 + newline_onset --all · line_break · gap_check · 장 경계 조각 훑기
# 사용: after04.sh <V>   (렌더 render04.py V=<V> 가 render_<V>.log 끝에 ok 를 쓴 뒤) → 결과 _작업/04강/검사_<V>/
cd "${0:A:h}/../.."; V=$1; W=04강/work; O=04강/검사_$V; C=$W/chk_$V; mkdir -p $O $C; H=검수/heavy_run.sh; TL=04강/타임라인_$V.json; MP=04강/04강_$V.mp4
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
log "대기 시작"
while true; do
  if grep -qE "Traceback|Error|error" $W/render_$V.log 2>/dev/null; then log "렌더 에러"; tail -5 $W/render_$V.log >> $O/진행.log; exit 1; fi
  grep -qx "ok" $W/render_$V.log 2>/dev/null && break
  sleep 20
done
# 공용 검사 사본(파일 이름 v4c → $V · 강 번호 04) — 원본은 그대로
sed -e "s/v4c/$V/g" 20강/work/chk_v4c/check_text25.py > $C/check_text25.py
for f in edge16 still16 check16_frames; do sed -e "s/v4c/$V/g" -e "s#오더25/v4/place16.py#$C/place16.py#" 20강/work/chk_v4c/$f.py > $C/$f.py; done
sed -e 's#N = int(sys.argv\[1\]); D = f"{N}강"; tl = json.load(open(f"{D}/타임라인_v4.json"))#N = int(sys.argv[1]); D = f"{N:02d}강"; tl = json.load(open(f"{D}/타임라인_'$V'.json"))#' 오더25/v4/place16.py > $C/place16.py
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $MP); t=$(python3 -c "import json;print(json.load(open('$TL'))['total'])")
log "렌더 끝 길이 $d (타임라인 $t) · $(ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate -of csv=p=0 $MP | tr '\n' ' ')"; [ -z "$d" ] && { log "moov 없음"; exit 1; }
AX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
EX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']}\" for a in t['anchors']))")
log "anc-x(움직임 창) $AX · edge x $EX"
python3 $W/chk/announcer04.py $TL --mp4 $MP > $O/announcer.txt 2>&1; log "announcer exit=$?"
(cd 오더25 && python3 ../$C/check_text25.py 04) > $O/check_text.txt 2>&1; log "check_text $(tail -1 $O/check_text.txt)"
python3 검수/검사기/edge_check.py 04 --video $MP --timeline $TL --anc-x "$EX" --out $O/edge_check.json > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-80)"
python3 $C/edge16.py 04 > $O/경계16.txt 2>&1; log "경계16 exit=$? $(tail -1 $O/경계16.txt)"
python3 $C/check16_frames.py 4 > $O/배치16_프레임.txt 2>&1; log "배치16 exit=$? $(tail -1 $O/배치16_프레임.txt | cut -c1-60)"
python3 $C/still16.py 04 > $O/정지16.txt 2>&1; log "정지16 $(tail -1 $O/정지16.txt)"
python3 오더25/v4/end_check.py $MP $TL > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
python3 검수/검사기/line_break_check.py 04 --timeline $TL > $O/line_break.txt 2>&1; log "line_break 위반=$?"
python3 검수/검사기/newline_onset_check.py 04 --timeline $TL --prev $TL --all --json $O/newline_onset.json > $O/newline_onset.txt 2>&1; log "newline_onset exit=$? $(head -1 $O/newline_onset.txt | cut -c1-120)"
V=$V python3 $W/chk/gap_check04.py > $O/문장텀.txt 2>&1; log "문장텀 $(tail -1 $O/문장텀.txt | cut -c1-160)"
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py 04 --timeline $TL > $O/anchor_sync.txt 2>&1; log "anchor_sync exit=$? $(tail -1 $O/anchor_sync.txt | cut -c1-80)"
$H render python3 $W/chk/flash04.py $MP $TL $V > $O/흑백튐.txt 2>&1; log "흑백튐 exit=$? $(tail -1 $O/흑백튐.txt | cut -c1-60)"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $MP --timeline $TL --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$?"
log "끝(장 경계 조각 훑기는 따로: piece04)"
