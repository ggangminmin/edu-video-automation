#!/bin/zsh
# 오더32 구간 시안: 가=0.5 페이드 · 나=0.8 페이드 · 다=0.5 페이드+98→100%
O="${0:A:h}"; cd "$O/../work"; H=../../검수/heavy_run.sh
go(){ env FADE=$2 GROW=$3 SEG=$4 OUT="$O/$1.mp4" $H render python3 "$O/render_seg.py" >> "$O/seg.log" 2>&1 }
go 시안가_오프닝 0.5 0 0,20 & go 시안나_오프닝 0.8 0 0,20 & go 시안다_오프닝 0.5 1 0,20 &
go 시안가_클로징 0.5 0 858,884 & go 시안나_클로징 0.8 0 858,884 & go 시안다_클로징 0.5 1 858,884 &
wait; echo SEGDONE >> "$O/seg.log"
