#!/bin/zsh
# 10강 아나운서 「가」(warp_s flow) — 값 = DRYJSON+anchor_sync_check 로 고름(sweep.sh · dry/)
#  인삿말 = 타깃 _fix 사본(「입고부터」 시작 7.56→7.48 실소리) · PINS 7.48:10.40(클립에만 「의」 10.135~10.40 · 「입」 실측) · SIGMA .25 TOL .03 SMIN .45 SMAX 2.5 WP0 → dry 최대 0.092(마루: 타깃 받아쓰기 1.10 vs 실소리 1.13 → 실제 ≈0.06)
#  끝인사 = ONSETPAIR · SIGMA .2 TOL .01 SMIN .45 SMAX 2.3 WP0(20강 값 그대로) → dry 최대 0.070
cd "${0:A:h:h:h}"; O=10강/아나운서B; H=검수/heavy_run.sh; S=$O/warp_s10.py; A=10강/아나운서
env PINS=7.48:10.40 SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.5 WORDPAIR=0 MODE=flow $H render python3 $S $A/10_인삿말_090.mp4 $A/10_인삿말_090.wav $O/greet_a9_090_fix.wav $O/10_인삿말_flow.mp4 $O/10_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $A/10_끝인사_090.mp4 $A/10_끝인사_090.wav 10강/work/bye_tc_090.wav $O/10_끝인사_flow.mp4 $O/10_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE >> $O/run.log
