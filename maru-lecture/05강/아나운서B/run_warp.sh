#!/bin/zsh
# 05강 아나운서 flow(오더48) — 값 = dry 비교(dry.sh/dryo.sh + anchor_sync_check)
#  인삿말 g1: _fix 사본(클립 「자재」 11.34→11.72 · 타깃 「마루시공」 0.64→1.12 · 「자재」 10.32→10.66 실측) · ONSETPAIR SIGMA .25 TOL .03 SMIN .45 SMAX 2.3 WP0 → 입싱크 최대 0.040 · 꺾임 0.34
#  끝인사 o7: 원본 캐시 · ONSETPAIR SIGMA .2 TOL .01 SMIN .45 SMAX 2.0 WP0 → 입싱크 최대 0.038 · 꺾임 0.20
cd "${0:A:h:h:h}"; O=05강/아나운서B; H=검수/heavy_run.sh; S=$O/warp_s05.py
env ONSETPAIR=1 SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.3 WORDPAIR=0 MODE=flow $H render python3 $S $O/5_인삿말_090_fix.mp4 $O/5_인삿말_090_fix.wav $O/greet_tc_090_fix.wav $O/5_인삿말_flow.mp4 $O/5_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=2.0 WORDPAIR=0 MODE=flow $H render python3 $S $O/5_끝인사_090.mp4 $O/5_끝인사_090.wav $O/bye_tc_090.wav $O/5_끝인사_flow.mp4 $O/5_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE > $O/warp.done
