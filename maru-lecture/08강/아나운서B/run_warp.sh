#!/bin/zsh
# 08강 아나운서 「가」(warp_s flow) — 값 = DRYJSON+anchor_sync_check 로 고름(dry/ g14 · g17)
#  인삿말 = ONSETPAIR=1 SIGMA .25 TOL .01 SMIN .45 SMAX 2.3 → 입싱크 최대 0.051 · 소리시작 0.015 · 꺾임 0.38
#  끝인사 = ONSETPAIR=0 SIGMA .2 TOL .01 SMIN .45 SMAX 1.9 → 입싱크 최대 0.054 · 소리시작 0.029 · 꺾임 0.26
cd "${0:A:h:h}"; A=$PWD/아나운서; W=$PWD/work; O=$PWD/아나운서B; H=../검수/heavy_run.sh
env ONSETPAIR=1 SIGMA=0.25 TOL=0.01 SMIN=0.45 SMAX=2.3 MODE=flow $H render python3 $O/warp_s08.py $A/08_인삿말_090.mp4 $A/08_인삿말_090.wav $W/greet_tc_090.wav $O/08_인삿말_flow.mp4 $O/08_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=0 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=1.9 MODE=flow $H render python3 $O/warp_s08.py $A/08_끝인사_090.mp4 $A/08_끝인사_090.wav $W/bye_tc_090.wav $O/08_끝인사_flow.mp4 $O/08_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE >> $O/run.log
