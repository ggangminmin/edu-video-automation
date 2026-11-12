#!/bin/zsh
# 납품 — 마루시공 11~20강 (2026-11-02 · 마루-자막싱크 p6)
# 사용: _작업/납품/deliver.sh <강번호> <mp4 경로>
#   1) 이름 = 이름표.md 표의 그 강 파일 이름에서 끝 _MMDD 를 오늘 날짜로 → `02. 최종파일/` 에 복사
#      같은 이름이 있으면 덮어쓰지 않고 _v2, _v3 … (이미 넘긴 판은 지우거나 옮기지 않는다)
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

base=$(grep -E "^\| *${1#0} *\|" "$SHEET" | grep -o '`마루시공_[^`]*\.mp4`' | head -1 | tr -d '`')
[[ -n "$base" ]] || { echo "❌ 이름표에 ${nn}강 줄 없음"; exit 2; }
stem="${base%.mp4}"; stem="${stem%_[0-9][0-9][0-9][0-9]}_${TODAY}"
name="$stem.mp4"; k=2
while [[ -e "$DEST/$name" ]]; do name="${stem}_v$k.mp4"; (( k++ )); done
dst="$DEST/$name"

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
