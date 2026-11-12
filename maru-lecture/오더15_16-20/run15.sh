#!/bin/zsh
# 오더15 — 16~20강 타임라인_v2 까지(렌더 X). 한 강씩 · warp(ffmpeg 인코딩) = heavy_run render · 받아쓰기 = heavy_run asr
cd "${0:A:h}/.."          # _작업
H=검수/heavy_run.sh; PY=~/.venvs/tts/bin/python; C=오더09_공용
LS=(${@}); (( ${#LS} )) || LS=(16 17 18 19 20)
for n in $LS; do
  echo "=== $n $(date +%T)"; D=${n}강/아나운서; W=${n}강/work; G=$W/greet_a$((n-1))_090.wav; B=$W/bye_tc_090.wav
  (cd ${n}강 && python3 ../오더15_16-20/prep_sound15.py $n 타임라인_초안.json) | tail -1
  python3 오더15_16-20/loud.py $n
  for k in 인삿말 끝인사; do
    [ $k = 인삿말 ] && T=$G || T=$B
    [ -f $D/${n}_${k}_warp2.json ] || $H render python3 $C/warp_clip2.py $D/${n}_${k}_090.mp4 $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.mp4 $D/${n}_${k}_warp2.json | tail -1
  done
  $H asr $PY $C/words.py $G $B 2>&1 | grep -v Fetching
  for k in 인삿말 끝인사; do
    [ $k = 인삿말 ] && T=$G || T=$B
    $H asr $PY $C/lipcheck2.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.json 2>&1 | grep -v Fetching | cut -c1-200
    python3 $C/onsetcheck.py $D/${n}_${k}_090.wav $T $D/${n}_${k}_warp2.json | cut -c1-200
  done
  python3 오더15_16-20/fix15_tl.py $n | head -3
  (cd 오더15_16-20 && python3 check_text15.py $n | tail -1)
  python3 $C/tl_struct_check.py $n
  python3 $C/check_onsets09.py $n | tail -1
  python3 검수/검사기/announcer_audio_check.py ${n}강/타임라인_v2.json | tail -4; echo "aac exit $?"
done
echo "RUN15 DONE $(date +%T)"
