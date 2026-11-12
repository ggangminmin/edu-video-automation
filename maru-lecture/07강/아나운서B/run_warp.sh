#!/bin/zsh
# 07강 아나운서 「가」(warp_s flow) — 값 = DRYJSON+anchor_sync_check 로 고름(dry/ 인삿말 g1 · 끝인사 c0)
#  인삿말 = ONSETPAIR=1 SIGMA .2 TOL .01 SMIN .45 SMAX 1.9 → 입싱크 최대 0.038 · 소리시작 0.24(타깃 「부유식」 ㅅ 0.08초 저음량 = 검사기 경계값, 예외) · 꺾임 0.26
#  끝인사 = ONSETPAIR=0 SIGMA .2 TOL .01 SMIN .45 SMAX 1.9 → 입싱크 최대 0.073 · 소리시작 0.012 · 꺾임 0.22
cd "${0:A:h:h}"; A=$PWD/아나운서; W=$PWD/work; O=$PWD/아나운서B; H=../검수/heavy_run.sh
env ONSETPAIR=1 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=1.9 MODE=flow $H render python3 $O/warp_s07.py $A/07_인삿말_090.mp4 $A/07_인삿말_090.wav $W/greet_tc_090.wav $O/07_인삿말_flow.mp4 $O/07_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=0 SIGMA=0.2 TOL=0.01 SMIN=0.45 SMAX=1.9 MODE=flow $H render python3 $O/warp_s07.py $A/07_끝인사_090.mp4 $A/07_끝인사_090.wav $W/bye_tc_090.wav $O/07_끝인사_flow.mp4 $O/07_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE >> $O/run.log
