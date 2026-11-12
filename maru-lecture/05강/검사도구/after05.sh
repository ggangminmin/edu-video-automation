#!/bin/zsh
# 05강 렌더 뒤 검사대(오더48 · 09강 after09 사본 · 20강 after_render_v4c.sh 방식 + 오더44 5번 칸 전부) · 사용: after05.sh v2  (결과 05강/검사_v2/)
cd "${0:A:h:h:h}"; v=$1; n=05; W=05강/work; O=05강/검사_$v; mkdir -p $O; H=검수/heavy_run.sh; TL=05강/타임라인_$v.json; MP=05강/05강_$v.mp4; PY=~/.venvs/tts/bin/python
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
log "대기 시작"
while true; do
  if grep -qE "Traceback|Error|exit [1-9]" $W/render_$v.log 2>/dev/null; then log "렌더 에러"; tail -5 $W/render_$v.log >> $O/진행.log; exit 1; fi
  grep -q "^ok" $W/render_$v.log 2>/dev/null && break
  sleep 20
done
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $MP); t=$(python3 -c "import json;print(json.load(open('$TL'))['total'])")
log "렌더 끝 길이 $d (타임라인 $t)"; [ -z "$d" ] && { log "moov 없음"; exit 1; }
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate -of compact $MP > $O/규격.txt
python3 05강/검사도구/announcer_audio_check05.py $TL --mp4 $MP > $O/announcer.txt 2>&1; log "announcer exit=$?"
python3 05강/검사도구/check_text05.py $v > $O/check_text.txt 2>&1; log "check_text $(tail -1 $O/check_text.txt)"
AX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
EX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']}\" for a in t['anchors']))")
log "anc-x scene $AX · edge $EX"
python3 검수/검사기/edge_check.py $n --video $MP --timeline $TL --anc-x "$EX" > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-80)"
python3 05강/검사도구/frames05.py $v > $O/배치16_프레임.txt 2>&1; log "배치 exit=$? $(cut -c1-40 $O/배치16_프레임.txt)"
python3 05강/검사도구/still05.py $v > $O/정지16.txt 2>&1; log "정지 $(tail -1 $O/정지16.txt)"
python3 05강/검사도구/gap_check05.py $v > $O/문장텀.txt 2>&1; log "문장텀 exit=$? $(cut -c1-60 $O/문장텀.txt)"
python3 05강/검사도구/end_survey05.py $v > $O/end_survey.txt 2>&1; log "end_survey exit=$? $(head -1 $O/end_survey.txt | cut -c1-80)"
python3 오더25/v4/end_check.py $MP $TL > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
$PY 검수/검사기/anchor_sync_check.py $n --timeline $TL > $O/anchor_sync.txt 2>&1; log "anchor_sync exit=$? $(tail -1 $O/anchor_sync.txt)"
python3 검수/검사기/line_break_check.py $n --timeline $TL > $O/line_break.txt 2>&1; log "line_break 위반=$?"
python3 검수/검사기/newline_onset_check.py $n --timeline $TL --prev $TL --all --quiet --json $O/newline_onset.json > $O/newline_onset.txt 2>&1; log "newline_onset exit=$? $(head -1 $O/newline_onset.txt | cut -c40-130)"
$H asr $PY 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $MP --timeline $TL --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$?"
$H asr $PY 05강/검사도구/piece05.py $v > $O/경계_조각.txt 2>&1; log "경계조각 exit=$? $(tail -1 $O/경계_조각.txt)"
$H render python3 05강/검사도구/flash05.py $MP $TL $O/흑백튐.json > $O/흑백튐.txt 2>&1; log "흑백튐 exit=$? $(tail -1 $O/흑백튐.txt | cut -c1-60)"
log "끝"
