#!/bin/zsh
# 19강 v5b 렌더 + 검사(오더37) — 실행 위치 _작업
cd "${0:A:h:h:h}"; O=19강/검사_v5b; mkdir -p $O; V=19강/19강_v5b.mp4; T=19강/타임라인_v5b.json; H=검수/heavy_run.sh
(cd 19강/work && ../../$H render python3 render_v5b.py > render_v5b.log 2>&1); echo "render $(tail -1 19강/work/render_v5b.log)"
ffprobe -v error -show_entries format=duration -of csv=p=0 $V
python3 검수/검사기/edge_check.py 19 --video $V --timeline $T > $O/edge_check.txt 2>&1; echo "edge $? $(tail -1 $O/edge_check.txt|cut -c1-60)"
python3 검수/검사기/announcer_audio_check.py $T --mp4 $V > $O/announcer.txt 2>&1; echo "announcer $? $(tail -1 $O/announcer.txt)"
python3 검수/검사기/line_break_check.py 19 --timeline $T > $O/line_break.txt 2>&1; echo "line_break $(head -1 $O/line_break.txt)"
python3 검수/검사기/newline_onset_check.py 19 --timeline $T --prev 19강/타임라인_v4b.json --json $O/newline_onset.json > $O/newline_onset.txt 2>&1; echo "onset $(head -1 $O/newline_onset.txt)"
~/.venvs/tts/bin/python 검수/검사기/anchor_sync_check.py 19 --timeline $T > $O/anchor_sync.txt 2>&1; echo "anchor $? $(tail -3 $O/anchor_sync.txt | tr '\n' ' ')"
AX=$(python3 -c "import json;t=json.load(open('$T'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
$H asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video $V --timeline $T --voice 19강/work/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1
python3 -c "
import json;d=json.load(open('$O/scene_sub.json'));s=d['summary'];print({k:s[k] for k in ['verdict','cuts_found','cuts_expected','boundary_stale','boundary_early','blank_bar_frames','sync_too_early','sync_late','sync_hold','sync_unknown']})
print([(x['n'],x['sub_t'],x['voice_t'],x['lead'],x['result']) for x in d['sync'] if x['n'] in (97,98,99)])"
shasum -a 256 $V
echo AFTERDONE
