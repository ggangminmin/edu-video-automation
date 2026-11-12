#!/bin/zsh
# 오더13: 렌더 끝나면 스스로 → ffprobe 길이(moov) → announcer_audio_check --mp4 · check_text09 · scene_sub_check(asr 칸)
# 사용: after_render.sh NN   (결과 _작업/NN강/검사_v5b/)
cd "${0:A:h}/../.."; n=$1; W=${n}강/work; O=${n}강/검사_v5b; mkdir -p $O; H=검수/heavy_run.sh
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
log "대기 시작"; [ "$SKIP_TO" = "1" ] && true
while true; do
  if grep -qE "Traceback|Error|error" $W/render_v5b.log 2>/dev/null; then log "렌더 에러"; tail -5 $W/render_v5b.log >> $O/진행.log; exit 1; fi
  [ "$(tail -1 $W/render_v5b.log 2>/dev/null)" = "ok" ] && break
  sleep 20
done
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 ${n}강/${n}강_v5b.mp4); t=$(python3 -c "import json;print(json.load(open('${n}강/타임라인_v5b.json'))['total'])")
log "렌더 끝 길이 $d (타임라인 $t)"; [ -z "$d" ] && { log "moov 없음"; exit 1; }
python3 검수/검사기/announcer_audio_check.py ${n}강/타임라인_v5b.json --mp4 ${n}강/${n}강_v5b.mp4 > $O/announcer.txt 2>&1; log "announcer exit=$?"
(cd 오더25 && python3 ../16강/work/chk5b/check_text25.py $n) > $O/check_text.txt 2>&1; log "check_text $(tail -1 $O/check_text.txt)"
AX=$(python3 -c "import json;t=json.load(open('${n}강/타임라인_v5b.json'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")   # p6: 옮긴 아나운서 움직임 검사 창(기본 1130 = 934+196 / 952+178)
log "anc-x $AX"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video ${n}강/${n}강_v5b.mp4 --timeline ${n}강/타임라인_v5b.json --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$?"
python3 16강/work/chk5b/check16_frames.py $n > $O/배치16_프레임.txt 2>&1; log "배치16 exit=$? $(tail -1 $O/배치16_프레임.txt | cut -c1-40)"
python3 16강/work/chk5b/edge16.py $n > $O/경계16.txt 2>&1; log "경계16 exit=$? $(tail -1 $O/경계16.txt)"
python3 16강/work/chk5b/still16.py $n > $O/정지16.txt 2>&1; log "정지16 $(tail -1 $O/정지16.txt)"
python3 검수/검사기/edge_check.py $n --video ${n}강/${n}강_v5b.mp4 --timeline ${n}강/타임라인_v5b.json --anc-x "$AX" > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-80)"
python3 16강/work/chk5b/gap_check21.py $n > $O/문장텀.txt 2>&1; log "문장텀 $(tail -1 $O/문장텀.txt | cut -c1-60)"
python3 16강/work/chk5b/end_check.py ${n}강/${n}강_v5b.mp4 ${n}강/타임라인_v5b.json > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
$H render python3 16강/work/chk5b/flash_check.py ${n}강/${n}강_v5b.mp4 ${n}강/타임라인_v5b.json > $O/흑백튐.txt 2>&1; log "흑백튐 exit=$? $(tail -1 $O/흑백튐.txt | cut -c1-60)"
log "끝"
