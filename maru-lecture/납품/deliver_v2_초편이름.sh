#!/bin/zsh
# 납품 — 마루시공 11~20강 (2026-11-02 · 마루-자막싱크 p6)
# 사용: _작업/납품/deliver.sh <강번호> <mp4 경로>
#   1) 🆕11/3 이름 = `마루시공_NN강_초편.mp4` → `02. 최종파일/` 에 복사(강마다 하나)
#      같은 이름이 있으면 앞 판을 `_작업/납품/이전판_NN강/` 으로 옮김(지우지 않음 · 민석 11/3 「최종본만 남기기」)
#   2) 복사본 검사: 1920x1080 · 30000/1001 · AAC 48000Hz · 길이 = 원본 · sha256 원본 = 복사본
#   3) 통과하면 이름표.md 표의 그 강 줄에 「넘김 시각 · sha256」 기록(여러 번이면 <br> 로 이어 붙임)
#   검사에 걸리면 복사본을 `_작업/납품/_실패/` 로 옮기고 이름표는 건드리지 않는다(종료 코드 1).
# 시험용 덮어쓰기: DEST=<폴더> SHEET=<이름표 사본> TODAY=MMDD 환경변수.
set -u
here="${0:A:h}"; prj="${here:h:h}"
DEST="${DEST:-$prj/02. 최종파일}"; SHEET="${SHEET:-$here/이름표.md}"; TODAY="${TODAY:-$(date +%m%d)}"
(( $# == 2 )) || { echo "사용: deliver.sh <강번호> <mp4>"; exit 2; }
nn=$(printf "%02d" "$1"); src="${2:A}"
[[ -f "$src" ]] || { echo "❌ 원본 없음: $src"; exit 2; }
[[ -d "$DEST" ]] || { echo "❌ 넘길 폴더 없음: $DEST"; exit 2; }

# 🆕11/3 민석: 최종본 이름 = 마루시공_NN강_초편.mp4 (제목·자막본·날짜 없음). 02. 최종파일 엔 강마다 하나만.
#   같은 이름이 있으면 그 판을 _작업/납품/이전판_NN강/ 으로 옮긴 뒤(지우지 않음, 이름 뒤 _옮김HHMMSS) 새 판을 넣는다.
name="마루시공_${nn}강_초편.mp4"
dst="$DEST/$name"
if [[ -e "$dst" ]]; then
  arch="${ARCH:-$here}/이전판_${nn}강"; mkdir -p "$arch"
  keep="$arch/마루시공_${nn}강_초편_옮김$(date +%m%d_%H%M%S).mp4"; j=2
  while [[ -e "$keep" ]]; do keep="${keep%.mp4}_$j.mp4"; (( j++ )); done
  mv -n "$dst" "$keep" && [[ ! -e "$dst" ]] || { echo "❌ 앞 판 옮기기 실패"; exit 1; }
  echo "앞 판 → ${keep#$prj/}"
fi

cp -n "$src" "$dst" || { echo "❌ 복사 실패"; exit 1; }
[[ -f "$dst" ]] || { echo "❌ 복사본 없음"; exit 1; }

probe() { ffprobe -v error -select_streams "$2" -show_entries "$3" -of default=nw=1:nk=1 "$1" | head -1; }
dur() { ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$1"; }
fail=()
[[ "$(probe "$dst" v:0 stream=width)x$(probe "$dst" v:0 stream=height)" == "1920x1080" ]] || fail+=("해상도 $(probe "$dst" v:0 stream=width)x$(probe "$dst" v:0 stream=height)")
[[ "$(probe "$dst" v:0 stream=r_frame_rate)" == "30000/1001" ]] || fail+=("fps $(probe "$dst" v:0 stream=r_frame_rate)")
[[ "$(probe "$dst" a:0 stream=codec_name)" == "aac" ]] || fail+=("오디오 $(probe "$dst" a:0 stream=codec_name)")
[[ "$(probe "$dst" a:0 stream=sample_rate)" == "48000" ]] || fail+=("샘플레이트 $(probe "$dst" a:0 stream=sample_rate)")
ds=$(dur "$src"); dd=$(dur "$dst")
[[ -n "$dd" && "$ds" == "$dd" ]] || fail+=("길이 원본 $ds ≠ 복사본 $dd")
hs=$(shasum -a 256 "$src" | cut -d' ' -f1); hd=$(shasum -a 256 "$dst" | cut -d' ' -f1)
[[ "$hs" == "$hd" ]] || fail+=("sha256 다름")

if (( ${#fail} )); then
  mkdir -p "$here/_실패"; mv -n "$dst" "$here/_실패/"
  echo "❌ ${nn}강 검사 걸림 → 복사본 _작업/납품/_실패/$name"; printf ' - %s\n' "${fail[@]}"; exit 1
fi

when=$(date "+%Y-%m-%d %H:%M:%S")
python3 - "$SHEET" "${1#0}" "$name" "$when" "$hd" <<'PY'
import sys, re
p, n, name, when, sha = sys.argv[1:6]
L = open(p, encoding="utf-8").read().split("\n")
for i, l in enumerate(L):
    if l.startswith("| 강 | 파일 이름 |"):
        if "넘김 시각" not in l:
            L[i] = l + " 넘김 시각 | sha256 |"; L[i + 1] = L[i + 1] + "---|---|"
            j = i + 2
            while j < len(L) and L[j].startswith("|"): L[j] = L[j] + "  |  |"; j += 1
        break
for i, l in enumerate(L):
    if re.match(rf"^\| *{n} *\|", l):
        c = l.split("|"); rec_t, rec_s = f"`{name}` {when}", f"`{sha}`"
        c[-3] = (c[-3].strip() + "<br>" if c[-3].strip() else "") + rec_t
        c[-2] = (c[-2].strip() + "<br>" if c[-2].strip() else "") + rec_s
        L[i] = "|".join(x if k in (0, len(c) - 1) else f" {x.strip()} " for k, x in enumerate(c)); break
open(p, "w", encoding="utf-8").write("\n".join(L))
PY
echo "✅ ${nn}강 넘김: $dst"; echo "   길이 $dd · sha256 $hd · $when"
