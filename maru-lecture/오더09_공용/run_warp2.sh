#!/bin/zsh
cd "${0:A:h}/.."
for n in 12 13 14 15; do
  if [ $n = 12 ]; then D=12강/인삿말; else D=${n}강/아나운서; fi
  for k in 인삿말 끝인사; do
    if [ $k = 인삿말 ]; then T=$(ls ${n}강/work/greet_a*_090.wav); else T=${n}강/work/bye_tc_090.wav; fi
    [ -f $D/${n}_${k}_warp2.json ] || 검수/heavy_run.sh render python3 오더09_공용/warp_clip2.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.mp4 $D/${n}_${k}_warp2.json 2>&1 | grep -E "^\{" 
  done
done
echo WARP2DONE
