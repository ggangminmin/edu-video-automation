#!/bin/zsh
# 16강 오프닝 B방식 3차(SMAX 2.5) — 1차(WORDPAIR 0)는 「마루시공」 실제 0.6초 늦음(타입캐스트 안녕하세요 0.42초 vs 클립 0.85초) → 단어짝 고정 켬 · SMAX 3.0
cd "${0:A:h:h:h}"; O=16강/아나운서B; A=16강/아나운서; W=16강/work; H=검수/heavy_run.sh
env SIGMA=0.25 TOL=0.03 SMIN=0.45 SMAX=2.5 WORDPAIR=1 MODE=flow $H render python3 오더09_공용/warp_s.py $A/16_인삿말_090.mp4 $A/16_인삿말_090.wav $W/greet_a15_090.wav $O/16_인삿말_flow3.mp4 $O/16_인삿말_flow3.json > $O/warp_인삿말3.log 2>&1
echo WARPDONE >> $O/warp_인삿말3.log
