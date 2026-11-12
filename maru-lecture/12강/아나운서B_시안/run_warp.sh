#!/bin/zsh
# 오더32: 12강 아나운서 B방식(warp_s MODE=flow) — 실행 위치 _작업
cd "${0:A:h:h:h}"; O=12강/아나운서B_시안; I=12강/인삿말; W=12강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.6 SMAX=2.5 WORDPAIR=0 MODE=flow $H render python3 오더09_공용/warp_s.py $I/12_인삿말_090.mp4 $I/12_인삿말_090.wav $W/greet_a11_090.wav $O/12_인삿말_flow.mp4 $O/12_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=1 MODE=flow $H render python3 오더09_공용/warp_s.py $I/12_끝인사_090.mp4 $I/12_끝인사_090.wav $W/bye_tc_090.wav $O/12_끝인사_flow.mp4 $O/12_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE
