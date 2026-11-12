#!/usr/bin/env python3
"""line_break_check 회귀 검산 (오더25 연장) — line_break_regress_cases.json 의 사례마다 기대(bad) == 검사기 판단인지.
실행: python3 검수/검사기/line_break_regress.py   → 틀린 사례 목록 · 종료코드 = 틀린 수"""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from line_break_check import reason
C = json.load(open(os.path.join(D, "line_break_regress_cases.json")))
wrong = []
for c in C:
    bad, why = reason(c["prev"], c["next"], c.get("part"))
    if bad != c["bad"]: wrong.append((c, bad, why))
print(f"사례 {len(C)} · 맞음 {len(C) - len(wrong)} · 틀림 {len(wrong)}")
for c, bad, why in wrong:
    print(f"  ✗ {c['id']} 「…{c['prev'][-14:]}」/「{c['next'][:14]}…」 기대 {'위반' if c['bad'] else '통과'} · 검사기 {'위반' if bad else '통과'}({why})")
sys.exit(min(len(wrong), 255))
