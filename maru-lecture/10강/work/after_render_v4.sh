#!/bin/zsh
# 10강 v3(오더51 토막 자막) = after_render_v2.sh 사본(v2→v3) + short_card · newline_onset(--prev v2) · end_survey · mix_v2=mix_v4 · 장 경계 조각 훑기
# (옛) 10강(오더43) v1 렌더 뒤 검사대 = 20강 after_render_v4c.sh 사본(이름 v1 · chk_v4 사본) + piece10 은 렌더 전 따로
cd "${0:A:h}/../.."; n=10; W=${n}강/work; O=${n}강/검사_v4; mkdir -p $O; H=검수/heavy_run.sh
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
log "대기 시작"
while true; do
  if grep -qE "Traceback|Error|error" $W/render_v4.log 2>/dev/null; then log "렌더 에러"; tail -5 $W/render_v4.log >> $O/진행.log; exit 1; fi
  [ "$(tail -1 $W/render_v4.log 2>/dev/null)" = "ok" ] && break
  sleep 20
done
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ${n}강/${n}강_v4.mp4); t=$(python3 -c "import json;print(json.load(open('${n}강/타임라인_v4.json'))['total'])")
log "렌더 끝 길이 $d (타임라인 $t)"; [ -z "$d" ] && { log "moov 없음"; exit 1; }
python3 검수/검사기/announcer_audio_check.py ${n}강/타임라인_v4.json --mp4 ${n}강/${n}강_v4.mp4 > $O/announcer.txt 2>&1; log "announcer exit=$?"
(cd 오더25 && python3 ../10강/work/chk_v4/check_text25.py $n) > $O/check_text.txt 2>&1; log "check_text $(tail -1 $O/check_text.txt)"
AX=$(python3 -c "import json;t=json.load(open('${n}강/타임라인_v4.json'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
log "anc-x $AX"
python3 검수/검사기/edge_check.py $n --video ${n}강/${n}강_v4.mp4 --timeline ${n}강/타임라인_v4.json --anc-x "$AX" > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-80)"
python3 10강/work/chk_v4/check16_frames.py $n > $O/배치16_프레임.txt 2>&1; log "배치16 exit=$? $(tail -1 $O/배치16_프레임.txt | cut -c1-60)"
python3 10강/work/chk_v4/edge16.py $n > $O/경계16.txt 2>&1; log "경계16 exit=$? $(tail -1 $O/경계16.txt)"
python3 10강/work/chk_v4/still16.py $n > $O/정지16.txt 2>&1; log "정지16 $(tail -1 $O/정지16.txt)"
python3 10강/work/chk_v4/gap_check21.py $n > $O/문장텀.txt 2>&1; log "문장텀 $(tail -1 $O/문장텀.txt | cut -c1-80)"
python3 오더25/v4/end_check.py ${n}강/${n}강_v4.mp4 ${n}강/타임라인_v4.json > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
$H render python3 10강/work/chk_v4/flash_check.py ${n}강/${n}강_v4.mp4 ${n}강/타임라인_v4.json > $O/흑백튐.txt 2>&1; log "흑백튐 exit=$? $(tail -1 $O/흑백튐.txt | cut -c1-60)"
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py $n --timeline ${n}강/타임라인_v4.json > $O/anchor_sync.txt 2>&1; log "anchor_sync exit=$? $(tail -1 $O/anchor_sync.txt | cut -c1-80)"
python3 검수/검사기/line_break_check.py $n --timeline ${n}강/타임라인_v4.json > $O/line_break.txt 2>&1; log "line_break 위반=$?"
python3 검수/검사기/newline_onset_check.py $n --timeline ${n}강/타임라인_v4.json --prev ${n}강/타임라인_v2.json --json $O/newline_onset.json > $O/newline_onset.txt 2>&1; log "newline_onset(바뀐 줄) exit=$? $(head -1 $O/newline_onset.txt | cut -c1-110)"
python3 검수/검사기/short_card_check.py ${n}강/타임라인_v4.json > $O/short_card.txt 2>&1; log "short_card exit=$? $(tail -1 $O/short_card.txt)"
python3 오더23/end_survey.py $n 타임라인_v4.json > $O/end_survey.txt 2>&1; cp 오더23/end_survey_${n}.json $O/end_survey.json; log "end_survey $(tail -1 $O/end_survey.txt | cut -c1-90)"
python3 10강/work/v3/mixcmp.py $W/mix_v3.wav $W/mix_v4.wav > $O/mix_same.txt 2>&1; log "mix v3=v4 $(cat $O/mix_same.txt)"
$H asr ~/.venvs/tts/bin/python 10강/work/piece10.py ${n}강/타임라인_v4.json $O > $O/piece.txt 2>&1; log "조각 훑기 exit=$? $(tail -1 $O/piece.txt | cut -c1-90)"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video ${n}강/${n}강_v4.mp4 --timeline ${n}강/타임라인_v4.json --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$?"
log "끝"
