#!/bin/zsh
# 오더23: 18 끝인사 손 고정점(클립 3.246~3.404 ↔ 타깃 2.205~2.417) → warp3c
cd "${0:A:h}/.."; H=검수/heavy_run.sh; C=오더09_공용; D=18강/아나운서; T=18강/work/bye_tc_090.wav
AN=$(head -1 $D/18_끝인사_anchor3c.txt)
$H render python3 $C/warp_clip2.py $D/18_끝인사_090.mp4 $D/18_끝인사_090.wav $T $D/18_끝인사_warp3c.mp4 $D/18_끝인사_warp3c.json "$AN" > /dev/null
python3 $C/onsetcheck.py $D/18_끝인사_090.wav $T $D/18_끝인사_warp3c.json | cut -c1-220
python3 오더15_16-20/pausecheck.py $D/18_끝인사_090.wav $T $D/18_끝인사_warp3c.json $D/18_끝인사_anchor3c.txt
python3 -c "import json;print('env',json.load(open('$D/18_끝인사_warp3c.json')).get('env_corr'))"
echo REWARP3C DONE
