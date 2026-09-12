# -*- coding: utf-8 -*-
"""눌러서 바로 바꿔 보는 서체 비교 페이지 한 장. 글꼴은 파일 안에 박혀 있어 인터넷 없이도 그대로 보인다."""
import io, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
FACES = io.open(os.path.join(HERE, "_faces.css"), encoding="utf-8").read()

# (번호, 제목서체, 본문서체, 크기배, 한 줄 설명, 걸리는 점)
PAIRS = [
    (1,  "Gaegu",            "Hi Melody",    1.00, "지금 쓰는 것. 연필로 눌러쓴 공책 글씨", "획이 가늘어 작은 글자가 흐려집니다"),
    (2,  "Jua",              "Gaegu",        0.94, "둥글고 통통. 크레용 두께와 잘 맞습니다", "길어지면 글자가 다 비슷해 보입니다"),
    (3,  "Do Hyeon",         "Gowun Dodum",  0.94, "각지고 또렷. 멀리서도 읽힙니다", "손맛이 없어 그림과 조금 따로 놉니다"),
    (4,  "Black Han Sans",   "Jua",          0.90, "제목이 아주 굵어 제시어가 쿵 박힙니다", "굵기가 하나뿐이라 강약을 못 줍니다"),
    (5,  "Nanum Pen Script", "Gaegu",        1.22, "사인펜으로 슥슥 쓴 글씨", "아주 작게 쓰면 읽기 어렵습니다"),
    (6,  "Gamja Flower",     "Gowun Dodum",  1.12, "삐뚤빼뚤 어린이 글씨", "진지한 안내문까지 장난스러워집니다"),
    (7,  "Poor Story",       "Gowun Dodum",  1.10, "동화책에서 본 듯한 글씨", "받침 많은 낱말이 좁아 보입니다"),
    (8,  "Yeon Sung",        "Jua",          1.02, "두툼한 붓으로 눌러쓴 글씨", "숫자가 뭉툭해 시계가 덜 또렷합니다"),
    (9,  "Kirang Haerang",   "Gowun Dodum",  1.08, "옛 간판 붓글씨. 나이 든 결이 섞입니다", "크레용보다 어른스러워 따로 놉니다"),
    (10, "Gothic A1",        "Noto Sans KR", 0.92, "손글씨를 뺀 대조군. 제일 잘 읽힙니다", "크레용 그림과 성격이 어긋납니다"),
]

DATA = [{"no": n, "d": d, "b": b, "s": s, "good": g, "bad": x} for n, d, b, s, g, x in PAIRS]

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>텔레스트레이션 서체 고르기</title>
<style>
%(faces)s
:root{--paper:#fff6e0;--ink:#3d2b1f;--dim:#8a7461;--card:#fffdf8;--orange:#e8590c;
      --yellow:#ffd43b;--blue:#74c0fc;--green:#51cf66;--red:#e03131;--pink:#f06595;
      --d:"Gaegu";--b:"Hi Melody";--k:1}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);padding:20px 16px 48px;
     font-family:var(--b),system-ui,sans-serif}
.wrap{max-width:980px;margin:0 auto}
h1{font-family:var(--d);font-size:26px;margin:0 0 4px}
.sub{font-size:15px;color:var(--dim);margin:0 0 16px}
.sub b{color:var(--orange)}

/* 번호 단추 */
.tabs{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:18px}
.tabs button{font:inherit;font-size:14px;cursor:pointer;padding:6px 12px;border:3px solid var(--ink);
  border-radius:999px;background:#fff;color:var(--ink);box-shadow:2px 2px 0 var(--ink);
  font-family:system-ui,sans-serif}
.tabs button.on{background:var(--yellow)}
.tabs button b{font-size:15px;margin-right:4px}

.split{display:grid;grid-template-columns:390px 1fr;gap:22px;align-items:start}
@media (max-width:800px){.split{grid-template-columns:1fr}}

/* 견본 화면 */
.screen{width:390px;background:var(--paper);border:4px solid var(--ink);border-radius:20px;
  padding:16px;box-shadow:6px 6px 0 var(--ink);display:flex;flex-direction:column;gap:11px}
.logo{display:flex;align-items:flex-end;gap:1px;font-family:var(--d);line-height:1}
.logo span{display:inline-block;text-shadow:2px 2px 0 var(--ink);font-weight:700}
.squig{display:block;width:74%%;height:10px;margin-top:-3px}
.bar{display:flex;align-items:center;gap:7px}
.chip{background:#fff;border:3px solid var(--ink);border-radius:999px;padding:0 11px;font-weight:700;
  box-shadow:2px 2px 0 var(--ink)}
.chip.code{letter-spacing:.16em}
.clock{margin-left:auto;background:var(--yellow);border:3px solid var(--ink);border-radius:50%%;
  width:46px;height:46px;display:flex;align-items:center;justify-content:center;font-family:var(--d);
  font-weight:700;transform:rotate(5deg);box-shadow:3px 3px 0 var(--ink);flex:none}
.prompt{background:var(--blue);border:3px solid var(--ink);border-radius:16px;padding:10px;
  text-align:center;box-shadow:4px 4px 0 var(--ink);transform:rotate(.7deg)}
.prompt .cap{color:#194663}
.prompt .big{font-family:var(--d);font-weight:700;line-height:1.15;color:#fff;
  text-shadow:2px 2px 0 var(--ink)}
.line{color:var(--dim)}
.pens{display:flex;gap:3px;align-items:flex-end;justify-content:center}
.pens svg{display:block;width:24px;height:56px}
.go{background:var(--green);border:4px solid var(--ink);border-radius:16px;text-align:center;
  font-family:var(--d);font-weight:700;padding:9px;box-shadow:5px 5px 0 var(--ink)}
.score{border-top:3px dotted #e0d2b8;padding-top:8px;display:flex;align-items:baseline}
.score .nm{font-weight:700}
.score .sm{color:var(--dim);margin-left:5px}
.score .pt{margin-left:auto;font-family:var(--d);font-weight:700}

/* 오른쪽 설명 + 한눈에 보기 */
.note{background:#fff;border:3px solid var(--ink);border-radius:16px;padding:14px 16px;
  box-shadow:4px 4px 0 var(--ink);margin-bottom:16px}
.note h2{font-family:var(--d);font-size:22px;margin:0 0 6px}
.note p{margin:4px 0;font-size:15px}
.note .bad{color:#b08a6a}
.all{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:9px}
.all button{font:inherit;cursor:pointer;text-align:left;padding:9px 12px;background:#fff;
  border:3px solid var(--ink);border-radius:14px;box-shadow:2px 2px 0 var(--ink);color:var(--ink)}
.all button.on{background:var(--yellow)}
.all .w{font-size:24px;font-weight:700;line-height:1.2;display:block}
.all .n{font-size:12px;color:var(--dim);font-family:system-ui,sans-serif}
.hint{font-size:13px;color:var(--dim);margin-top:14px;font-family:system-ui,sans-serif}
.one{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:-6px 0 18px;
  font-family:system-ui,sans-serif;font-size:14px}
.one label{display:flex;align-items:center;gap:7px;cursor:pointer;background:#fff;
  border:3px solid var(--ink);border-radius:999px;padding:5px 14px;box-shadow:2px 2px 0 var(--ink)}
.one input{width:17px;height:17px;accent-color:var(--orange);cursor:pointer}
.one span{color:var(--dim)}
</style>
</head>
<body>
<div class="wrap">
  <h1>텔레스트레이션 — 서체 고르기</h1>
  <p class="sub">숫자를 누르면 글자만 바뀝니다. 크레용 차림은 그대로입니다. <b>글꼴은 이 파일 안에 들어 있어 인터넷 없이도 그대로 보입니다.</b></p>

  <div class="tabs" id="tabs"></div>

  <div class="one">
    <label><input type="checkbox" id="same"> <b>본문도 같은 서체로</b> — 끄면 제목과 본문에 다른 글꼴 두 벌을 씁니다</label>
    <span id="pairNow"></span>
  </div>

  <div class="split">
    <div class="screen" id="screen">
      <div class="logo" id="logo"></div>
      <svg class="squig" viewBox="0 0 280 11" fill="none">
        <path d="M3 7C28 2 52 9 78 5s48 5 74 1 47 6 73 2 48 1 48 1" stroke="#e8590c" stroke-width="4" stroke-linecap="round"/>
      </svg>
      <div class="bar">
        <span class="chip code" id="f15a">NPW3</span>
        <span class="chip" id="f15b">2 / 4라운드</span>
        <span class="clock" id="f22a">47</span>
      </div>
      <div class="prompt">
        <div class="cap" id="f16">이 말을 그리세요</div>
        <div class="big" id="f34">사면초가</div>
      </div>
      <div class="line" id="f17">넷 모였습니다. 넷부터 시작할 수 있고 열까지 들어옵니다.</div>
      <div class="pens" id="pens"></div>
      <div class="go" id="f24">다 그렸어요!</div>
      <div class="score">
        <span class="nm" id="f18">1. 낙서봇</span>
        <span class="sm" id="f14">★3 · 한 바퀴 돌아옴</span>
        <span class="pt" id="f22b">4점</span>
      </div>
    </div>

    <div>
      <div class="note">
        <h2 id="nName"></h2>
        <p id="nGood"></p>
        <p class="bad" id="nBad"></p>
      </div>
      <div class="all" id="all"></div>
      <p class="hint">숫자키 1~9 · 0 으로도 바꿉니다. 손글씨 서체는 같은 크기에서 작게 나와, 서체마다 0.90~1.22배로 맞춰 두었습니다.</p>
    </div>
  </div>
</div>

<script>
var PAIRS = %(data)s;
var LOGO = ['텔','레','스','트','레','이','션'];
var COLORS = ['#e03131','#e8590c','#ffd43b','#51cf66','#74c0fc','#f06595','#e8590c'];
var ROT = [-4,3,-2,4,-3,2,-4];
var PENS = ['#3d2b1f','#e03131','#f76707','#ffd43b','#51cf66','#339af0','#9775fa','#f06595'];
var cur = 0;

function crayon(c){
  return '<svg viewBox="0 0 26 64"><path d="M13 3 L20.5 15 L20.5 59 Q20.5 61.5 18 61.5 L8 61.5'
    + ' Q5.5 61.5 5.5 59 L5.5 15 Z" fill="' + c + '" stroke="#3d2b1f" stroke-width="2.6" stroke-linejoin="round"/>'
    + '<rect x="5.5" y="26" width="15" height="21" fill="#fff6e0" stroke="#3d2b1f" stroke-width="2.6"/>'
    + '<path d="M8.6 32.5h8.8M8.6 40.5h8.8" stroke="' + c + '" stroke-width="2.3" stroke-linecap="round"/></svg>';
}

document.getElementById('pens').innerHTML = PENS.map(crayon).join('');
document.getElementById('logo').innerHTML = LOGO.map(function(ch,i){
  return '<span style="color:' + COLORS[i] + ';transform:rotate(' + ROT[i] + 'deg)">' + ch + '</span>';
}).join('');

document.getElementById('tabs').innerHTML = PAIRS.map(function(p,i){
  return '<button data-i="' + i + '"><b>' + p.no + '</b>' + p.d + '</button>';
}).join('');

document.getElementById('all').innerHTML = PAIRS.map(function(p,i){
  return '<button data-i="' + i + '">'
    + '<span class="w" style="font-family:\\'' + p.d + '\\';font-size:' + Math.round(24*p.s) + 'px">사면초가</span>'
    + '<span class="n">' + p.no + '. ' + p.d + ' + ' + p.b + '</span></button>';
}).join('');

var SIZES = { f14:14, f15a:15, f15b:15, f16:16, f17:17, f18:18, f22a:22, f22b:22, f24:24, f34:34 };

function pick(i){
  cur = i;
  var p = PAIRS[i], r = document.documentElement.style;
  var one = document.getElementById('same').checked;
  var body = one ? p.d : p.b;               // 한 벌로 쓸지, 제목·본문을 나눌지
  r.setProperty('--d', "'" + p.d + "'");
  r.setProperty('--b', "'" + body + "'");
  document.getElementById('pairNow').textContent =
    one ? ('지금: ' + p.d + ' 한 벌') : ('지금: 제목 ' + p.d + ' · 본문 ' + p.b);
  for (var id in SIZES) document.getElementById(id).style.fontSize = Math.round(SIZES[id] * p.s) + 'px';
  document.querySelectorAll('#logo span').forEach(function(s){ s.style.fontSize = Math.round(38*p.s) + 'px'; });
  document.getElementById('nName').textContent = p.no + '. ' + p.d + ' + ' + p.b;
  document.getElementById('nGood').textContent = p.good;
  document.getElementById('nBad').textContent = '걸리는 점 — ' + p.bad;
  document.querySelectorAll('#tabs button, #all button').forEach(function(b){
    b.classList.toggle('on', +b.dataset.i === i);
  });
}

document.addEventListener('click', function(e){
  var b = e.target.closest('#tabs button, #all button');
  if (b) pick(+b.dataset.i);
});
document.getElementById('same').addEventListener('change', function(){ pick(cur); });
document.addEventListener('keydown', function(e){
  if (e.key >= '1' && e.key <= '9') pick(+e.key - 1);
  if (e.key === '0') pick(9);
});
pick(0);
</script>
</body>
</html>
"""

out = HTML % {"faces": FACES, "data": json.dumps(DATA, ensure_ascii=False)}
path = os.path.join(HERE, "type-compare.html")
io.open(path, "w", encoding="utf-8", newline="\n").write(out)
print("→ type-compare.html  %.0f KB" % (len(out.encode("utf-8")) / 1024))
