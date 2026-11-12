#!/bin/zsh
# 오더23: NN강 v3 렌더(heavy_run render) → after_v3.sh 검사 · 사용: nohup 오더23/run_v3.sh NN &
cd "${0:A:h}/.."; n=$1; W=${n}강/work; H=$PWD/검수/heavy_run.sh
(cd $W && $H render python3 render_v3.py > render_v3.log 2>&1)
오더23/after_v3.sh $n
echo "$(date +%T) RUN_V3 DONE $n" >> 오더23/run_v3.log
