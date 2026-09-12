# -*- coding: utf-8 -*-
"""넘김 연출 제거 → 자연스러운 꾸밈 → 버그 수정. 한 번에 적용하는 패치."""
import io, os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ══════════ 1. 스케치북 넘김 연출 제거 — 새 쪽은 그냥 살짝 내려앉는다 ══════════
sub('''      var was = stage.querySelector('.pg.now');
      var flip = was && S.stageBook === rev.b && rev.i === S.stageIdx + 1 && r.phase === 'reveal';
      if (flip) {
        was.classList.remove('now'); was.classList.add('leaf');
        was.addEventListener('animationend', function(){ was.remove(); });
        setTimeout(function(){ if (was.parentNode) was.remove(); }, 900);
      } else {
        stage.innerHTML = '';
      }
      var pg = (r.pages || [])[rev.i];
      if (pg) stage.insertAdjacentHTML('afterbegin', pageHtml(pg, rev.i, 'now' + (r.phase === 'done' && rev.i > 0 ? ' last' : '')));''',
'''      stage.innerHTML = '';
      var pg = (r.pages || [])[rev.i];
      if (pg) stage.insertAdjacentHTML('afterbegin', pageHtml(pg, rev.i, 'now' + (r.phase === 'done' && rev.i > 0 ? ' last' : ''), rev.i + 1, rev.pages));''')
s = re.sub(r'\.stage \.pg\.leaf\{[^}]*\}\n@keyframes flipup\{[^}]*\}\n', '', s)
s = s.replace('@media (prefers-reduced-motion:reduce){.stage .pg.leaf{animation:none;display:none}.stage .pg.now{animation:none}}',
              '@media (prefers-reduced-motion:reduce){.stage .pg.now{animation:none}}')
s = s.replace('.stage{position:relative;perspective:1200px;min-height:80px}', '.stage{position:relative;min-height:80px}')
sub('.stage .pg.now{animation:settle .35s ease-out}\n@keyframes settle{from{transform:translateY(6px)}to{transform:none}}',
    '.stage .pg.now{animation:settle .32s ease-out}\n@keyframes settle{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}')
s = s.replace("/* ── 공개 — 스케치북 한 권. 지금 쪽 하나가 크게, 다음을 누르면 위 고리를 축으로 젖혀 올라가고 그 밑 쪽이 드러난다 ── */",
              "/* ── 공개 — 스케치북 한 권. 지금 쪽 하나가 크게, 지난 쪽은 아래에 작게 ── */")

# 쪽마다 오른쪽 위에 '2 / 5' 쪽수 귀표
sub('''function pageHtml(pg, k, cls){
  var cap = k === 0 ? '고른 말' : (pg.kind === 'draw' ? '그림' : '추측');
  return '<div class="pg ' + cls + (k === 0 ? ' first' : '') + (pg.word === '…' ? ' miss' : '') + '">' +
    '<div class="by"><span>' + cap + ' · ' + esc(pg.by) + '</span><button class="star" data-k="' + k + '"></button></div>' +''',
'''function pageHtml(pg, k, cls, no, of){
  var cap = k === 0 ? '고른 말' : (pg.kind === 'draw' ? '그림' : '추측');
  return '<div class="pg ' + cls + (k === 0 ? ' first' : '') + (pg.word === '…' ? ' miss' : '') + '">' +
    (no ? '<i class="tab num">' + no + ' / ' + of + '</i>' : '') +
    '<div class="by"><span>' + cap + ' · ' + esc(pg.by) + '</span><button class="star" data-k="' + k + '"></button></div>' +''')
sub('.pg.first{background-color:var(--yellow)}',
    '''.pg .tab{position:absolute;right:-3px;top:-3px;font-style:normal;font-size:13px;font-weight:700;color:var(--ink);
  background:var(--yellow);border:3px solid var(--ink);border-radius:0 12px 0 12px;padding:1px 10px;box-shadow:2px 2px 0 var(--ink)}
.pg.first .tab{background:#fff}
.pg .by{padding-right:70px}
.pg.first{background-color:var(--yellow)}''')

# ══════════ 2. 꾸밈 — 같은 결로 컴포넌트 추가 ══════════
# 대기실: 방 번호 큰 표찰(초대용) + 빈자리 유령 칸
sub('''  <section class="card hide" id="sLobby">
    <p class="lede" id="lobbyLede"></p>
    <div class="who" id="whoLobby"></div>''',
'''  <section class="card hide" id="sLobby">
    <div class="codebox">
      <div class="cap">방 번호</div>
      <div class="code num" id="lobbyCode"></div>
      <button class="btn sm" id="bCopy2">링크 복사</button>
    </div>
    <p class="lede" id="lobbyLede"></p>
    <div class="who" id="whoLobby"></div>''')
sub('''/* ── 사람들 ── */''',
'''/* ── 방 번호 표찰 — 옆 사람에게 불러 주는 용도 ── */
.codebox{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:6px 14px;padding:10px 14px;
  background:var(--yellow);border:3px solid var(--ink);border-radius:14px;box-shadow:4px 4px 0 var(--ink);transform:rotate(-.6deg);margin-bottom:12px}
.codebox .cap{font-size:14px;color:#7a5a1a}
.codebox .code{font-size:clamp(28px,8vw,40px);letter-spacing:.22em;font-weight:700;line-height:1;text-shadow:2px 2px 0 rgba(61,43,31,.18)}
.codebox .btn{background:#fff}
.who .p.ghost{border-style:dashed;background:transparent;color:var(--dim);box-shadow:none;opacity:.7}
.who .p.ghost .dot{background:transparent;border-style:dashed}

/* ── 사람들 ── */''')
sub("""    $('#whoLobby').innerHTML = whoHtml(r, false);""",
    """    $('#lobbyCode').textContent = r.code;
    var ghosts = '';
    for (var gi = n; gi < 4; gi++) ghosts += '<span class="p ghost"><i class="dot"></i>빈 자리</span>';   // 넷이 될 때까지 빈칸을 보여 준다
    $('#whoLobby').innerHTML = whoHtml(r, false) + ghosts;""")
sub("""$('#bCopy').onclick = function(){""", """$('#bCopy2').onclick = function(){ $('#bCopy').click(); };
$('#bCopy').onclick = function(){""")
sub('''    <div class="row">
      <button class="btn sm" id="bCopy">초대 링크 복사</button>
      <button class="btn go" id="bStart">시작</button>
    </div>''',
'''    <div class="row">
      <button class="btn sm hide" id="bCopy">초대 링크 복사</button>
      <button class="btn go big" id="bStart">시작</button>
    </div>''')

# 제시어 고르기: 카드 위에 '카드' 느낌의 작은 귀퉁이 색 점
sub('''.six button.on{background:var(--yellow)}''',
'''.six button.on{background:var(--yellow)}
.six button::before{content:"";position:absolute;left:10px;top:10px;width:9px;height:9px;border-radius:50%;background:var(--pink);border:2px solid var(--ink)}
.six button:nth-child(2)::before{background:var(--blue)}.six button:nth-child(3)::before{background:var(--green)}
.six button:nth-child(4)::before{background:var(--orange)}.six button:nth-child(5)::before{background:#9775fa}.six button:nth-child(6)::before{background:var(--red)}
.six button{position:relative}''')

# 기다리는 화면: 시계도 같이 보이게 이미 있음. 낸 사람은 초록 — 이미 있음.
# 시계: 10초 남으면 빨갛게 떨리는 것 이미 있음.

# ══════════ 3. 버그 수정 ══════════
# (a) 지우개가 종이 점무늬까지 지워 얼룩이 남는다 → 획은 따로 그려서 얹는다
sub("""function paint(cv, strokes){
  var dpr = Math.min(2, window.devicePixelRatio || 1);
  /* 폭은 CSS 가 정한다. 혹시 0 으로 읽히면 둘레에서 받아 온다 — 제 속성값을 따라가면 커지기만 한다 */
  var w = cv.clientWidth || (cv.parentElement && cv.parentElement.clientWidth) || 300;
  cv.width = Math.round(w * dpr); cv.height = Math.round(w * dpr);
  var g = cv.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  var k = w / 1024;
  g.fillStyle = '#ece2cc';                       // 도화지 점무늬 — 바탕일 뿐, 획에는 안 들어간다
  for (var gy = 64; gy < 1024; gy += 64) for (var gx = 64; gx < 1024; gx += 64) g.fillRect(gx * k - .8, gy * k - .8, 1.6, 1.6);
  g.lineCap = 'round'; g.lineJoin = 'round';
  (strokes || []).forEach(function(st){
    var p = st.p; if (!p || p.length < 2) return;
    g.strokeStyle = st.c === ERASER ? PAPER : (PENS[st.c] || PENS[0]);
    g.lineWidth = (NIBS[st.w] || NIBS[0]) * k * (st.c === ERASER ? 2.2 : 1);
    g.beginPath();
    g.moveTo(p[0] * k, p[1] * k);
    if (p.length === 2) { g.lineTo(p[0] * k + .1, p[1] * k + .1); }
    for (var i = 2; i + 1 < p.length; i += 2) g.lineTo(p[i] * k, p[i + 1] * k);
    g.stroke();
  });
}""",
"""var inkLayer = document.createElement('canvas');   // 획만 그리는 투명한 층. 지우개는 여기서만 파낸다
function paint(cv, strokes){
  var dpr = Math.min(2, window.devicePixelRatio || 1);
  /* 폭은 CSS 가 정한다. 혹시 0 으로 읽히면 둘레에서 받아 온다 — 제 속성값을 따라가면 커지기만 한다 */
  var w = cv.clientWidth || (cv.parentElement && cv.parentElement.clientWidth) || 300;
  var px = Math.round(w * dpr);
  cv.width = px; cv.height = px;
  var k = w / 1024;

  /* 획은 투명한 층에 그린다 — 지우개가 종이 점무늬까지 지워 얼룩을 남기지 않게 */
  inkLayer.width = px; inkLayer.height = px;
  var ink = inkLayer.getContext('2d');
  ink.setTransform(dpr, 0, 0, dpr, 0, 0);
  ink.lineCap = 'round'; ink.lineJoin = 'round';
  (strokes || []).forEach(function(st){
    var p = st.p; if (!p || p.length < 2) return;
    var erase = st.c === ERASER;
    ink.globalCompositeOperation = erase ? 'destination-out' : 'source-over';
    ink.strokeStyle = erase ? '#000' : (PENS[st.c] || PENS[0]);
    ink.lineWidth = (NIBS[st.w] || NIBS[0]) * k * (erase ? 2.2 : 1);
    ink.beginPath();
    ink.moveTo(p[0] * k, p[1] * k);
    if (p.length === 2) { ink.lineTo(p[0] * k + .1, p[1] * k + .1); }
    for (var i = 2; i + 1 < p.length; i += 2) ink.lineTo(p[i] * k, p[i + 1] * k);
    ink.stroke();
  });

  var g = cv.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  g.fillStyle = '#ece2cc';                       // 도화지 점무늬 — 바탕일 뿐, 획에는 안 들어간다
  for (var gy = 64; gy < 1024; gy += 64) for (var gx = 64; gx < 1024; gx += 64) g.fillRect(gx * k - .8, gy * k - .8, 1.6, 1.6);
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.drawImage(inkLayer, 0, 0);
}""")

# (b) 맞히기 입력창이 남이 낼 때마다 다시 포커스돼 폰에서 키보드가 들썩인다 → 화면이 처음 뜰 때만
sub("""      show('#sGuess');
      $('#gw').value = '';
      requestAnimationFrame(function(){ paint($('#guessShot'), r.prev ? r.prev.strokes : []); });
      $('#gw').focus();""",
"""      var fresh = $('#sGuess').classList.contains('hide') || S.guessFor !== r.round;
      show('#sGuess');
      if (fresh) { $('#gw').value = ''; S.guessFor = r.round; $('#gw').focus(); }   // 처음 뜰 때만 비우고 포커스
      requestAnimationFrame(function(){ paint($('#guessShot'), r.prev ? r.prev.strokes : []); });""")

# (c) 시간이 다 되면 그리던 것·적던 것이 날아간다 → 1초 남았을 때 있는 그대로 낸다
sub("""  var beat = function(){
    var s = Math.max(0, Math.round((end - Date.now()) / 1000));
    c.textContent = s;
    c.classList.toggle('hot', s <= 10);
    if (s <= 0) clearInterval(S.tick);
  };""",
"""  var beat = function(){
    var s = Math.max(0, Math.round((end - Date.now()) / 1000));
    c.textContent = s;
    c.classList.toggle('hot', s <= 10);
    if (s <= 1) autoHand();                       // 시간이 다 되기 직전, 하던 것을 그대로 낸다
    if (s <= 0) clearInterval(S.tick);
  };""")
sub("""/** 새 쪽을 맡을 때만 그림판을 비운다. 같은 쪽을 다시 그리는 중이면 남겨 둔다 */""",
"""/** 시계가 다 되기 직전 — 안 냈으면 그리던 그림·적던 답을 그대로 낸다. 빈 쪽으로 남는 것보단 낫다 */
function autoHand(){
  var r = S.room;
  if (!r || S.sent || r.done) return;
  if (!$('#sDraw').classList.contains('hide') && pad.strokes.length) $('#bDrawDone').click();
  else if (!$('#sGuess').classList.contains('hide') && ($('#gw').value || '').trim()) $('#bGuessDone').click();
}

/** 새 쪽을 맡을 때만 그림판을 비운다. 같은 쪽을 다시 그리는 중이면 남겨 둔다 */""")

# (d) 대기실 안내 문구 정리 — 방 번호 표찰이 생겼으니 lede 는 비운다
sub("""    $('#lobbyNote').textContent = n < 4 ? (4 - n) + '명 더' : '';""",
    """    $('#lobbyNote').textContent = '';""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', 'leaf' in s, 'flipup' in s)
