#!/bin/zsh
# 사용: dry.sh <인삿말|끝인사> <이름> [ENV=..]  → dry/<k>_<이름>.json + anchor_sync 결과
cd "${0:A:h:h}"; A=$PWD/아나운서; W=$PWD/work; D=$PWD/아나운서B/dry; k=$1; n=$2; shift 2
[[ $k == 인삿말 ]] && T=$W/greet_tc_090.wav || T=$W/bye_tc_090.wav
env DRYJSON=1 MODE=flow "$@" python3 아나운서B/warp_s07.py $A/07_${k}_090.mp4 $A/07_${k}_090.wav $T $D/${k}_$n.mp4 $D/${k}_$n.json > $D/${k}_$n.log 2>&1
~/.venvs/tts/bin/python ../검수/검사기/anchor_sync_check.py --warp $D/${k}_$n.json 2>&1 | grep -v "^타임라인"
