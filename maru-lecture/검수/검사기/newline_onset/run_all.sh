#!/bin/zsh
# 11/3 팀장: 납품본 줄 나눔 새 줄 시작 표(고치지 않음) — 실행 위치 _작업
cd "${0:A:h:h:h:h}"; O=검수/검사기/newline_onset; P=~/.venvs/tts/bin/python
for x in "11 11강/타임라인_v7.json 11강/타임라인_v6.json" "12 12강/타임라인_v5.json 12강/타임라인_v3d.json" "13 13강/타임라인_v6.json 13강/타임라인_v5.json" \
         "15 15강/타임라인_v6.json 15강/타임라인_v3c.json" "16 16강/타임라인_v5b.json 16강/타임라인_v3b.json" "17 17강/타임라인_v4c.json 17강/타임라인_v3c.json"; do
  set -- ${=x}; $P 검수/검사기/newline_onset_check.py $1 --timeline $2 --prev $3 --asr --json $O/$1강.json > $O/$1강.txt 2>&1; echo "$1 rc=$? $(grep -m1 바뀐 $O/$1강.txt)"
done
