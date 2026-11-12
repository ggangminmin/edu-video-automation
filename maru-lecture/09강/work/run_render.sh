#!/bin/zsh
# 사용: run_render.sh v1  → heavy_run render 로 render09.py
cd "${0:A:h}"; v=$1
env VER=$v ../../검수/heavy_run.sh render python3 render09.py > render_$v.log 2>&1; echo "exit $?" >> render_$v.log
