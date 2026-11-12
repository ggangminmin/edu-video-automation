#!/bin/zsh
# 18강 v4 아나운서 B방식 2판 — 1판(run_warp.sh) anchor_sync 걸림 → 고침:
#  인삿말 = warp_s18.py(ONSETPAIR: 쉼 뒤 시작점 짝 · 타깃 시작점 둘이 클립 하나에 걸리면 가운데) SIGMA .2 TOL .01 SMIN .55 SMAX 1.9 WP0
#  끝인사 = 공용 warp_s.py 17강 값 그대로 + 받아쓰기 단어 시작 고친 사본(bye_tc_090_fix · 18_끝인사_090_fix, 원본 그대로)
cd "${0:A:h:h:h}"; O=18강/아나운서B; A=18강/아나운서; W=18강/work; H=검수/heavy_run.sh
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.55 SMAX=1.9 WORDPAIR=0 MODE=flow $H render python3 $O/warp_s18.py $A/18_인삿말_090.mp4 $A/18_인삿말_090.wav $W/greet_a17_090.wav $O/18_인삿말_flow2.mp4 $O/18_인삿말_flow2.json > $O/warp2_인삿말.log 2>&1 &
env SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=1 MODE=flow $H render python3 오더09_공용/warp_s.py $O/18_끝인사_090_fix.mp4 $O/18_끝인사_090_fix.wav $O/bye_tc_090_fix.wav $O/18_끝인사_flow2.mp4 $O/18_끝인사_flow2.json > $O/warp2_끝인사.log 2>&1 &
wait; echo WARP2DONE >> $O/run.log
