#!/bin/zsh
# 04강 아나운서 「가」(warp_s flow) — 값 = DRYJSON+anchor_sync_check 로 고름(dry/ n1 · f7)
#  클립 = *_090_fix.mp4(심링크)+_fix.wav(복사) → _fix_words.json(쉼 끝·자르기 받아쓰기로 고친 단어 시작) · 타깃 = greet_tc_090_fix / bye_tc_090_fix
#  인삿말 n1 = ONSETPAIR=1 SIGMA .25 TOL .01 SMIN .45 SMAX 2.5 PINS 「바닥」9.00:12.875 · 「상태를」9.60:13.27 → 입싱크 최대 0.096 · 소리시작 9.73 = 「과」 앞 0.09 막힘 쉼(타깃만) 짝 다툼 = 예외
#  끝인사 f7 = ONSETPAIR=0 SIGMA .23 TOL .015 SMIN .45 SMAX 2.3 PINS 「5강에서는」10.997:11.333 · 「공구와」13.559:14.087 · 「발주」15.456:16.07 → 입싱크 최대 0.081 · 소리시작 0.072 · 꺾임 0.54 ✓
cd "${0:A:h:h}"; A=$PWD/아나운서; W=$PWD/work; O=$PWD/아나운서B; H=../검수/heavy_run.sh
env ONSETPAIR=1 SIGMA=0.25 TOL=0.01 SMIN=0.45 SMAX=2.5 PINS=9.00:12.875,9.60:13.27 MODE=flow $H render python3 $O/warp_s04.py $A/04_인삿말_090_fix.mp4 $A/04_인삿말_090_fix.wav $W/greet_tc_090_fix.wav $O/04_인삿말_flow.mp4 $O/04_인삿말_flow.json > $O/warp_인삿말.log 2>&1 &
env ONSETPAIR=0 SIGMA=0.23 TOL=0.015 SMIN=0.45 SMAX=2.3 PINS=10.997:11.333,13.559:14.087,15.456:16.07 MODE=flow $H render python3 $O/warp_s04.py $A/04_끝인사_090_fix.mp4 $A/04_끝인사_090_fix.wav $W/bye_tc_090_fix.wav $O/04_끝인사_flow.mp4 $O/04_끝인사_flow.json > $O/warp_끝인사.log 2>&1 &
wait; echo WARPDONE >> $O/run.log
