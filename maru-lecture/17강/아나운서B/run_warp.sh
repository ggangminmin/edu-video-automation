#!/bin/zsh
# 17강 오프닝·클로징 B방식(warp_s MODE=flow, 13강 v4 와 같은 값) — 민석 11/3 「오프닝, 클로징 아나운서 부드럽게 + 광학효과」
cd "${0:A:h:h:h}"; O=17강/아나운서B; A=17강/아나운서; W=17강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.6 SMAX=1.7 WORDPAIR=0 MODE=flow $H render python3 오더09_공용/warp_s.py $A/17_인삿말_090.mp4 $A/17_인삿말_090.wav $W/greet_a16_090.wav $O/17_인삿말_flow.mp4 $O/17_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=1 MODE=flow $H render python3 오더09_공용/warp_s.py $A/17_끝인사_090.mp4 $A/17_끝인사_090.wav $W/bye_tc_090.wav $O/17_끝인사_flow.mp4 $O/17_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE
