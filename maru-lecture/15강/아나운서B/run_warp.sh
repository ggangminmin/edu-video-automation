#!/bin/zsh
# 15강 클로징(끝인사)만 B방식(warp_s MODE=flow, 13강 v4 와 같은 값) — 실행 위치 _작업 · 민석 11/3
cd "${0:A:h:h:h}"; O=15강/아나운서B; A=15강/아나운서; W=15강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=1 MODE=flow $H render python3 오더09_공용/warp_s.py $A/15_끝인사_090.mp4 $A/15_끝인사_090.wav $W/bye_tc_090.wav $O/15_끝인사_flow.mp4 $O/15_끝인사_flow.json > $O/warp_끝인사.log 2>&1
echo WARPDONE >> $O/warp_끝인사.log
# 오더33: 인삿말도 B(12강 인삿말 값) — RUN=인삿말 일 때만
