# 오더41: poc.html #encode 맨 위 그림 카드 #encode-pic 삽입 (막대 = 초당데이터_235초.json 실측)
import json
d = json.load(open("encode_설명/초당데이터_235초.json"))
S0, N = 16, 20                      # 16~35초: 11강 슬라이드 넘어감 3번 포함
a, b = d["00"][S0:S0+N], d["11"][S0:S0+N]
YM = 16.0
def bars(v, us):
    W, H = 1000, 150; cw = W / N; out = []
    for i, x in enumerate(v):
        h = max(min(x, YM) / YM * (H - 30), 2)
        col = "#0071e3" if us else "#86868b"
        out.append(f'<rect x="{i*cw+4:.1f}" y="{H-h:.1f}" width="{cw-8:.1f}" height="{h:.1f}" rx="3" fill="{col}"/>')
        if us and x > 1:
            out.append(f'<text x="{max(i*cw+cw/2,40):.1f}" y="{H-h-26:.1f}" text-anchor="middle" font-size="16" fill="#0071e3" font-weight="600"><tspan x="{max(i*cw+cw/2,40):.1f}">슬라이드</tspan><tspan x="{max(i*cw+cw/2,40):.1f}" dy="18">넘어감</tspan></text>')
    grid = "".join(f'<rect x="{i*cw+2:.1f}" y="0" width="{cw-4:.1f}" height="{H}" rx="4" fill="#f5f5f7"/>' for i in range(N))
    return f'<svg viewBox="0 0 1000 150" style="width:100%;height:auto;display:block" role="img">{grid}{"".join(out)}</svg>'
ticks = '<div class="ep-tk">' + "".join(f"<span>{i+1}</span>" for i in range(N)) + "</div>"
bub = "".join(f'<circle cx="{x}" cy="{y}" r="9" fill="#fff" stroke="#c7c7cc" stroke-width="1.5"/>' for x in range(30, 262, 22) for y in range(40, 232, 22)
              if not (85 <= x <= 205 and 105 <= y <= 175))
slide = lambda x, y: (f'<rect x="{x}" y="{y}" width="110" height="62" rx="5" fill="#fff" stroke="#1d1d1f" stroke-width="2"/>'
                      f'<rect x="{x+12}" y="{y+12}" width="60" height="7" rx="2" fill="#c7c7cc"/><rect x="{x+12}" y="{y+26}" width="44" height="7" rx="2" fill="#c7c7cc"/>'
                      f'<rect x="{x+8}" y="{y+46}" width="94" height="9" rx="2" fill="#1d1d1f"/>')
boxes = f'''<div class="ep-two">
<div class="ep-bx"><svg viewBox="0 0 290 250" role="img" aria-label="큰 상자"><rect x="12" y="22" width="266" height="220" rx="8" fill="#ededf0" stroke="#86868b" stroke-width="3"/>{bub}{slide(90,108)}</svg>
<b>00강 상자</b><p>1초마다 큰 상자 · 빈자리는 뽁뽁이로 채움</p><p class="ep-num">1초 ≈ 1.3MB</p><p class="ep-t">10.2Mbps ÷ 8 = 1.28MB</p></div>
<div class="ep-bx us"><svg viewBox="0 0 290 250" role="img" aria-label="딱 맞는 상자"><rect x="80" y="98" width="130" height="82" rx="8" fill="#eef4ff" stroke="#0071e3" stroke-width="3"/>{slide(90,108)}</svg>
<b>우리 상자</b><p>같은 물건, 딱 맞는 상자</p><p class="ep-num">1초 ≈ 0.04MB</p><p class="ep-t">0.35Mbps ÷ 8 = 0.044MB</p></div></div>'''
pr = '''<div class="ep-pr"><div class="ep-prh">내보내기 설정</div>
<div class="ep-prr"><span>형식</span><i>H.264 ▾</i></div><div class="ep-prr"><span>사전 설정</span><i>사용자 정의 ▾</i></div>
<div class="ep-prtab"><u>효과</u><u class="on">비디오</u><u>오디오</u><u>멀티플렉서</u></div>
<div class="ep-prr"><span>프레임 크기</span><i>1920 × 1080</i></div><div class="ep-prr"><span>프레임 속도</span><i>29.97 ▾</i></div>
<div class="ep-prs">▾ 비트 전송률 설정</div>
<div class="ep-hl"><div class="ep-prr"><span>비트 전송률 인코딩</span><i>CBR ▾</i></div>
<div class="ep-prr"><span>대상 비트 전송률 [Mbps]</span><i class="ep-sl"><em style="width:10%"></em></i><i>10</i></div></div>
<div class="ep-say">여기서 「1초에 10만큼 쓰라」고 정함</div></div>'''
us = '''<div class="ep-us"><div class="ep-ush">우리 방식</div>
<div class="ep-usr"><span>포장 방식</span><i>H.264</i></div><div class="ep-usr"><span>화면 크기</span><i>1920 × 1080</i></div><div class="ep-usr"><span>1초 장수</span><i>29.97</i></div>
<div class="ep-hl us"><div class="ep-usr"><span>정하는 것</span><i>화질 기준 · 18 <small>CRF 18</small></i></div>
<div class="ep-usr"><span>1초에 쓰는 양</span><i>알아서 (장면 따라)</i></div></div>
<div class="ep-say us">여기서 화질만 정하고, 양은 알아서</div></div>'''
reply = "화질은 00강과 똑같이 맞췄습니다. 00강은 1초마다 저장하는 양을 크게 고정해 두는 방식이라 화면 변화가 적어도 용량이 크게 나옵니다. 저는 화질을 기준으로 필요한 만큼만 저장하는 방식으로 뽑아서 용량이 작게 나왔습니다. 00강처럼 용량을 맞춰야 하면 같은 방식으로 다시 뽑아드리겠습니다."
css = '''<style>
#encode-pic{scroll-margin-top:64px}#encode-pic .card{margin-bottom:14px}#encode-pic h3{font-size:19px;margin:0 0 4px}#encode-pic .ep-n{color:var(--blue);margin-right:6px}
#encode-pic .ep-one{font-size:15px;margin:0 0 12px;color:var(--ink)}#encode-pic .ep-t{font-size:12px;color:var(--sub);margin:2px 0 0}
#encode-pic .ep-two{display:grid;grid-template-columns:1fr 1fr;gap:14px}#encode-pic .ep-cap{font-size:12px;color:var(--sub);margin:0 0 8px}
#encode-pic .ep-pr{background:#232323;color:#d6d6d6;border-radius:6px;padding:12px;font:12px/1.4 -apple-system,"Apple SD Gothic Neo",sans-serif;border:1px solid #111}
#encode-pic .ep-prh{font-weight:600;color:#eee;padding-bottom:8px;border-bottom:1px solid #3a3a3a;margin-bottom:8px}
#encode-pic .ep-prr,#encode-pic .ep-usr{display:flex;align-items:center;gap:8px;padding:5px 4px}#encode-pic .ep-prr span,#encode-pic .ep-usr span{flex:1;min-width:0}
#encode-pic .ep-prr i{font-style:normal;color:#5fa8ff;white-space:nowrap}#encode-pic .ep-prtab{display:flex;gap:2px;margin:8px 0;border-bottom:1px solid #3a3a3a;flex-wrap:wrap}
#encode-pic .ep-prtab u{text-decoration:none;padding:4px 8px;color:#999}#encode-pic .ep-prtab u.on{color:#fff;border-bottom:2px solid #5fa8ff}
#encode-pic .ep-prs{margin:8px 0 4px;color:#eee;font-weight:600}#encode-pic .ep-sl{flex:0 0 70px;height:4px;background:#444;border-radius:2px;position:relative}
#encode-pic .ep-sl em{position:absolute;left:0;top:0;bottom:0;background:#5fa8ff;border-radius:2px}
#encode-pic .ep-hl{border:2.5px solid #2f8bff;border-radius:6px;box-shadow:0 0 0 4px rgba(47,139,255,.25)}#encode-pic .ep-hl.us{border-color:var(--blue);box-shadow:0 0 0 4px rgba(0,113,227,.15)}
#encode-pic .ep-say{margin-top:10px;background:#2f8bff;color:#fff;font-weight:600;font-size:14px;border-radius:6px;padding:7px 10px}#encode-pic .ep-say.us{background:var(--blue)}
#encode-pic .ep-us{border:1px solid var(--line);border-radius:6px;padding:12px;font-size:13px;background:#fff}#encode-pic .ep-ush{font-weight:600;padding-bottom:8px;border-bottom:1px solid var(--line);margin-bottom:8px}
#encode-pic .ep-usr i{font-style:normal;font-weight:600;color:var(--ink);text-align:right}#encode-pic .ep-usr small{display:block;font-weight:400;font-size:11px;color:var(--sub)}
#encode-pic .ep-bx{text-align:center}#encode-pic .ep-bx svg{width:100%;max-width:290px;height:auto}#encode-pic .ep-bx b{display:block;font-size:15px}#encode-pic .ep-bx p{margin:2px 0;font-size:13px;color:var(--sub)}
#encode-pic .ep-bx .ep-num{font-size:22px;font-weight:700;color:var(--ink)}#encode-pic .ep-bx.us .ep-num{color:var(--blue)}#encode-pic .ep-bx .ep-t{font-size:12px}
#encode-pic .ep-row{font-size:14px;font-weight:600;margin:10px 0 4px}#encode-pic .ep-row small{font-weight:400;color:var(--sub);font-size:12px;margin-left:6px}
#encode-pic .ep-tk{display:grid;grid-template-columns:repeat(20,1fr);font-size:10px;color:var(--sub);text-align:center}
#encode-pic .ep-zoom img{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--line)}#encode-pic .ep-zoom b{display:block;font-size:14px;margin:10px 0 4px}
@media(max-width:720px){#encode-pic .ep-two{grid-template-columns:1fr}#encode-pic .ep-tk span:nth-child(even){visibility:hidden}}
</style>'''
block = f'''<section id="encode-pic">{css}
<div class="card"><h3>한눈에 보기 <span class="pill">오더41 · 11/5 · 그림으로</span></h3><p class="ep-one">화질은 같다. 「1초에 얼마나 담느냐」를 정하는 칸만 다르다.</p></div>
<div class="card"><h3><span class="ep-n">1</span>내보내기 화면에서 정하는 칸이 다르다</h3><p class="ep-cap">프리미어 화면을 다시 그린 것 (실제 화면 아님)</p>
<div class="ep-two"><div><div class="ep-row">00강 · 프리미어 <small>비트 전송률 인코딩 CBR · 10Mbps</small></div>{pr}</div><div><div class="ep-row">11~20강 · 우리 <small>FFmpeg x264 · CRF 18</small></div>{us}</div></div></div>
<div class="card"><h3><span class="ep-n">2</span>같은 물건, 상자 크기만 다르다</h3><p class="ep-one">강의 화면 1초를 상자에 넣으면</p>{boxes}</div>
<div class="card"><h3><span class="ep-n">3</span>1초 칸마다 담은 양 (20초)</h3><p class="ep-one">00강은 모든 칸이 늘 높다. 우리는 슬라이드가 넘어가는 칸만 높다.</p>
<div class="ep-row">00강 <small>1초 평균 약 10Mbps</small></div>{bars(a, False)}{ticks}
<div class="ep-row" style="margin-top:16px">우리 11강 <small>대부분 0.02~0.1Mbps · 넘어가는 칸 약 2Mbps</small></div>{bars(b, True)}{ticks}
<p class="ep-t">칸 하나 = 1초 · 높이 = 그 1초에 담은 양 · 실측 (00강 0:16~0:35, 11강 0:16~0:35) · 칸 아래 숫자 = 초</p></div>
<div class="card ep-zoom"><h3><span class="ep-n">4</span>확대해도 똑같다</h3><p class="ep-one">자막 글씨를 3배로 키워 봄</p>
<div class="ep-two"><div><b>00강 (294.8MB)</b><img src="encode_설명/00강_자막_확대.png" alt="00강 자막 확대"></div><div><b>우리 11강 (71.0MB)</b><img src="encode_설명/11강_자막_확대.png" alt="11강 자막 확대"></div></div>
<p class="ep-t">둘 다 1920×1080 · 29.97fps · 00강 3분 56초 294.8MB · 11~20강 약 15분 64~71MB</p></div>
<div class="card"><h3><span class="ep-n">5</span>팀장님께 보낼 답장</h3><div class="reply" id="enc_pic_reply">{reply}</div><button class="cbtn" data-t="enc_pic_reply" type="button">복사</button></div>
</section>
'''
p = open("poc.html", encoding="utf-8").read()
assert 'id="encode-pic"' not in p
anchor = '<h2 id="encode">'
i = p.index(anchor); j = p.index("\n", i) + 1
p = p[:j] + block + p[j:]
open("poc.html", "w", encoding="utf-8").write(p)
print("ok", [round(x,2) for x in a], [round(x,2) for x in b])
