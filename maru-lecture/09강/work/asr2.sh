#!/bin/zsh
cd "${0:A:h}"; B=../아나운서B
../../검수/heavy_run.sh asr ~/.venvs/tts/bin/python words_cache.py $B/9_인삿말_090.wav $B/9_끝인사_090.wav $B/greet_tc_090.wav $B/bye_tc_090.wav > asr2.log 2>&1
echo DONE > asr2.done
