#!/bin/zsh
cd "${0:A:h}/../../.."; n=13; O=13강/검사_v4; TL=13강/타임라인_v4.json; V=13강/13강_v4.mp4; H=검수/heavy_run.sh; W=13강/work
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $V); log "길이 $d"
python3 검수/검사기/announcer_audio_check.py $TL --mp4 $V > $O/announcer.txt 2>&1; log "announcer exit=$?"
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py 13 --timeline $TL > $O/anchor_sync.txt 2>&1; log "anchor_sync exit=$? $(tail -1 $O/anchor_sync.txt)"
(cd 오더21 && python3 check_text21.py $n) > $O/check_text.txt 2>&1; log "check_text $(tail -1 $O/check_text.txt)"
AX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))"); log "anc-x $AX"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $V --timeline $TL --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$?"
python3 $O/sc/check16_frames.py $n > $O/배치16_프레임.txt 2>&1; log "배치16 exit=$? $(tail -1 $O/배치16_프레임.txt | cut -c1-60)"
python3 $O/sc/edge16.py $n > $O/경계16.txt 2>&1; log "경계16 exit=$? $(tail -1 $O/경계16.txt)"
python3 $O/sc/still16.py $n > $O/정지16.txt 2>&1; log "정지16 $(tail -1 $O/정지16.txt)"
python3 검수/검사기/edge_check.py $n --video $V --timeline $TL --anc-x "$AX" > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-90)"
python3 오더24/end_check.py $V $TL > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
$H render python3 오더24/flash_check.py $V $TL > $O/흑백튐.txt 2>&1; log "흑백튐 exit=$? $(tail -1 $O/흑백튐.txt | cut -c1-60)"
log "끝"
