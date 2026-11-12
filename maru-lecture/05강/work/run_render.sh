#!/bin/zsh
# 사용: run_render.sh v1  → heavy_run render 로 render05.py
cd "${0:A:h}"; v=$1
env VER=$v ../../검수/heavy_run.sh render python3 render05.py > render_$v.log 2>&1; echo "exit $?" >> render_$v.log
