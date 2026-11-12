#!/bin/zsh
cd "${0:A:h}/.."; D=20강/아나운서; T=20강/work/greet_a19_090.wav
AN=$(head -1 $D/20_인삿말_anchor4.txt)
검수/heavy_run.sh render python3 오더09_공용/warp_clip2.py $D/20_인삿말_090.mp4 $D/20_인삿말_090.wav $T $D/20_인삿말_warp4.mp4 $D/20_인삿말_warp4.json "$AN" > /dev/null
python3 오더09_공용/onsetcheck.py $D/20_인삿말_090.wav $T $D/20_인삿말_warp4.json | cut -c1-260
python3 오더15_16-20/pausecheck.py $D/20_인삿말_090.wav $T $D/20_인삿말_warp4.json $D/20_인삿말_anchor4.txt
python3 -c "import json;print('env',json.load(open('$D/20_인삿말_warp4.json')).get('env_corr'))"
echo REWARP4 DONE
