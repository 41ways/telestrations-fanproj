# -*- coding: utf-8 -*-
"""공개 화면을 스케치북으로: 한 쪽씩 보여 주고, 다음을 누르면 지금 쪽이 위로 젖혀져 넘어간다. 지난 쪽은 아래에 작게."""
import io, os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 마크업 ──
sub('''    <div class="chain" id="chain"></div>
    <div class="row" id="revBtns">''',
'''    <div class="book"><div class="rings"></div><div class="stage" id="stage"></div></div>
    <div class="row" id="revBtns">''')
sub('''    <p class="note" id="revNote"></p>
  </section>

  <!-- 끝 -->''',
'''    <p class="note" id="revNote"></p>
    <div class="past" id="past"></div>
  </section>

  <!-- 끝 -->''')

# ── CSS ──
i = s.index('/* ── 공개 ── */'); j = s.index('/* ── 1등 ── */')
s = s[:i] + '''/* ── 공개 — 스케치북 한 권. 지금 쪽 하나가 크게, 다음을 누르면 위 고리를 축으로 젖혀 올라가고 그 밑 쪽이 드러난다 ── */
.book{position:relative;margin-top:10px}
.stage{position:relative;perspective:1200px;min-height:80px}
.pg{position:relative;border:3px solid var(--ink);border-radius:14px;padding:14px 13px 11px;box-shadow:5px 5px 0 var(--yellow);
  background:var(--card) radial-gradient(#ede3cf 1.1px,transparent 1.3px) 0 0/20px 20px}
.stage .pg.leaf{position:absolute;left:0;right:0;top:0;transform-origin:50% 0;z-index:2;pointer-events:none;
  animation:flipup .6s cubic-bezier(.5,0,.8,.4) forwards}
@keyframes flipup{0%{transform:rotateX(0)}100%{transform:rotateX(-118deg);opacity:0}}
.stage .pg.now{animation:settle .35s ease-out}
@keyframes settle{from{transform:translateY(6px)}to{transform:none}}
@media (prefers-reduced-motion:reduce){.stage .pg.leaf{animation:none;display:none}.stage .pg.now{animation:none}}
.pg .by{display:flex;align-items:center;gap:8px;font-size:15px;color:var(--dim);margin-bottom:6px}
.pg .by .star{margin-left:auto;font:inherit;font-size:19px;border:0;background:none;cursor:pointer;color:var(--dim);padding:0 4px}
.pg .by .star.on{color:var(--orange)}
.pg .said{font-size:clamp(22px,6vw,28px);font-weight:700;line-height:1.2;word-break:keep-all}
/* 그림을 보여 주는 자리. 폭을 여기서 못 박아 둬야 한다 — 캔버스는 폭이 없으면
   다시 그릴 때마다 제 속성값을 따라 한없이 커진다 */
.shot{width:100%;aspect-ratio:1;border-radius:12px;background:var(--card);border:3px solid var(--ink);display:block}
.pg.first{background-color:var(--yellow)}
.pg.last{background-color:var(--green)}
.pg.miss .said{color:var(--dim)}

/* 지난 쪽들 — 아래에 작게 쌓인다 */
.past{display:flex;flex-direction:column;gap:9px;margin-top:16px}
.past .pg{padding:8px 11px;box-shadow:3px 3px 0 var(--ink);display:grid;grid-template-columns:1fr auto;gap:2px 12px;align-items:center}
.past .pg .by{margin:0;grid-column:1/-1}
.past .pg .said{font-size:19px}
.past .pg .shot{width:150px;border-width:2px}
@media (min-width:760px){
  #sReveal{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:6px 22px;align-items:start}
  #sReveal>.book{grid-column:1;grid-row:1/span 3;width:min(100%,calc(100vh - 300px));margin:0 auto}
  #sReveal>#revLede,#sReveal>#revBtns,#sReveal>#revNote{grid-column:2}
  #sReveal>.past{grid-column:2;margin-top:6px;max-height:calc(100vh - 380px);overflow:auto;padding:4px}
}

''' + s[j:]
s = re.sub(r'\.chain\{[^}]*\}\n', '', s)
s = s.replace('.pad.view{box-shadow:6px 6px 0 var(--blue)}', '.pad.view{box-shadow:6px 6px 0 var(--blue)}\n.book .rings{margin-bottom:-8px}')

# ── JS: 사슬 그리던 자리 → 스케치북 무대 ──
i = s.index("    /* 별만 눌린 거라면 쪽을 다시 만들지 않는다")
j = s.index("    return;\n  }\n}\n\nfunction waitAt", i)
s = s[:i] + '''    /* 스케치북 무대: 지금 쪽 하나. 같은 공책에서 한 쪽 앞으로 갔으면 지금 쪽을 위로 젖혀 올리고 새 쪽을 그 밑에 깐다 */
    var stage = $('#stage'), cur = r.phase + ':' + rev.b + ':' + rev.i;
    if (S.stageFor !== cur) {
      var was = stage.querySelector('.pg.now');
      var flip = was && S.stageBook === rev.b && rev.i === S.stageIdx + 1 && r.phase === 'reveal';
      if (flip) {
        was.classList.remove('now'); was.classList.add('leaf');
        was.addEventListener('animationend', function(){ was.remove(); });
        setTimeout(function(){ if (was.parentNode) was.remove(); }, 900);
      } else {
        stage.innerHTML = '';
      }
      var pg = (r.pages || [])[rev.i];
      if (pg) stage.insertAdjacentHTML('afterbegin', pageHtml(pg, rev.i, 'now' + (r.phase === 'done' && rev.i > 0 ? ' last' : '')));
      stage.querySelectorAll('.pg.now canvas.shot').forEach(function(cv){ paint(cv, (r.pages[+cv.dataset.k] || {}).strokes); });
      S.stageFor = cur; S.stageBook = rev.b; S.stageIdx = rev.i;

      var past = $('#past');
      past.innerHTML = (r.pages || []).slice(0, rev.i).map(function(p2, k){ return p2 ? pageHtml(p2, k, 'mini') : ''; }).reverse().join('');
      past.querySelectorAll('canvas.shot').forEach(function(cv){ paint(cv, (r.pages[+cv.dataset.k] || {}).strokes); });
    }
    document.querySelectorAll('#sReveal button.star').forEach(function(b){
      var k = +b.dataset.k, pg2 = (r.pages || [])[k] || {};
      var on = r.myVote === rev.b + ':' + k;
      b.classList.toggle('on', on);
      b.textContent = (on ? '★' : '☆') + (pg2.votes ? ' ' + pg2.votes : '');
    });
    $('#sReveal').onclick = function(e){
      var b = e.target.closest('button.star'); if (!b) return;
      send({ t:'vote', b:rev.b, i:+b.dataset.k });      // 한 사람이 한 표. 다시 누르면 거둔다
    };
''' + s[j:]

sub('''function waitAt(){''',
'''/** 공책 한 쪽 — 위에 누가 뭘 했는지, 아래에 말이나 그림 */
function pageHtml(pg, k, cls){
  var cap = k === 0 ? '고른 말' : (pg.kind === 'draw' ? '그림' : '추측');
  return '<div class="pg ' + cls + (k === 0 ? ' first' : '') + (pg.word === '…' ? ' miss' : '') + '">' +
    '<div class="by"><span>' + cap + ' · ' + esc(pg.by) + '</span><button class="star" data-k="' + k + '"></button></div>' +
    (pg.kind === 'draw' ? '<canvas class="shot" data-k="' + k + '"></canvas>' : '<div class="said">' + esc(pg.word) + '</div>') +
    '</div>';
}

function waitAt(){''')

# 크기가 바뀌면 무대도 다시
s = s.replace("if (r && (r.phase === 'reveal' || r.phase === 'done')) { S.chainSig = null; draw(); }",
              "if (r && (r.phase === 'reveal' || r.phase === 'done')) { S.stageFor = null; draw(); }")
assert '#chain' not in s, '#chain 참조가 남았다'
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
