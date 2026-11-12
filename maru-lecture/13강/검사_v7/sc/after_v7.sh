#!/bin/zsh
# 13강 v7 검사(팀장 지정: newline_onset 걸림 0 + scene_sub · edge) + 끝 검정 · mix 비교
cd "${0:A:h}/../../.."; n=13; O=13강/검사_v7; TL=13강/타임라인_v7.json; V=13강/13강_v7.mp4; H=검수/heavy_run.sh; W=13강/work
log(){ echo "$(date +%T) $*" >> $O/진행.log; }
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $V); log "길이 $d · sha $(shasum -a 256 $V | cut -c1-16)"
python3 검수/검사기/newline_onset_check.py $n --timeline $TL --prev 13강/타임라인_v6.json --json $O/newline_onset.json > $O/newline_onset.txt 2>&1; log "newline_onset exit=$? $(head -1 $O/newline_onset.txt | cut -c1-120)"
python3 검수/검사기/line_break_check.py $n --timeline $TL > $O/line_break.txt 2>&1; log "line_break exit=$? $(head -1 $O/line_break.txt)"
AX=$(python3 -c "import json;t=json.load(open('$TL'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
python3 검수/검사기/edge_check.py $n --video $V --timeline $TL --anc-x "$AX" --out $O/edge.json > $O/edge_check.txt 2>&1; log "edge_check exit=$? $(tail -1 $O/edge_check.txt | cut -c1-90)"
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $V --timeline $TL --voice $W/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1; log "scene_sub exit=$? $(tail -1 $O/scene_sub.txt | cut -c1-120)"
python3 오더24/end_check.py $V $TL > $O/end_check.txt 2>&1; log "end_check exit=$? $(tail -1 $O/end_check.txt)"
cmp -s $W/mix_v6.wav $W/mix_v7.wav && log "mix_v6 = mix_v7 (바이트 같음)" || log "mix_v6 ≠ mix_v7"
log "끝"
