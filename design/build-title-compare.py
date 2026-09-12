# -*- coding: utf-8 -*-
"""타이틀 그림 열 장을 한 파일에서 눌러 비교한다. 그림·글꼴은 make-title.py 것을 그대로 쓴다."""
import io, os, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mt", os.path.join(HERE, "make-title.py"))
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)

ITEMS = [{"no": n, "name": mt.ART[k][0], "desc": mt.ART[k][1], "art": mt.ART[k][2]} for n, k in enumerate(mt.ORDER, 1)]

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>텔레스트레이션 타이틀 그림 고르기</title>
<style>
%(face)s
:root{--paper:#fff6e0;--ink:#3d2b1f;--dim:#8a7461;--yellow:#ffd43b;--green:#51cf66;--orange:#e8590c}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);padding:20px 16px 48px;font-family:'Jua',system-ui,sans-serif}
.wrap{max-width:1000px;margin:0 auto}
h1{font-size:26px;margin:0 0 4px}
.sub{font-size:15px;color:var(--dim);margin:0 0 16px}
.tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:18px}
.tabs button{font:inherit;font-size:15px;cursor:pointer;padding:5px 12px;border:3px solid var(--ink);border-radius:999px;
  background:#fff;color:var(--ink);box-shadow:2px 2px 0 var(--ink)}
.tabs button.on{background:var(--yellow)}
.tabs button b{margin-right:5px}
.split{display:grid;grid-template-columns:390px 1fr;gap:24px;align-items:start}
@media (max-width:820px){.split{grid-template-columns:1fr}}

/* 타이틀 화면 그대로 — 상자 없이, 가운데 정렬 */
.screen{width:390px;min-height:520px;background:var(--paper);border:3px dashed #d9c9a8;border-radius:16px;padding:34px 14px 26px;
  display:flex;flex-direction:column;align-items:center;text-align:center}
.logo{display:flex;gap:7px;line-height:1}
.logo b{display:inline-block;font-size:50px;text-shadow:2px 2px 0 var(--ink)}
.squig{width:250px;height:11px;display:block;margin-top:2px}
.eyebrow{margin:12px 0 0;font-size:15px;letter-spacing:.2em;color:var(--dim)}
.art{width:100%%;display:block;margin-top:18px}
.go{margin-top:20px;background:var(--green);border:4px solid var(--ink);border-radius:16px;padding:9px 46px;font-size:24px;box-shadow:5px 5px 0 var(--ink)}
.rules{margin-top:16px;font-size:16px;color:var(--dim);border-bottom:3px solid transparent}

.note{background:#fff;border:3px solid var(--ink);border-radius:16px;padding:14px 16px;box-shadow:4px 4px 0 var(--ink);margin-bottom:16px}
.note h2{font-size:22px;margin:0 0 4px}
.note p{margin:0;font-size:15px;color:var(--dim)}
.all{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:9px}
.all button{font:inherit;cursor:pointer;text-align:left;padding:8px 10px 6px;background:#fff;border:3px solid var(--ink);
  border-radius:14px;box-shadow:2px 2px 0 var(--ink);color:var(--ink)}
.all button.on{background:var(--yellow)}
.all svg{width:100%%;display:block}
.all .n{font-size:13px;display:block;margin-top:4px}
.hint{font-size:13px;color:var(--dim);margin-top:14px}
</style>
</head>
<body>
<div class="wrap">
  <h1>텔레스트레이션 — 타이틀 그림 고르기</h1>
  <p class="sub">숫자를 누르면 가운데 그림만 바뀝니다. 제목과 단추는 게임 그대로입니다. 글꼴은 이 파일 안에 있습니다.</p>
  <div class="tabs" id="tabs"></div>
  <div class="split">
    <div class="screen">
      <div class="logo">%(logo)s</div>
      <svg class="squig" viewBox="0 0 280 11" fill="none"><path d="M3 7C28 2 52 9 78 5s48 5 74 1 47 6 73 2 48 1 48 1" stroke="#e8590c" stroke-width="4" stroke-linecap="round"/></svg>
      <p class="eyebrow">그림과 말이 한 바퀴</p>
      <svg class="art" id="art" viewBox="0 0 380 200" fill="none"></svg>
      <div class="go">게임 시작</div>
      <div class="rules">규칙</div>
    </div>
    <div>
      <div class="note"><h2 id="nName"></h2><p id="nDesc"></p></div>
      <div class="all" id="all"></div>
      <p class="hint">숫자키 1~9 · 0 으로도 바꿉니다.</p>
    </div>
  </div>
</div>
<script>
var ITEMS = %(items)s;
var cur = 0;
document.getElementById('tabs').innerHTML = ITEMS.map(function(p,i){ return '<button data-i="'+i+'"><b>'+p.no+'</b>'+p.name+'</button>'; }).join('');
document.getElementById('all').innerHTML = ITEMS.map(function(p,i){
  return '<button data-i="'+i+'"><svg viewBox="0 0 380 200" fill="none">'+p.art+'</svg><span class="n">'+p.no+'. '+p.name+'</span></button>'; }).join('');
function pick(i){
  cur = i; var p = ITEMS[i];
  document.getElementById('art').innerHTML = p.art;
  document.getElementById('nName').textContent = p.no + '. ' + p.name;
  document.getElementById('nDesc').textContent = p.desc;
  document.querySelectorAll('#tabs button, #all button').forEach(function(b){ b.classList.toggle('on', +b.dataset.i === i); });
}
document.addEventListener('click', function(e){ var b = e.target.closest('#tabs button, #all button'); if (b) pick(+b.dataset.i); });
document.addEventListener('keydown', function(e){ if (e.key >= '1' && e.key <= '9') pick(+e.key - 1); if (e.key === '0') pick(9); });
pick(0);
</script>
</body>
</html>
"""

out = HTML % {"face": mt.FACE, "logo": mt.LOGO, "items": json.dumps(ITEMS, ensure_ascii=False)}
path = os.path.join(HERE, "title-compare.html")
io.open(path, "w", encoding="utf-8", newline="\n").write(out)
print("title-compare.html %.0f KB" % (len(out.encode("utf-8")) / 1024))
