#!/bin/zsh
# 무거운 작업 줄 세우기 (11/2 민석: 렌더 2개 동시 · 받아쓰기 1개)
# 사용: heavy_run.sh render <명령...>   — 렌더(ffmpeg) 칸 2개
#       heavy_run.sh asr <명령...>      — 받아쓰기(whisper·mlx) 칸 1개
# 램 여유 20% 밑이면 새 작업은 시작하지 않고 기다린다.
D="${0:A:h:h}"; kind=$1; shift
if [[ $kind == render ]]; then slots=(.render.lock1 .render.lock2); else slots=(.asr.lock); fi
while true; do
  free=$(memory_pressure | awk -F': ' '/free percentage/{gsub("%","",$2);print $2}')
  if (( free >= 20 )); then
    for s in $slots; do
      lockf -s -t 0 "$D/$s" "$@" && exit 0
      rc=$?; (( rc != 75 )) && exit $rc   # 75 = 칸이 차 있음 → 다음 칸
    done
  fi
  sleep 15
done
