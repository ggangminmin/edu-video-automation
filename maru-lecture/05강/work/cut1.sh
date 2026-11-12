#!/bin/zsh
cd "${0:A:h}"; ../../검수/heavy_run.sh render python3 cut_greet.py > cut_greet.log 2>&1; echo DONE > cut1.done
