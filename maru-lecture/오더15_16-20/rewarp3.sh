#!/bin/zsh
# 오더15-2: 대본 글자 자리로 짝지은 쉼 고정점(anchor_words.py)으로 다시 warp(_warp3) → onsetcheck·lipcheck2
cd "${0:A:h}/.."; H=검수/heavy_run.sh; PY=~/.venvs/tts/bin/python; C=오더09_공용
for c in "18 인삿말" "18 끝인사" "19 인삿말" "19 끝인사" "20 인삿말" "20 끝인사"; do
  set -- ${=c}; n=$1; k=$2; D=${n}강/아나운서; [ $k = 인삿말 ] && T=${n}강/work/greet_a$((n-1))_090.wav || T=${n}강/work/bye_tc_090.wav
  python3 오더15_16-20/anchor_words.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.json > $D/${n}_${k}_anchor3.txt
  AN=$(head -1 $D/${n}_${k}_anchor3.txt); echo "=== $n $k 고정점 $AN"
  [ -f $D/${n}_${k}_warp3.json ] || $H render python3 $C/warp_clip2.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3.mp4 $D/${n}_${k}_warp3.json "$AN" > /dev/null
  python3 $C/onsetcheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3.json | cut -c1-220
  python3 오더15_16-20/pausecheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3.json $D/${n}_${k}_anchor3.txt
  $H asr $PY $C/lipcheck2.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp3.json 2>&1 | grep -v Fetching | cut -c1-220
done
echo REWARP3 DONE
