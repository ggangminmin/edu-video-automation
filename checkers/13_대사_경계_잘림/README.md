# 13 대사 경계 잘림
- 무엇을 잡나: 소리 클립 시작·끝·페이드가 말(목소리) 중간을 자르는 것, 페이드가 말을 먹는 것, 대사끼리 겹치거나 붙은 것.
- 왜 생겼나: 2026-10-26 마키 티저 — v02 「대사 뚝뚝 끊긴다」 → v03 「다 중간에 잘린다」. 음량 덩어리(바닥+14dB)로 말 끝을 잡아 한국어 어미 꼬리를 잘랐고, 받아쓰기·제미나이 Flash 는 글자가 맞으니 통과시켰다.
- 언제: 대사·비명이 있는 영상의 오디오를 편집했으면 민석에게 올리기 전 매번.
- 준비: 원본마다 목소리 분리 `~/.local/share/meomuru-audio-env/bin/demucs --two-stems=vocals -n htdemucs -o <out> <원본.wav>`.
- 명령: `python3 minstack/검수기/13_대사_경계_잘림/check_dialogue_bounds.py events.json --out report.md` (종료코드 0 = 통과)
- events.json 칸: label · voice(그 클립 원본의 vocals.wav) · src_in · src_out · tl · fi · fo(프레임) · speech(대사면 [말시작, 말끝] 소스초).
- 본보기: `~/Movies/maki_trailer_v03/pr_src/check_v04.py`(설계표 → events.json → 이 검사기).
- 못 보는 것: 목소리 분리가 놓친 소리(효과음 속 기합), 말의 자연스러움·감정. 통과 후 귀로 한 번.
