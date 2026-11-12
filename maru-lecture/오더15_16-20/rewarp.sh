#!/bin/zsh
# 오더15: 입싱크 0.1초 넘은 클립 → 쉼 고정점 넣어 다시 warp(_warp2a) → onsetcheck·lipcheck2 비교
cd "${0:A:h}/.."; H=검수/heavy_run.sh; PY=~/.venvs/tts/bin/python; C=오더09_공용
for c in "18 인삿말" "18 끝인사" "19 인삿말" "19 끝인사" "20 인삿말" "20 끝인사"; do
  set -- ${=c}; n=$1; k=$2; D=${n}강/아나운서; [ $k = 인삿말 ] && T=${n}강/work/greet_a$((n-1))_090.wav || T=${n}강/work/bye_tc_090.wav
  AN=$(python3 오더15_16-20/auto_anchor.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.json)
  echo "=== $n $k 고정점 $AN"
  [ -f $D/${n}_${k}_warp2a.json ] || $H render python3 $C/warp_clip2.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2a.mp4 $D/${n}_${k}_warp2a.json "$AN" > /dev/null
  python3 $C/onsetcheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2a.json | cut -c1-200
  $H asr $PY $C/lipcheck2.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2a.json 2>&1 | grep -v Fetching | cut -c1-200
done
echo REWARP DONE
