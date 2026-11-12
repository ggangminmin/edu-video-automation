#!/bin/zsh
cd "${0:A:h}"; H=../../검수/heavy_run.sh; A=../아나운서; W=../work
for mode in blend flow; do for k in 인삿말 끝인사; do
  if [ $k = 인삿말 ]; then T=$W/greet_a12_090.wav; P=(SMIN=0.6 SMAX=1.7 WORDPAIR=0); else T=$W/bye_tc_090.wav; P=(SMIN=0.45 SMAX=2.3 WORDPAIR=1); fi
  o=13_${k}_${mode}
  [ -f $o.json ] || env SIGMA=0.25 TOL=0.03 $P MODE=$mode $H render python3 warp_s.py $A/13_${k}_090.mp4 $A/13_${k}_090.wav $T $o.mp4 $o.json &
done; wait; done; echo WARPDONE
