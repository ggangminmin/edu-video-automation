#!/bin/zsh
# 10강 받아쓰기(heavy_run asr): whisper.cpp 단어(wfull.json) → mlx 단어(mlxwords.json) → 인삿말 단어
cd "${0:A:h}"; H=../../검수/heavy_run.sh; PY=~/.venvs/tts/bin/python
echo "$(date +%T) cpp 시작"
[ -f wfull.json ] || $H asr whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -ml 1 -sow -ojf -of wfull -f v090_16k.wav > wcpp.log 2>&1
echo "$(date +%T) cpp 끝 $?"
[ -f mlxwords.json ] || $H asr $PY mlxw.py > mlx.log 2>&1
echo "$(date +%T) mlx 끝 $?"
echo ASRDONE
