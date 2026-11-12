#!/bin/zsh
cd "${0:A:h}"; H=../../검수/heavy_run.sh
$H asr ~/.venvs/tts/bin/python mlxw.py > mlx.log 2>&1; echo "mlx $?" >> asr1.done
$H asr whisper-cli -m ~/.cache/whisper-cpp/ggml-large-v3-turbo.bin -l ko -ml 1 -sow -ojf -of wfull -f v090_16k.wav > wcpp.log 2>&1; echo "cpp $?" >> asr1.done
