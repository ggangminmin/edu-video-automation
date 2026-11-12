#!/bin/zsh
# 오더33 15강 인삿말 B(warp_s MODE=flow, 12강 인삿말 값 SMIN 0.6 SMAX 2.5 WORDPAIR 0) — 실행 위치 _작업
cd "${0:A:h:h:h}"; O=15강/아나운서B; A=15강/아나운서; W=15강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.6 SMAX=2.5 WORDPAIR=0 MODE=flow $H render python3 오더09_공용/warp_s.py $A/15_인삿말_090.mp4 $A/15_인삿말_090.wav $W/greet_a14_090.wav $O/15_인삿말_flow.mp4 $O/15_인삿말_flow.json > $O/warp_인삿말.log 2>&1
echo WARPDONE >> $O/warp_인삿말.log
