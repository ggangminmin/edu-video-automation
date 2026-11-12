#!/bin/zsh
cd "${0:A:h}"
zsh asr1.sh; zsh asr2.sh; echo ASRDONE >> asr1.done
