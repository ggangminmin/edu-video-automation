#!/bin/zsh
# 오더09 무거운 단계 — 한 강씩, 명령마다 lockf
cd "${0:A:h}/.."
L=.heavy.lock; PY=~/.venvs/tts/bin/python
for n in 12 13 14 15; do
  if [ $n = 12 ]; then D=12강/인삿말; else D=${n}강/아나운서; fi
  W=${n}강/work
  for k in 인삿말 끝인사; do
    if [ $k = 인삿말 ]; then T=$(ls $W/greet_a*_090.wav); else T=$W/bye_tc_090.wav; fi
    [ -f $D/${n}_${k}_warp.json ] || lockf -k $L python3 오더09_공용/warp_clip.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp.mp4 $D/${n}_${k}_warp.json
    [ -f $D/${n}_${k}_warp_lip.json ] || lockf -k $L $PY 오더09_공용/lipcheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp.json
  done
  lockf -k $L $PY 오더09_공용/words.py $W/greet_a*_090.wav $W/bye_tc_090.wav
  echo "== $n done $(date +%T)"
done
echo ALLDONE
