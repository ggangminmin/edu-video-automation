#!/bin/zsh
cd "${0:A:h}"; H=../../검수/heavy_run.sh; P=~/.venvs/tts/bin/python
$H asr $P mlxw.py > mlxw.log 2>&1
$H asr whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -f v090_16k.wav -oj -ml 1 -sow -of wfull -np > wfull.log 2>&1
$H asr $P greet_tc.py > greet_tc.log 2>&1
echo DONE > asr1.done
