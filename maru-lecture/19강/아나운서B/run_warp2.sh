#!/bin/zsh
# 19강 아나운서 B방식 2판(오더34) — 1판(run_warp.sh, 11강 값) anchor_sync 걸림 → 값 고름(영상 없는 DRYJSON 으로 anchor_sync_check 돌려 고름 · 20강/아나운서B/warp_s1920.py = 18강 warp_s18.py + DRYJSON + PINS)
#  인삿말 = 원본 입력 · ONSETPAIR · SIGMA .2 TOL .01 SMIN .45 SMAX 2.3 WP0 → 통과
#  끝인사 = _fix 사본(「자료에서」 받아쓰기 시작 → 실측 소리 시작) · PINS 3.28:4.04(자료에서) 6.92:7.10(20강에서는, 쉼 끝 실측) · SIGMA .25 TOL .03 SMIN .45 SMAX 2.3 WP0
cd "${0:A:h:h:h}"; O=19강/아나운서B; A=19강/아나운서; W=19강/work; H=검수/heavy_run.sh; S=20강/아나운서B/warp_s1920.py
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $A/19_인삿말_090.mp4 $A/19_인삿말_090.wav $W/greet_a18_090.wav $O/19_인삿말_flow2.mp4 $O/19_인삿말_flow2.json > $O/warp2_인삿말.log 2>&1 &
env PINS=3.28:4.04,6.92:7.10 SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $O/19_끝인사_090_fix.mp4 $O/19_끝인사_090_fix.wav $O/bye_tc_090_fix.wav $O/19_끝인사_flow2.mp4 $O/19_끝인사_flow2.json > $O/warp2_끝인사.log 2>&1 &
wait; echo WARP2DONE >> $O/run.log
