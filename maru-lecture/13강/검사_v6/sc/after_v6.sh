#!/bin/zsh
# 13강 v6 검사 묶음 (팀장 지정: line_break · edge(fade_in) · announcer_audio · anchor_sync · scene_sub) + 끝 검정
cd "${0:A:h}/../../.."; n=13; O=13강/검사_v6; TL=13강/타임라인_v6.json; V=13강/13강_v6.mp4; H=검수/heavy_run.sh; W=13강/work
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $V); log "길이 $d · sha $(shasum -a 256 $V | cut -c1-16)"
python3 검수/검사기/line_break_check.py $n --timeline $TL > $O/line_break.txt 2>&1; log "line_break exit=$? $(head -1 $O/line_break.txt)"
python3 검수/검사기/announcer_audio_check.py $TL --mp4 $V > $O/announcer.txt 2>&1; log "announcer exit=$? $(tail -1 $O/announcer.txt)"
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py $n --timeline $TL > $O/anchor_sync.txt 2>&1; log "anchor_sync exit=$? $(tail -1 $O/anchor_sync.txt)"
AX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
python3 검수/검사기/edge_check.py $n --video $V --timeline $TL --anc-x "$AX" --out $O/edge.json > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-90)"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $V --timeline $TL --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$? $(tail -1 $O/scene_sub.txt | cut -c1-120)"
python3 오더24/end_check.py $V $TL > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
log "끝"
