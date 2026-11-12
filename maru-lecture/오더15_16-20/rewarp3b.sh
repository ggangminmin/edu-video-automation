#!/bin/zsh
# 오더15-2: 대본 글자 자리로 짝지은 쉼 고정점(anchor_words.py)으로 다시 warp(_warp3b) → onsetcheck·lipcheck2
cd "${0:A:h}/.."; H=검수/heavy_run.sh; PY=~/.venvs/tts/bin/python; C=오더09_공용
for c in "18 인삿말" "18 끝인사" "19 인삿말" "19 끝인사" "20 인삿말" "20 끝인사"; do
  set -- ${=c}; n=$1; k=$2; D=${n}강/아나운서; [ $k = 인삿말 ] && T=${n}강/work/greet_a$((n-1))_090.wav || T=${n}강/work/bye_tc_090.wav
  ONE=0 python3 오더15_16-20/anchor_words.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.json > $D/${n}_${k}_anchor3b.txt
  AN=$(head -1 $D/${n}_${k}_anchor3b.txt); echo "=== $n $k 고정점 $AN"
  [ -f $D/${n}_${k}_warp3b.json ] || $H render python3 $C/warp_clip2.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3b.mp4 $D/${n}_${k}_warp3b.json "$AN" > /dev/null
  python3 $C/onsetcheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3b.json | cut -c1-220
  python3 오더15_16-20/pausecheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3b.json $D/${n}_${k}_anchor3b.txt
done
echo REWARP3B DONE
