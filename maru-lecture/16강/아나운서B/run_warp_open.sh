#!/bin/zsh
# 16강 오프닝(인삿말) B방식 — 오더33 · 12강 인삿말 값(SMIN 0.6 SMAX 2.5 WORDPAIR 0)
cd "${0:A:h:h:h}"; O=16강/아나운서B; A=16강/아나운서; W=16강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.6 SMAX=2.5 WORDPAIR=0 MODE=flow $H render python3 오더09_공용/warp_s.py $A/16_인삿말_090.mp4 $A/16_인삿말_090.wav $W/greet_a15_090.wav $O/16_인삿말_flow.mp4 $O/16_인삿말_flow.json > $O/warp_인삿말.log 2>&1
echo WARPDONE >> $O/warp_인삿말.log
