#!/bin/zsh
# 값 찾기: warp_s10.py DRYJSON=1(지도 json 만) + anchor_sync_check --warp  · 사용: sweep.sh <인삿말|끝인사> <이름> "ENV=..."
cd "${0:A:h:h:h}"; O=10강/아나운서B; k=$1; nm=$2; shift 2
if [ $k = 인삿말 ]; then T=${T_GREET:-10강/work/greet_a9_090.wav}; else T=10강/work/bye_tc_090.wav; fi
env DRYJSON=1 MODE=flow "$@" python3 $O/warp_s10.py 10강/아나운서/10_${k}_090.mp4 10강/아나운서/10_${k}_090.wav $T $O/dry/${k}_$nm.mp4 $O/dry/${k}_$nm.json 2>/dev/null
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py --warp $O/dry/${k}_$nm.json 2>&1 | grep -vE "^\s*$" | tail -4
