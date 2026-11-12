#!/bin/zsh
cd "${0:A:h}/.."; n=14; O=14강/검사_v2
AX=$(python3 -c "import json;t=json.load(open('14강/타임라인_v2.json'));print(','.join(f\"{a['name']}:{a['x']+(196 if a['name']=='인삿말' else 178)}\" for a in t['anchors']))")
echo "$(date +%T) 재검사(새 scene_sub · anc-x $AX)" >> $O/진행.log
검수/heavy_run.sh asr ~/.venvs/tts/bin/python 검수/검사기/scene_sub_check.py --anc-x "$AX" --video 14강/14강_v2.mp4 --timeline 14강/타임라인_v2.json --voice 14강/work/v090.wav --out $O/scene_sub.json --sheet $O/경계.jpg > $O/scene_sub.txt 2>&1
echo "$(date +%T) scene_sub exit=$? · 끝(재검사)" >> $O/진행.log
