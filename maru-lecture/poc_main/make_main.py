# 오더40: POC 메인 = 완성 영상 11→20강 · 기존 내용은 지우지 않고 화면 전환(상단 고정 네비)으로만
import re, urllib.parse as u
p = "poc.html"; s = open(p).read()
assert 'class="wrap mainview"' not in s
D = [("00","강의 사전 안내","3:55","10/30 14:15","팀장님 제작","d70081d8","마루시공_00강_강의사전안내_초편_자막본_1030.mp4"),
("11","패턴 심화와 이형 공간 시공","15:29","11/3 14:45","v8","b4e88e1b",None),("12","마감 기술과 디테일","14:53","11/3 15:59","v7","b5c79535",None),
("13","공간별 시공 적용","15:32","11/3 14:20","v7","aa938fb3",None),("14","마루 시공 견적과 고객 관리","15:29","11/4 09:08","v7b","f8060414",None),
("15","하자의 종류와 원인 분석","14:28","11/3 13:03","v6","dda9b998",None),("16","하자 보수 방법","15:10","11/3 13:39","v5b","3c5eb93b",None),
("17","하자 예방과 유지 관리","13:55","11/3 13:14","v4c","7e3dee83",None),("18","개인 보호와 위험 예방","15:35","11/3 14:34","v4c","474fd92c",None),
("19","화학물질과 환경 관리","14:48","11/3 17:11","v5b","88248c7c",None),("20","전문가 윤리와 직업 전망","15:21","11/3 14:44","v4c","23b15464",None)]
def card(n,t,dur,when,ver,h,f, ref=False):
    src = "../" + u.quote(f"02. 최종파일/{f or f'마루시공_{n}강.mp4'}")
    return (f'<article class="mv{" ref" if ref else ""}" id="m{n}"><div class="mvh"><span class="mvn">{n}강</span><b>{t}</b></div>'
            f'<video controls preload="metadata" src="{src}"></video>'
            f'<div class="mvm"><span>{dur}</span><span>납품 {when}</span><span class="pill">{ver}</span><code>{h}</code></div></article>')
main = ('<div class="wrap mainview"><h1>마루시공전문가 11~20강</h1><div class="sub">완성 영상 10편 · 강 순서대로 · 1920×1080 · 파일 <code>02. 최종파일/마루시공_NN강.mp4</code></div>'
        '<div class="mvgrid">' + "".join(card(*r) for r in D[1:]) + '</div>'
        '<h2 class="mvref">참고 — 00강 (팀장님 제작)</h2><div class="mvgrid">' + card(*D[0], ref=True) + '</div></div>\n')
css = '''<style>
.topnav{position:sticky;top:0;z-index:50;background:rgba(245,245,247,.92);backdrop-filter:saturate(180%) blur(12px);-webkit-backdrop-filter:saturate(180%) blur(12px);border-bottom:1px solid var(--line)}
.topnav .in{max-width:1180px;margin:0 auto;padding:10px 16px;display:flex;gap:8px;align-items:center;overflow-x:auto;scrollbar-width:none}.topnav .in::-webkit-scrollbar{display:none}
.topnav .brand{font-weight:700;font-size:14px;margin-right:6px;white-space:nowrap}
.topnav button{font:600 13px/1 -apple-system,"Apple SD Gothic Neo",sans-serif;padding:8px 14px;border-radius:99px;border:1px solid var(--line);background:#fff;color:var(--ink);cursor:pointer;white-space:nowrap}
.topnav button.on{background:var(--blue);border-color:var(--blue);color:#fff}
[id]{scroll-margin-top:64px}
.wrap.mainview,.wrap.encview{display:none}body[data-view=main] .wrap.mainview{display:block}body[data-view=enc] .wrap.encview{display:block}
body:not([data-view=rec]) .wrap.main{display:none!important}
.mvgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;margin-top:16px}
.mv{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px}.mv.ref{border-style:dashed}
.mvh{display:flex;gap:10px;align-items:baseline;margin:0 0 10px}.mvn{font-weight:700;color:var(--blue);font-size:15px}.mvh b{font-size:15px}
.mvm{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;margin-top:10px;font-size:13px;color:var(--sub)}.mvm .pill{margin-left:0}.mvm code{font-size:12px;color:var(--sub)}
h2.mvref{font-size:16px;margin:36px 0 0;color:var(--sub)}
@media(max-width:720px){.mvgrid{grid-template-columns:1fr}}
</style>
<div class="topnav"><div class="in"><span class="brand">마루시공 11~20강</span><button type="button" data-go="main">완성 영상</button><button type="button" data-go="rec">수정 기록</button><button type="button" data-go="encode">용량·화질 설명</button><button type="button" data-go="howwe">작업 방식</button></div></div>
'''
js = '''<script>
(function(){var V={main:'.wrap.mainview',enc:'.wrap.encview',how:'.wrap.howwrap'};
function viewOf(el){for(var k in V){if(el.closest(V[k]))return k;}return 'rec';}
function setView(v){document.body.dataset.view=v;document.body.classList.toggle('howmode',v==='how');
 document.querySelectorAll('.topnav button').forEach(function(b){var g=b.dataset.go;b.classList.toggle('on',(g==='main'&&v==='main')||(g==='rec'&&v==='rec')||(g==='encode'&&v==='enc')||(g==='howwe'&&v==='how'));});}
function route(){var h=decodeURIComponent(location.hash.slice(1));
 if(!h||h==='main'){setView('main');window.scrollTo(0,0);return;}
 if(h==='rec'){setView('rec');window.scrollTo(0,0);return;}
 var el=document.getElementById(h);if(!el){setView('main');return;}
 setView(viewOf(el));requestAnimationFrame(function(){if(h==='howwe'||h==='encode'||h==='main')window.scrollTo(0,0);else el.scrollIntoView();});}
function go(h){if(location.hash==='#'+h)route();else location.hash=h;}
document.addEventListener('DOMContentLoaded',function(){
 document.querySelectorAll('.topnav button').forEach(function(b){b.addEventListener('click',function(){go(b.dataset.go);});});
 document.querySelectorAll('.howbtn').forEach(function(b){b.addEventListener('click',function(){go(b.classList.contains('howback')?'main':'howwe');});});
 window.addEventListener('hashchange',route);route();});
})();
</script>
'''
# ① 옛 작업방식 토글 스크립트 → 새 화면 전환 스크립트(같은 일 + 화면 4개)
old_js = re.search(r"<script>\ndocument\.addEventListener\('DOMContentLoaded',function\(\)\{var b=document\.getElementById\('howbtn'\).*?</script>", s, re.S)
assert old_js; s = s[:old_js.start()] + js + s[old_js.end():]
# ② 용량 설명(#encodewrap)을 수정 기록 화면 밖 자기 화면으로 옮김(내용 그대로)
m = re.search(r'<div id="encodewrap">.*?</div>\n(?=<div id="midotwrap">)', s, re.S); assert m
enc = m.group(0); s = s[:m.start()] + s[m.end():]
# ③ 네비·메인·용량 화면을 작업 방식 화면 앞에
a = '<div class="wrap howwrap">'; assert s.count(a) == 1
s = s.replace(a, css + main + '<div class="wrap encview">' + enc + '</div>\n' + a)
# ④ 수정 기록 화면의 옛 nav 첫 링크(#encode)는 그대로 둠 — 누르면 용량 화면으로 전환
open(p, "w").write(s); print("ok", len(s))
