# -*- coding: utf-8 -*-
"""화면이 줄었다 늘었다 하지 않게(머리글 자리 고정), 그리기가 버벅이지 않게(프레임당 한 번만 그림), 화면 전환을 부드럽게."""
import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 1. 머리글 높이 고정: 시계·라운드 칩·진행 띠는 사라져도 자리를 남긴다 ──
sub('''  var prog = '';
  for (var pi = 1; pi <= r.rounds; pi++) prog += '<i class="' + (pi < r.round ? 'did' : pi === r.round ? 'now' : '') + '"></i>';
  $('#prog').innerHTML = prog;
  $('#prog').classList.toggle('hide', !(r.phase === 'pick' || r.phase === 'play'));''',
'''  var prog = '';
  for (var pi = 1; pi <= r.rounds; pi++) prog += '<i class="' + (pi < r.round ? 'did' : pi === r.round ? 'now' : '') + '"></i>';
  $('#prog').innerHTML = prog;
  $('#prog').classList.remove('hide');
  $('#prog').classList.toggle('ghost', !(r.phase === 'pick' || r.phase === 'play'));   // 자리는 두고 안 보이게''')
sub("""  if (!r || r.phase === 'lobby') $('#prog').classList.add('hide');""",
    """  if (!r || r.phase === 'lobby') $('#prog').classList.add('hide');
  $('#step').classList.toggle('ghost', !!r && r.phase === 'lobby'); $('#step').classList.toggle('hide', !r);""")
sub("""  if (!r.left || (r.phase !== 'pick' && r.phase !== 'play')) { c.classList.add('hide'); return; }
  var end = Date.now() + r.left * 1000;
  c.classList.remove('hide');""",
"""  c.classList.remove('hide');
  if (!r.left || (r.phase !== 'pick' && r.phase !== 'play')) { c.classList.add('ghost'); c.classList.remove('hot'); return; }
  var end = Date.now() + r.left * 1000;
  c.classList.remove('ghost');""")
sub("""  if (!r) { show(S.entered ? '#sGate' : '#sTitle'); $('#clock').classList.add('hide'); return; }""",
    """  if (!r) { show(S.entered ? '#sGate' : '#sTitle'); $('#clock').classList.add('hide'); $('#prog').classList.add('hide'); return; }""")
sub('.hide{display:none!important}', '.hide{display:none!important}\n.ghost{visibility:hidden!important}   /* 자리는 차지하되 안 보인다 — 화면이 들썩이지 않게 */')

# ── 2. 그리기 버벅임: pointermove 마다가 아니라 프레임당 한 번만 다시 그린다. 바탕(종이+점)은 크기별로 한 번만 만들어 둔다 ──
sub("""var inkLayer = document.createElement('canvas');   // 획만 그리는 투명한 층. 지우개는 여기서만 파낸다
function paint(cv, strokes){""",
"""var inkLayer = document.createElement('canvas');   // 획만 그리는 투명한 층. 지우개는 여기서만 파낸다
var paperCache = { px:0, cv:null };                // 종이+점무늬 바탕. 크기가 같으면 다시 안 그린다
function paper(px, w, k, dpr){
  if (paperCache.px === px) return paperCache.cv;
  var c = document.createElement('canvas'); c.width = px; c.height = px;
  var g = c.getContext('2d'); g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  g.fillStyle = '#ece2cc';
  for (var gy = 64; gy < 1024; gy += 64) for (var gx = 64; gx < 1024; gx += 64) g.fillRect(gx * k - .8, gy * k - .8, 1.6, 1.6);
  paperCache = { px:px, cv:c };
  return c;
}
function paint(cv, strokes){""")
sub("""  var g = cv.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  g.fillStyle = '#ece2cc';                       // 도화지 점무늬 — 바탕일 뿐, 획에는 안 들어간다
  for (var gy = 64; gy < 1024; gy += 64) for (var gx = 64; gx < 1024; gx += 64) g.fillRect(gx * k - .8, gy * k - .8, 1.6, 1.6);
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.drawImage(inkLayer, 0, 0);""",
"""  var g = cv.getContext('2d');
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.drawImage(paper(px, w, k, dpr), 0, 0);       // 도화지 점무늬 — 바탕일 뿐, 획에는 안 들어간다
  g.drawImage(inkLayer, 0, 0);""")
sub("""function padSize(){ paint(pad.cv, pad.strokes); rings(); }""",
"""function padSize(){ paint(pad.cv, pad.strokes); rings(); }
/* 그리는 중에는 프레임당 한 번만 — pointermove 는 한 프레임에 여러 번 온다 */
var padTick = false;
function padSoon(){ if (padTick) return; padTick = true; requestAnimationFrame(function(){ padTick = false; paint(pad.cv, pad.strokes); }); }""")
sub("""    if (p.length < 1200) p.push(xy[0], xy[1]);
  }
  padSize();
});""",
"""    if (p.length < 1200) p.push(xy[0], xy[1]);
  }
  padSoon();
});""")
sub("""  pad.cur = { c:pad.pen, w:pad.nib, p:[xy[0], xy[1]] };
  pad.strokes.push(pad.cur);
  padSize();""",
"""  pad.cur = { c:pad.pen, w:pad.nib, p:[xy[0], xy[1]] };
  pad.strokes.push(pad.cur);
  padSoon();""")

# ── 3. 화면 전환을 부드럽게: 나타나는 판은 살짝 떠오른다 ──
sub('''function show(){
  var want = [].slice.call(arguments);
  SECTIONS.forEach(function(s){ $(s).classList.toggle('hide', want.indexOf(s) < 0); });
}''',
'''function show(){
  var want = [].slice.call(arguments);
  SECTIONS.forEach(function(s){
    var el = $(s), was = !el.classList.contains('hide'), now = want.indexOf(s) >= 0;
    el.classList.toggle('hide', !now);
    if (now && !was) { el.classList.remove('in'); void el.offsetWidth; el.classList.add('in'); }   // 새로 뜨는 판만
  });
}''')
sub('.card.tilt{transform:rotate(-.5deg)}',
'''.card.tilt{transform:rotate(-.5deg)}
.card.in,.title.in{animation:in .22s ease-out}
@keyframes in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.card.in,.title.in{animation:none}}''')

# ── 4. 레이아웃 손질: 넓은 화면 옆 판 간격·정렬, 시계 떨림 줄이기 ──
sub('@keyframes shake{0%,100%{transform:rotate(5deg)}50%{transform:rotate(-5deg) scale(1.06)}}',
    '@keyframes shake{0%,100%{transform:rotate(5deg)}50%{transform:rotate(-5deg)}}')
sub('''  #sDraw,#sGuess{display:grid;grid-template-columns:minmax(0,1fr) 340px;grid-template-rows:auto 1fr;gap:6px 22px;align-items:stretch}''',
    '''  #sDraw,#sGuess{display:grid;grid-template-columns:minmax(0,1fr) 340px;grid-template-rows:auto 1fr;gap:10px 24px;align-items:stretch}''')
sub('''.tools2{align-items:center;margin-top:0}''', '''.tools2{align-items:center;margin-top:0;gap:8px}''')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
