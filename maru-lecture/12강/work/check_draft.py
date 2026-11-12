# 12강 타임라인 초안 자체 점검: 자막 선행 범위 · 장면=첫 자막 같은 프레임 · 빈 바 · 텀 · 문제 대기 · 글자수
import json, statistics
tl = json.load(open("../타임라인_초안.json")); subs = tl["subs"]; sl = {s["slide"]: s for s in tl["slides"]}
lead = [x["voice_on"] - x["start"] for x in subs]
print(f"자막 {len(subs)}줄 · 총 {tl['total']}초 · 선행 최소 {min(lead):.3f} 중앙 {statistics.median(lead):.3f} 최대 {max(lead):.3f}")
print("선행 범위 밖(<0 또는 >0.16):", [(x['n'], round(x['voice_on'] - x['start'], 3)) for x in subs if not (0 <= x['voice_on'] - x['start'] <= 0.16)])
print("장면 시작 ≠ 첫 자막:", [s for s in sl if min(x['start'] for x in subs if x['slide'] == s) != sl[s]['start']])
print("옛 자막이 새 장면에 넘어감:", [x['n'] for x in subs if x['end'] > sl[x['slide']]['end'] + 1e-6])
print("빈 바:", [(a['n'], b['n']) for a, b in zip(subs, subs[1:]) if abs(a['end'] - b['start']) > 1e-6])
print("말끝→컷 텀:", sorted(set(round(s.get('hold_after_voice', 0), 2) for s in sl.values())))
print("문제 대기:", {s: round(sl[s]['hold_after_voice'], 2) for s in sl if sl[s].get('quiz_wait')})
print("35자 넘는 줄:", [x['n'] for x in subs if len(x['text']) > 35], "· 1초 미만 줄:", [(x['n'], round(x['end'] - x['start'], 2)) for x in subs if x['end'] - x['start'] < 1.0])
