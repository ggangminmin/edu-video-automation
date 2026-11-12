#!/bin/zsh
# 오더23: pS 「19·20 렌더는 12·13 이 칸 잡은 뒤」 → 13강 렌더가 칸을 잡거나(lockf cwd 13강) 끝나면 19·20 run_v3 걸기
cd "${0:A:h}/.."
while true; do
  for p in $(pgrep -f "lockf -s -t 0"); do lsof -p $p 2>/dev/null | awk '/cwd/{print $NF}' | grep -q "13강/work" && break 2; done
  [ -f 13강/13강_v3.mp4 ] && [ "$(tail -1 13강/work/render_v3.log 2>/dev/null)" = "ok" ] && break
  sleep 15
done
echo "$(date +%T) 13 칸 잡음 → 19·20 걸기" >> 오더23/run_v3.log
nohup 오더23/run_v3.sh 19 > /dev/null 2>&1 &
sleep 5; nohup 오더23/run_v3.sh 20 > /dev/null 2>&1 &
