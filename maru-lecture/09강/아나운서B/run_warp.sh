#!/bin/zsh
# 09강 아나운서 flow(오더44) — 값 = dry 비교(dry.sh/dryo.sh + anchor_sync_check)
#  인삿말 g5: _fix 사본(「각」 클립 11.72→12.16 · 타깃 10.26→10.50 실측) · ONSETPAIR SIGMA .25 TOL .03 SMIN .45 SMAX 2.3 WP0 → 입싱크 최대 0.033 · 꺾임 0.26
#  끝인사 b10: 원본 캐시 · ONSETPAIR SIGMA .2 TOL .01 SMIN .45 SMAX 2.0 WP0 → 입싱크 최대 0.053 · 꺾임 0.42
cd "${0:A:h:h:h}"; O=09강/아나운서B; H=검수/heavy_run.sh; S=$O/warp_s09.py
env ONSETPAIR=1 SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $O/9_인삿말_090_fix.mp4 $O/9_인삿말_090_fix.wav $O/greet_tc_090_fix.wav $O/9_인삿말_flow.mp4 $O/9_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=2.0 WORDPAIR=0 MODE=flow $H render python3 $S $O/9_끝인사_090.mp4 $O/9_끝인사_090.wav $O/bye_tc_090.wav $O/9_끝인사_flow.mp4 $O/9_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE > $O/warp.done
