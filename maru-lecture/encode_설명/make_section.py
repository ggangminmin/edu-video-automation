# 오더39: poc.html #encode 구간 생성 (그래프 = 초당데이터_235초.json 실측)
import json, html, re
d = json.load(open("encode_설명/초당데이터_235초.json"))
W, H, PAD, YMAX = 1000, 260, 34, 20.0
def pts(v):
    n = len(v); return " ".join(f"{PAD + i*(W-PAD-10)/(n-1):.1f},{H-24 - min(x,YMAX)/YMAX*(H-50):.1f}" for i, x in enumerate(v))
grid = "".join(f'<line x1="{PAD}" x2="{W-10}" y1="{H-24-g/YMAX*(H-50):.1f}" y2="{H-24-g/YMAX*(H-50):.1f}" stroke="#e5e5ea"/><text x="{PAD-6}" y="{H-20-g/YMAX*(H-50):.1f}" text-anchor="end" font-size="12" fill="#6e6e73">{g}</text>' for g in (0,5,10,15,20))
xt = "".join(f'<text x="{PAD + s*(W-PAD-10)/234:.1f}" y="{H-6}" text-anchor="middle" font-size="12" fill="#6e6e73">{s//60}분{"" if s%60==0 else f" {s%60}초"}</text>' for s in (0,60,120,180,234))
graph = f'''<svg viewBox="0 0 {W} {H}" role="img" aria-label="1초마다 쓰는 데이터 양 비교" style="width:100%;height:auto;display:block">{grid}{xt}
<polyline fill="none" stroke="#86868b" stroke-width="2" points="{pts(d['00'])}"/>
<polyline fill="none" stroke="#0071e3" stroke-width="2.5" points="{pts(d['11'])}"/></svg>'''
def strip(same):
    cells = []
    for i in range(10):
        if same and i > 0:
            cells.append('<div class="fr same"><span>그대로</span></div>')
        else:
            body = '<div class="sl"><i></i><i></i><i class="s"></i><b></b></div>' if same else f'<div class="mv" style="--x:{8+i*8}%"></div>'
            cells.append(f'<div class="fr">{body}</div>')
    return '<div class="strip">' + "".join(cells) + '<div class="more">… 30장</div></div>'
easy = "화질 기준으로 압축해서 용량이 작게 나온 것이고, 화질은 00강과 같습니다. 용량(비트레이트)을 맞춰야 하면 말씀 주세요. 다시 뽑아 드리겠습니다."
tech = ("11~20강은 FFmpeg(x264)로 H.264 High · 1920×1080 · 29.97fps · CRF 18(화질 고정 방식, preset medium) · 오디오 AAC 320kbps 48kHz 스테레오로 인코딩했습니다. "
        "00강은 프리미어(미디어 인코더)에서 약 10Mbps 고정 비트레이트로 출력되어 용량 차이가 납니다. 슬라이드 위주 영상이라 CRF 방식에서는 평균 약 0.35Mbps로도 화질 차이 없이 담깁니다. "
        "같은 비트레이트 방식으로 맞춰야 하면 다시 출력해 드리겠습니다.")
terms = [("인코딩","영상을 파일로 「포장」하는 일. 어떤 상자에, 얼마나 꽉 담을지 정한다."),("압축","똑같은 그림은 「앞과 같음」이라고만 적어 자리를 아끼는 것."),
 ("H.264","포장 방식 이름. 지금 거의 모든 영상이 쓰는 표준 상자. 00강·11~20강 둘 다 이것."),("1080p (1920×1080)","화면 크기. 가로 1920점 × 세로 1080점. 둘 다 같음."),
 ("29.97fps","1초에 사진 약 30장. 둘 다 같음."),("비트레이트","1초에 쓰는 데이터 양. 위 그래프의 높이."),("Mbps","비트레이트 단위. 10Mbps = 1초에 약 1.25MB."),
 ("CRF 18","「용량」 대신 「화질」을 정해 두는 방식. 18 = 눈으로 원본과 구분 안 되는 수준. 복잡한 장면엔 많이, 멈춘 장면엔 조금 쓴다."),
 ("고정 비트레이트","장면과 상관없이 1초마다 같은 양을 쓰는 방식(00강). 멈춘 슬라이드에도 꽉 채운다."),
 ("AAC 48kHz 스테레오","소리 포장 방식. 둘 다 같음(우리는 320kbps 설정)."),("FFmpeg · x264","우리가 쓴 포장 프로그램. 유튜브·넷플릭스도 쓰는 무료 표준 도구."),
 ("프리미어 (미디어 인코더)","팀장님이 쓴 어도비 포장 프로그램. 00강은 이것(MainConcept H.264).")]
sizes = [("00강 (팀장님)","3분 56초","294.8MB","프리미어 · 약 10.2Mbps 고정"),("01강 (팀장님)","확인 못 함","858.5MB","로컬 파일 없음 · 00강과 같은 방식으로 보임"),
 ("11~20강 (우리)","13분 56초 ~ 15분 35초","61~68MB","FFmpeg x264 · CRF 18 · 평균 약 0.35Mbps")]
S = f'''<style>
#encodewrap .card{{margin-bottom:14px}}#encodewrap h3{{font-size:17px;margin:0 0 6px}}#encodewrap .big{{font-size:22px;font-weight:700;line-height:1.4;margin:0}}
#encodewrap .big em{{font-style:normal;color:var(--blue)}}#encodewrap .note{{font-size:13px;color:var(--sub);margin:6px 0 0}}
#encodewrap .strip{{display:flex;gap:4px;align-items:center;margin:8px 0;overflow:hidden}}#encodewrap .fr{{flex:1 1 0;min-width:0;aspect-ratio:16/9;border:1px solid var(--line);border-radius:4px;background:#fff;position:relative;overflow:hidden}}
#encodewrap .fr.same{{background:#eef4ff;border-style:dashed;border-color:#b9d4f7;display:flex;align-items:center;justify-content:center}}#encodewrap .fr.same span{{font-size:10px;color:var(--blue);white-space:nowrap}}
#encodewrap .sl{{position:absolute;inset:12% 10%}}#encodewrap .sl i{{display:block;height:9%;background:#d2d2d7;border-radius:2px;margin:0 0 9%;width:70%}}#encodewrap .sl i.s{{width:45%}}#encodewrap .sl b{{position:absolute;left:0;right:0;bottom:0;height:16%;background:#1d1d1f;border-radius:2px}}
#encodewrap .mv{{position:absolute;top:30%;left:var(--x);width:22%;height:40%;border-radius:50%;background:#86868b}}#encodewrap .more{{font-size:12px;color:var(--sub);white-space:nowrap}}
#encodewrap .rowl{{font-size:14px;font-weight:600;margin-top:10px}}
#encodewrap .cmp{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}#encodewrap .cmp img{{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--line)}}#encodewrap .cmp .lab{{font-size:13px;color:var(--sub);margin:8px 0 4px}}
#encodewrap .cmp .lab b{{color:var(--ink)}}#encodewrap table{{width:100%;border-collapse:collapse;font-size:14px}}#encodewrap td,#encodewrap th{{border-top:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}}
#encodewrap th{{font-size:13px;color:var(--sub);font-weight:600}}#encodewrap td:first-child{{font-weight:600;white-space:nowrap}}#encodewrap tr.us td{{background:#f5f9ff}}
#encodewrap .reply{{background:#f5f5f7;border-radius:10px;padding:12px 14px;font-size:14px;margin:8px 0}}#encodewrap .cbtn{{font:600 13px/1 -apple-system,"Apple SD Gothic Neo",sans-serif;padding:8px 14px;border-radius:99px;border:1px solid var(--blue);background:#fff;color:var(--blue);cursor:pointer}}
#encodewrap .cbtn.done{{background:var(--blue);color:#fff}}#encodewrap .opts{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}#encodewrap .opt{{border:1px solid var(--line);border-radius:12px;padding:14px}}#encodewrap .opt.rec{{border-color:var(--blue)}}
#encodewrap .opt h4{{margin:0 0 6px;font-size:15px}}#encodewrap .opt p{{margin:0;font-size:13px;color:var(--sub)}}#encodewrap .legend span{{display:inline-block;margin-right:14px;font-size:13px}}#encodewrap .legend i{{display:inline-block;width:18px;height:3px;vertical-align:middle;margin-right:6px}}
#encodewrap .box{{display:flex;gap:14px;align-items:flex-end;margin-top:10px;flex-wrap:wrap}}#encodewrap .bx{{text-align:center;font-size:12px;color:var(--sub)}}#encodewrap .bx div{{border:2px solid #86868b;border-radius:6px;margin:0 auto 4px;display:flex;align-items:center;justify-content:center;background:repeating-radial-gradient(circle at 6px 6px,#e5e5ea 0 3px,transparent 3px 12px)}}
#encodewrap .bx div i{{width:34px;height:24px;background:var(--blue);border-radius:3px}}#encodewrap .bx.us div{{border-color:var(--blue);background:#fff}}
@media(max-width:720px){{#encodewrap .fr.same span{{display:none}}#encodewrap .cmp,#encodewrap .opts{{grid-template-columns:1fr}}#encodewrap td:first-child{{white-space:normal}}#encodewrap table{{font-size:13px}}#encodewrap .big{{font-size:19px}}}}
</style>
<h2 id="encode">영상 용량이 왜 다를까 <span class="pill">오더39 · 11/4 · 고객 문의 「인코딩 뭐로 했나」</span></h2>
<section>
<div class="card"><p class="big">화질은 같고, <em>담는 방식만</em> 다르다.<br>민석이 잘못한 것 없음.</p>
<p class="note">00강 294.8MB · 01강 858.5MB(팀장님) vs 11~20강 61~68MB(우리). 화면 크기·초당 장수·포장 규격(H.264)·소리 규격은 전부 같다. 다른 건 「1초에 데이터를 얼마나 채우느냐」 하나뿐.</p></div>

<div class="card"><h3>그림 1 — 영상은 1초에 사진 30장</h3>
<div class="rowl">움직임이 많은 영상: 30장이 전부 다름 → 다 적어야 함</div>{strip(False)}
<div class="rowl">우리 강의(슬라이드): 30장이 거의 같음 → 첫 장만 적고 나머지는 「그대로」</div>{strip(True)}
<p class="note">이게 「압축」. 슬라이드가 몇 초씩 멈춰 있는 강의는 「그대로」가 대부분이라 아주 작게 담긴다. 그래도 화면에 보이는 그림은 똑같다.</p></div>

<div class="card"><h3>그림 2 — 1초마다 쓰는 데이터 양 (실측, 처음 3분 55초)</h3>
<div class="legend"><span><i style="background:#86868b"></i>팀장님 방식 00강 — 늘 꽉 채움 (평균 10.2)</span><span><i style="background:#0071e3"></i>우리 방식 11강 — 필요할 때만 씀 (평균 0.4)</span></div>
{graph}
<p class="note">세로 = 1초에 쓰는 데이터(Mbps). 파란 선은 낮게 깔리다가 슬라이드가 넘어가거나 아나운서가 움직일 때만 올라간다. 회색 선은 멈춘 화면에도 늘 높다.</p>
<div class="box"><div class="bx"><div style="width:150px;height:110px"><i></i></div>팀장님 방식 · 뽁뽁이로 꽉 채운 큰 상자</div><div class="bx us"><div style="width:48px;height:38px"><i></i></div>우리 방식 · 딱 맞는 상자</div></div>
<p class="note">안에 든 물건(화질)은 같다. 상자 크기(용량)만 다르다.</p></div>

<div class="card"><h3>그림 3 — 실제 화면 확대 비교</h3><p class="note" style="margin:0 0 10px">같은 위치를 픽셀 그대로 확대(자막 3배 · 얼굴 2배). 확대해도 글씨 가장자리·얼굴 차이가 보이지 않는다.</p>
<div class="cmp"><div><div class="lab"><b>00강 (294.8MB)</b> 0:40 자막 장면</div><img loading="lazy" src="encode_설명/00강_자막_작게.jpg" alt="00강 자막 장면"><div class="lab">자막 글씨 3배 확대</div><img loading="lazy" src="encode_설명/00강_자막_확대.png" alt="00강 자막 확대"></div>
<div><div class="lab"><b>11강 (67.6MB)</b> 2:00 자막 장면</div><img loading="lazy" src="encode_설명/11강_자막_작게.jpg" alt="11강 자막 장면"><div class="lab">자막 글씨 3배 확대</div><img loading="lazy" src="encode_설명/11강_자막_확대.png" alt="11강 자막 확대"></div>
<div><div class="lab"><b>00강</b> 0:05 아나운서</div><img loading="lazy" src="encode_설명/00강_아나운서_작게.jpg" alt="00강 아나운서"><div class="lab">얼굴 2배 확대</div><img loading="lazy" src="encode_설명/00강_아나운서_확대.png" alt="00강 얼굴 확대"></div>
<div><div class="lab"><b>11강</b> 0:05 아나운서</div><img loading="lazy" src="encode_설명/11강_아나운서_작게.jpg" alt="11강 아나운서"><div class="lab">얼굴 2배 확대</div><img loading="lazy" src="encode_설명/11강_아나운서_확대.png" alt="11강 얼굴 확대"></div></div>
<p class="note">원본 크기 PNG: <code>_작업/encode_설명/</code> (00강_자막.png · 11강_자막.png · 00강_아나운서.png · 11강_아나운서.png)</p></div>

<div class="card"><h3>파일 크기 표</h3><table><tr><th>영상</th><th>길이</th><th>용량(드라이브 표시)</th><th>방식</th></tr>
{"".join(f'<tr{" class=us" if "우리" in a else ""}><td>{a}</td><td>{b}</td><td>{c}</td><td>{e}</td></tr>' for a,b,c,e in sizes)}</table>
<p class="note">공통: 1920×1080 · 29.97fps · H.264 High · 소리 AAC 48kHz 스테레오. 11~20강 중 가장 작은 것 17강 61.3MB(13분 56초) · 가장 큰 것 11강 67.6MB(15분 29초).</p></div>

<div class="card"><h3>용어 사전</h3><table>{"".join(f'<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>' for a,b in terms)}</table></div>

<div class="card"><h3>고객 답장 — 골라서 복사</h3>
<div class="lab" style="font-size:14px;font-weight:600">쉬운 판</div><div class="reply" id="enc_easy">{html.escape(easy)}</div><button class="cbtn" data-t="enc_easy" type="button">복사</button>
<div class="lab" style="font-size:14px;font-weight:600;margin-top:14px">기술 판 (용어 포함)</div><div class="reply" id="enc_tech">{html.escape(tech)}</div><button class="cbtn" data-t="enc_tech" type="button">복사</button></div>

<div class="card"><h3>민석이 고를 것</h3><div class="opts">
<div class="opt rec"><h4>가. 이대로</h4><p>화질 같음 · 강의당 61~68MB · 올리기·내려받기 빠름. 고객이 용량만 물었다면 이걸로 충분.</p></div>
<div class="opt"><h4>나. 팀장님 방식으로 다시 뽑기</h4><p>내용·화질 그대로 · 약 10Mbps 고정 → 강의당 약 1.0~1.2GB(10편 약 11GB). 고객이 「00강과 같은 방식」을 원할 때만.</p></div></div></div>
</section>
<script>document.querySelectorAll('#encodewrap .cbtn').forEach(function(b){{b.addEventListener('click',function(){{var t=document.getElementById(b.dataset.t).innerText;(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).catch(function(){{var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove();}}).finally(function(){{b.textContent='복사됨';b.classList.add('done');setTimeout(function(){{b.textContent='복사';b.classList.remove('done');}},1500);}});}});}});</script>
'''
p = "poc.html"; s = open(p).read()
s = re.sub(r'<div id="encodewrap">.*?</div>\n(?=<div id="midotwrap">)', '', s, flags=re.S); assert 'id="encode"' not in s
a = '<div id="midotwrap">'; assert s.count(a) == 1
s = s.replace(a, '<div id="encodewrap">' + S + '</div>\n' + a)
n = '<nav style="margin-top:10px"><a href="#midotlist">'
s = s if '#encode"><b>' in s else s.replace(n, '<nav style="margin-top:10px"><a href="#encode"><b>용량·화질 설명</b></a><a href="#midotlist">')
open(p, "w").write(s); print("ok")
