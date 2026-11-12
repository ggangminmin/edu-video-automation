#!/bin/zsh
# 값 찾기: dry.sh <이름> <클립> <타깃> env...   (_작업 기준 경로로 → anchor_sync_check 가 wav 찾음)
n=$1; c=$2; t=$3; shift 3; cd "${0:A:h:h:h}"; O=09강/아나운서B
env DRYJSON=1 MODE=flow "$@" python3 $O/warp_s09.py $O/9_${c}_090_fix.mp4 $O/9_${c}_090_fix.wav $O/$t $O/dry/$n.mp4 $O/dry/$n.json 2>/dev/null
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py --warp $O/dry/$n.json 2>&1 | grep -E '✓|✗|걸림:' | sed "s/^/$n /"
