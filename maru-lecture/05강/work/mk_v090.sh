#!/bin/zsh
cd "${0:A:h}"; M="../../../녹음_본문_04-20강/마루시공_-_05강.mp3"
ffmpeg -v error -y -i "$M" -af atempo=0.9 -ar 48000 -ac 2 -c:a pcm_s16le v090.wav && ffmpeg -v error -y -i v090.wav -ar 16000 -ac 1 -c:a pcm_s16le v090_16k.wav && echo DONE > v090.done
