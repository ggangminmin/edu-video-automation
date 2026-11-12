#!/bin/zsh
# 20강 아나운서 B방식 2판(오더34) — 1판 anchor_sync 걸림 → 값 고름(DRYJSON + anchor_sync_check · warp_s1920.py = 18강 warp_s18.py + DRYJSON + PINS)
#  인삿말 = _fix 사본(「앞으로의」 시작 실측) · PINS 1.1:2.23(마루시공, 클립에만 쉼) 8.42:10.85 12.55:15.43 15.54:18.75(쉼 끝 실측) · SIGMA .25 TOL .03 SMIN .45 SMAX 2.5 WP0 → 통과
#  끝인사 = _fix 사본(클립 「배운」 · 타깃 「끝까지」 시작 실측) · ONSETPAIR · SIGMA .2 TOL .01 SMIN .45 SMAX 2.3 WP0 → 통과
cd "${0:A:h:h:h}"; O=20강/아나운서B; H=검수/heavy_run.sh; S=$O/warp_s1920.py
env PINS=1.1:2.23,8.42:10.85,12.55:15.43,15.54:18.75 SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.5 WORDPAIR=0 MODE=flow $H render python3 $S $O/20_인삿말_090_fix.mp4 $O/20_인삿말_090_fix.wav $O/greet_a19_090_fix.wav $O/20_인삿말_flow2.mp4 $O/20_인삿말_flow2.json > $O/warp2_인삿말.log 2>&1 &
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $O/20_끝인사_090_fix.mp4 $O/20_끝인사_090_fix.wav $O/bye_tc_090_fix.wav $O/20_끝인사_flow2.mp4 $O/20_끝인사_flow2.json > $O/warp2_끝인사.log 2>&1 &
wait; echo WARP2DONE >> $O/run.log
