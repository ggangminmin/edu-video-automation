#!/bin/zsh
# 무거운 작업 줄 세우기 (11/2 민석: 렌더 2개 동시 · 받아쓰기 1개)
# 사용: heavy_run.sh render <명령...>   — 렌더(ffmpeg) 칸 2개
#       heavy_run.sh asr <명령...>      — 받아쓰기(whisper·mlx) 칸 1개
# 램 여유 20% 밑이면 새 작업은 시작하지 않고 기다린다.
# 🆕11/2 23:3x 야간-팀장: 먼저 온 순서(번호표). 🆕11/3 00:1x 맨 앞 1명만 시도(1·2번이 같이 시도하면 1번이 계속 짐 — 16강 20분 굶음). 옛판 heavy_run_v1_공정성없음.sh 는 늦게 온 작업이 계속 앞질러 12·13강 v3 가 17분 굶음.
# 가벼운 검사(프레임 몇 장·소리 비교: edge_check · announcer_audio_check · check16_frames)는 이 칸에 넣지 않는다.
D="${0:A:h:h}"; kind=$1; shift
if [[ $kind == render ]]; then slots=(.render.lock1 .render.lock2); else slots=(.asr.lock); fi
Q="$D/.heavy_q/$kind"; mkdir -p "$Q"
me="$Q/$(date +%s%N 2>/dev/null || date +%s)000_$$"; : > "$me"
trap 'rm -f "$me"' EXIT INT TERM
while true; do
  for t in $Q/*(N); do kill -0 ${t##*_} 2>/dev/null || rm -f "$t"; done   # 죽은 번호표 정리
  tix=($Q/*(N:t)); tix=(${(o)tix}); pos=${tix[(i)${me:t}]}
  free=$(memory_pressure | awk -F': ' '/free percentage/{gsub("%","",$2);print $2}')
  if (( free >= 20 && pos == 1 )); then
    for s in $slots; do
      lockf -s -t 0 "$D/$s" zsh -c 'rm -f "$0"; exec "$@"' "$me" "$@" && exit 0
      rc=$?; (( rc != 75 )) && exit $rc
    done
  fi
  sleep 5
done
