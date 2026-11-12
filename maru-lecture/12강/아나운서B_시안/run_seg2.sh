#!/bin/zsh
O="${0:A:h}"; while pgrep -f run_seg.sh >/dev/null; do sleep 5; done; cd "$O/../work"; H=../../검수/heavy_run.sh
go(){ env FADE=$2 GROW=$3 SEG=$4 OUT="$O/$1.mp4" $H render python3 "$O/render_seg.py" >> "$O/seg2.log" 2>&1 }
go 시안가_오프닝 0.5 0 0,20 & go 시안나_오프닝 0.8 0 0,20 & go 시안다_오프닝 0.5 1 0,20 &
wait; echo SEGDONE >> "$O/seg2.log"
