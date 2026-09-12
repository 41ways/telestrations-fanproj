# -*- coding: utf-8 -*-
"""그리기 화면을 스케치북으로, 옆 판을 정돈, 나머지 화면에 꾸밈. 한 번 쓰고 버리는 패치."""
import io, re, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 타이틀은 조금 담백하게 ──
sub('.art{display:block;width:100%;max-width:380px;margin:30px auto 0;position:relative;z-index:1}',
    '.art{display:block;width:100%;max-width:340px;margin:26px auto 0;position:relative;z-index:1}')
sub('.title .squig{width:min(360px,86%);height:14px;margin:0 auto}', '.title .squig{width:min(300px,72%);height:12px;margin:0 auto}')

# ── 카드마다 도화지 점무늬, 초록 단추에 윤기 ──
sub('''.card{
  background:#fff;border:4px solid var(--ink);border-radius:20px;''',
'''.card{
  background:#fff radial-gradient(#ede3cf 1.1px,transparent 1.3px) 0 0/20px 20px;border:4px solid var(--ink);border-radius:20px;''')
sub('.btn.go{background:var(--green)}', '.btn.go{background:linear-gradient(#86e59a,var(--green) 45%)}')

# ── 그리기·맞히기 화면 짜임 ──
sub('''    <div class="prev"><div class="cap" id="drawCap">이 말을 그리세요</div><div class="big" id="drawWord"></div></div>
    <div class="pad"><canvas id="pad"></canvas></div>
    <div class="tools">
      <div class="pens" id="pens"></div>
      <div class="nibs" id="nibs"></div>
    </div>
    <div class="row">
      <button class="btn sm" id="bUndo">되돌리기</button>
      <button class="btn sm" id="bClear">전부 지우기</button>
    </div>
    <div class="row"><button class="btn go big" id="bDrawDone">다 그렸어요!</button></div>''',
'''    <div class="prev"><div class="cap" id="drawCap">이 말을 그리세요</div><div class="big" id="drawWord"></div></div>
    <div class="sheet"><div class="rings"></div><div class="pad"><canvas id="pad"></canvas></div></div>
    <div class="side">
      <div class="tray"><div class="pens" id="pens"></div></div>
      <div class="row tools2">
        <div class="nibs" id="nibs"></div>
        <button class="btn sm" id="bUndo">되돌리기</button>
        <button class="btn sm" id="bClear">전부 지우기</button>
      </div>
      <div class="row submit"><button class="btn go big" id="bDrawDone">다 그렸어요!</button></div>
    </div>''')
sub('''    <div class="prev shotbox"><div class="cap">무엇을 그린 걸까요</div><canvas class="shot" id="guessShot" style="margin-top:7px"></canvas></div>
    <label for="gw">한 마디로</label>
    <input type="text" id="gw" maxlength="24" placeholder="보이는 대로" autocomplete="off">
    <div class="row"><button class="btn go big" id="bGuessDone">이걸로 냅니다</button></div>''',
'''    <div class="prev shotbox"><div class="cap">무엇을 그린 걸까요</div></div>
    <div class="sheet"><div class="rings"></div><div class="pad view"><canvas class="shot" id="guessShot"></canvas></div></div>
    <div class="side">
      <label for="gw">한 마디로</label>
      <input type="text" id="gw" maxlength="24" placeholder="보이는 대로" autocomplete="off">
      <div class="row submit"><button class="btn go big" id="bGuessDone">이걸로 냅니다</button></div>
    </div>''')

i = s.index('/* ── 그림판 ── */'); j = s.index('/* ── 공개 ── */')
s = s[:i] + '''/* ── 그림판 — 스프링 스케치북 한 장 ── */
.sheet{position:relative;margin-top:16px}
.rings{height:24px;margin:0 20px -6px;position:relative;z-index:3;
  background:radial-gradient(circle at 50% 50%,transparent 4.6px,var(--ink) 5.4px,var(--ink) 8px,transparent 8.8px) 0 0/30px 24px repeat-x}
.pad{
  position:relative;width:100%;aspect-ratio:1;border-radius:14px;overflow:hidden;
  border:4px solid var(--ink);background:var(--card);touch-action:none;box-shadow:6px 6px 0 var(--yellow);
}
.pad::after{content:"";position:absolute;right:0;bottom:0;width:30px;height:30px;   /* 접힌 귀퉁이 */
  background:linear-gradient(135deg,transparent 50%,#e6dcc4 50%,#d9cfb5);border-top-left-radius:6px;pointer-events:none}
.pad canvas{display:block;width:100%;height:100%}
.pad.view{box-shadow:6px 6px 0 var(--blue)}
.pad.view canvas{border:0;border-radius:0}
.prev.shotbox{margin-bottom:0}

/* 옆 판 — 크레용 통, 굵기·되돌리기 한 줄, 맨 밑에 제출 */
.side{display:flex;flex-direction:column;gap:12px;margin-top:14px}
.tray{background:#fbf3df;border:3px solid var(--ink);border-radius:14px;padding:16px 10px 6px;box-shadow:3px 3px 0 var(--ink);
  background-image:linear-gradient(180deg,transparent 0 70%,#eadfc6 70%)}
.tools2{align-items:center;margin-top:0}
.tools2 .nibs{margin:0 auto 0 0}
.tools2 .btn{flex:0 0 auto}
.row.submit{margin-top:4px}
.pens{display:flex;gap:4px;align-items:flex-end;justify-content:center}
.pens button{border:0;padding:0;background:none;cursor:pointer;line-height:0;transition:transform .08s}
.pens button svg{display:block;width:30px;height:78px}
.pens button.eraser svg{height:56px}
.pens button.on{transform:translateY(-12px)}
.pens button.on svg{filter:drop-shadow(0 4px 0 rgba(61,43,31,.35))}
.nibs{display:flex;gap:5px}
.nibs button{
  width:32px;height:32px;border-radius:10px;border:3px solid var(--ink);background:#fff;cursor:pointer;
  display:grid;place-items:center;padding:0;box-shadow:2px 2px 0 var(--ink);
}
.nibs button i{display:block;border-radius:50%;background:var(--ink)}
.nibs button.on{background:var(--yellow)}

/* 넓은 화면: 스케치북은 왼쪽에 화면 높이만큼, 옆 판은 오른쪽에 위아래 꽉 차게 */
@media (min-width:760px){
  body:not(.title) .wrap{max-width:1040px}
  #sDraw,#sGuess{display:grid;grid-template-columns:minmax(0,1fr) 340px;grid-template-rows:auto 1fr;gap:6px 22px;align-items:stretch}
  #sDraw>.prev,#sGuess>.prev{grid-column:2;grid-row:1;transform:none;margin-bottom:6px}
  #sDraw>.sheet,#sGuess>.sheet{grid-column:1;grid-row:1/span 2;margin:0 auto;width:min(100%,calc(100vh - 300px))}
  #sDraw>.side,#sGuess>.side{grid-column:2;grid-row:2;margin-top:0}
  .side .submit{margin-top:auto}
}

''' + s[j:]

# 예전 그림판·넓은 화면 규칙 잔여물 정리
s = re.sub(r'\.pad canvas\{display:block;width:100%;height:100%;cursor:url\("data:image/svg\+xml,[^\n]*\n', '', s)
s = re.sub(r'\n/\* 넓은 화면: 그림판을 화면 높이에 맞추고 나머지를 옆에 세운다 \*/\n@media \(min-width:760px\)\{\n(?:  [^\n]*\n)+\}\n', '\n', s)

# ── 제시어 카드 → 색인 카드 ──
sub('''  border:3px solid var(--ink);border-radius:16px;background:var(--card);color:var(--ink);
  box-shadow:3px 3px 0 var(--ink);word-break:keep-all;line-height:1.3;
}''',
'''  border:3px solid var(--ink);border-radius:16px;color:var(--ink);
  background:var(--card) linear-gradient(90deg,transparent 0 13px,#f06595 13px 16px,transparent 16px),
             repeating-linear-gradient(180deg,transparent 0 21px,#dbe7f3 21px 22px);
  box-shadow:3px 3px 0 var(--ink);word-break:keep-all;line-height:1.3;
}''')

# ── 사람 이름표: 크레용 색 점 ──
sub('''    return '<span class="p' + (p.on ? '' : ' off') + (ok ? ' ok' : '') + '">' +
      '<i class="dot"></i>' + esc(p.name) +''',
'''    return '<span class="p' + (p.on ? '' : ' off') + (ok ? ' ok' : '') + '">' +
      '<i class="dot" style="background:' + (p.on ? PENS[r.players.indexOf(p) % PENS.length] : '') + '"></i>' + esc(p.name) +''')
sub('.who .p .dot{width:7px;height:7px;border-radius:50%;background:var(--green);flex:none}',
    '.who .p .dot{width:9px;height:9px;border-radius:50%;background:var(--green);flex:none;border:2px solid var(--ink)}')

# ── 기다리는 화면: 낙서가 그려지는 중 ──
sub('''  <section class="card hide" id="sWait">
    <p class="lede" id="waitLede"></p>''',
'''  <section class="card hide" id="sWait">
    <svg class="scribble" viewBox="0 0 300 60" fill="none" aria-hidden="true">
      <path d="M8 40c20-40 40 40 60 0s40-40 60 0 40 40 60 0 40-40 60 0 30 20 44 10" stroke="#e8590c" stroke-width="7" stroke-linecap="round"/>
    </svg>
    <p class="lede" id="waitLede"></p>''')
sub('.note{', '''.scribble{display:block;width:min(300px,80%);margin:4px auto 10px}
.scribble path{stroke-dasharray:520;stroke-dashoffset:520;animation:scrib 2.6s ease-in-out infinite}
@keyframes scrib{0%{stroke-dashoffset:520}55%{stroke-dashoffset:0}100%{stroke-dashoffset:-520}}
@media (prefers-reduced-motion:reduce){.scribble path{animation:none;stroke-dashoffset:0}}
.note{''')

# ── 공개: 테이프로 붙인 공책 장 ──
sub('.pg{border:3px solid var(--ink);border-radius:16px;background:var(--card);padding:11px 13px;box-shadow:3px 3px 0 var(--ink)}',
    '''.pg{position:relative;border:3px solid var(--ink);border-radius:16px;padding:16px 13px 11px;box-shadow:3px 3px 0 var(--ink);
  background:var(--card) radial-gradient(#ede3cf 1.1px,transparent 1.3px) 0 0/20px 20px}
.pg::before{content:"";position:absolute;top:-9px;left:50%;width:74px;height:18px;transform:translateX(-50%) rotate(-2deg);
  background:rgba(255,212,59,.78);border:2px solid rgba(61,43,31,.28);border-radius:2px}
.pg:nth-child(2n)::before{transform:translateX(-50%) rotate(2.5deg)}''')

# ── 1등: 색종이 ──
sub('''.win .said{font-size:clamp(24px,7vw,32px);font-weight:700;line-height:1.2;word-break:keep-all}''',
'''.win .said{font-size:clamp(24px,7vw,32px);font-weight:700;line-height:1.2;word-break:keep-all}
.confetti{position:relative;height:0;overflow:visible;pointer-events:none}
.confetti i{position:absolute;top:-12px;width:9px;height:16px;border-radius:2px;opacity:0;animation:fall 2.6s ease-in forwards}
@keyframes fall{0%{opacity:1;transform:translateY(0) rotate(0)}100%{opacity:0;transform:translateY(240px) rotate(540deg)}}
@media (prefers-reduced-motion:reduce){.confetti{display:none}}''')
sub("""      $('#top').innerHTML = top.length""",
    """      var confetti = '';
      if (top.length && S.confettiFor !== r.code + ':' + rev.of) {        // 판마다 한 번만 뿌린다
        S.confettiFor = r.code + ':' + rev.of;
        for (var ci = 0; ci < 18; ci++) confetti += '<i style="left:' + (4 + ci * 5.2) + '%;background:' + PENS[ci % PENS.length]
          + ';animation-delay:' + (ci % 6) * .13 + 's;transform:rotate(' + (ci * 37 % 90) + 'deg)"></i>';
        confetti = '<div class="confetti">' + confetti + '</div>';
      }
      $('#top').innerHTML = confetti + (top.length""")
sub("""        : '<p class="crown">아무도 안 뽑았습니다</p>';
      $('#top').querySelectorAll('canvas.shot')""",
    """        : '<p class="crown">아무도 안 뽑았습니다</p>');
      $('#top').querySelectorAll('canvas.shot')""")

# ── 종이 점무늬: 바탕에만. 획 데이터엔 손대지 않는다 ──
sub("""  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  g.lineCap = 'round'; g.lineJoin = 'round';
  var k = w / 1024;""",
"""  g.fillStyle = PAPER; g.fillRect(0, 0, w, w);
  var k = w / 1024;
  g.fillStyle = '#ece2cc';                       // 도화지 점무늬 — 바탕일 뿐, 획에는 안 들어간다
  for (var gy = 64; gy < 1024; gy += 64) for (var gx = 64; gx < 1024; gx += 64) g.fillRect(gx * k - .8, gy * k - .8, 1.6, 1.6);
  g.lineCap = 'round'; g.lineJoin = 'round';""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
