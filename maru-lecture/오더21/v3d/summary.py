# 강별 v3d 검사 요약 → NN강/검사_v3d/검사요약.md (결과 파일만 읽음)   실행: python3 오더24/summary.py NN "추가 메모(오검출 근거 등)"
import sys, json, os, subprocess
N = sys.argv[1]; NOTE = sys.argv[2] if len(sys.argv) > 2 else ""; D = f"{N}강"; O = f"{D}/검사_v3d"
def tail(p): return open(p).read().strip().splitlines()[-1] if os.path.exists(p) else "(없음)"
tl = json.load(open(f"{D}/타임라인_v3d.json")); g = json.load(open(f"{O}/문장텀.json"))
ss = json.load(open(f"{O}/scene_sub.json"))["summary"]
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{D}/{D}_v3d.mp4"], capture_output=True, text=True).stdout.strip()
drop = tl.get("dropped", [])
md = f"""# {N}강 v3d 검사 요약 (오더21·24 · 야간-12~15) — 만든 쪽: Claude(전부)
대상 `{D}/{D}_v3d.mp4` {d}초(타임라인 `{D}/타임라인_v3d.json` {tl['total']}) · 앞판 `{D}/{D}_v2.mp4`

## 바뀐 것
- v2→v3(오더21): 규칙 7 문장 텀 = 11강 pR `align_v5.py` 방식(`오더21/fix21_tl.py`) — 메모 문장 끝(. ? !) 뒤 쉼 ≥1.505(쉼 가운데 무음 삽입, 긴 건 그대로) · 문장 안 쉼 그대로 · 넘김 말끝→1.71→컷+새 자막→0.09→말 · 확인문제 5.5 · 스스로 3.0. 예외(팀장): 표지→2장 넘김 = v2 그대로 · 끝인사 warp 클립 안 쉼 그대로.
- 규칙 2 개정 대조(`오더21/svv_{N}.json`, `_작업/음성에없는문장.md`): 뺀 줄 {len(drop)}개 {[(x['slide'], x['text']) for x in drop]} · 표현 다름 0.
- v3→v3b(오더24): concat 맨 끝 반복 file 뒤 `option framerate 30000/1001` 한 줄(끝 검정 0.9초 빠짐 고침). 그 밖 변경 없음.

| 검사 | 결과 | 파일 |
|---|---|---|
| edge_check(장 컷·새 자막·아나운서 ±2프레임 + 끝 검정·길이) | {tail(f'{O}/edge_check.txt')[:90]} | `검수/검사기/edge_{N}_{N}강_v3d.json` |
| end_check(끝 0.9초 밝기·길이·PTS) | {tail(f'{O}/end_check.txt')} | end_check.txt |
| 흑백 튐(전편 프레임) | {tail(f'{O}/흑백튐.txt')[:80]} | 흑백튐.json |
| 문장텀(깨끗한 음성 실측) | 문장 끝 {g['문장끝_쉼']['개수']}곳 최소 {g['문장끝_쉼']['최소']} 미달 {len(g['문장끝_쉼']['미달'])} · 문장 안 {g['문장안_쉼']['개수']}곳 v2와 다름 {len(g['문장안_쉼']['v2와_다름'])} · 넘김 합 {g['넘김_합']['최소']}~{g['넘김_합']['최대']} · 문제/스스로 {g['확인문제_스스로']} · BGM {g['BGM']['곡']} 음성 대비 {g['BGM']['차이']}dB | 문장텀.json |
| announcer_audio_check --mp4 | {tail(f'{O}/announcer.txt')} | announcer.txt |
| check_text | {tail(f'{O}/check_text.txt')} | check_text.txt |
| scene_sub_check | verdict {ss['verdict']} · 컷 {ss['cuts_found']}/{ss['cuts_expected']} · 옛 자막 남음 {ss['boundary_stale']} · 빈 바 {ss['blank_bar_frames']} · 늦음 {ss['sync_late']} · 너무빠름 {ss['sync_too_early']} · 정지 {ss['anchor_still']} · 판정불가 {len(ss['sync_unknown'])}줄 | scene_sub.json · 경계.jpg |
| 배치16 · 경계16 · 정지16 | {tail(f'{O}/배치16_프레임.txt')[:30]} · {tail(f'{O}/경계16.txt')} · {tail(f'{O}/정지16.txt')} | |
| 아나운서배치 cx 판정 | 12~15 고칠 것 없음 | `검수/아나운서배치_12-20.md` |

{NOTE}
"""
open(f"{O}/검사요약.md", "w").write(md); print(md)
