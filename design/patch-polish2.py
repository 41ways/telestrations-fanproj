# -*- coding: utf-8 -*-
"""두 번째 꾸밈·수정 판: 라운드 진행 크레용 띠, 1등 왕관, 빈 안내문 자리 정리."""
import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 머리글 아래 라운드 진행 띠: 라운드 수만큼 크레용 토막, 지난 것은 색이 칠해진다 ──
sub('''      <span class="clock num hide" id="clock">0</span>
    </div>''',
'''      <span class="clock num hide" id="clock">0</span>
    </div>
    <div class="prog hide" id="prog" aria-hidden="true"></div>''')
sub('''.clock.hot{background:var(--red);color:#fff;animation:shake .5s infinite}''',
'''.prog{display:flex;gap:5px;margin-top:8px}
.prog i{flex:1 1 0;height:9px;border:2px solid var(--ink);border-radius:5px;background:#fff;box-shadow:2px 2px 0 var(--ink)}
.prog i.did{background:var(--green)}
.prog i.now{background:var(--yellow)}
body:not(.at-title) .prog{margin:6px 0 0}
.clock.hot{background:var(--red);color:#fff;animation:shake .5s infinite}''')
sub("""  $('#step').textContent = r.round + ' / ' + r.rounds + '라운드';""",
"""  $('#step').textContent = r.round + ' / ' + r.rounds + '라운드';
  var prog = '';
  for (var pi = 1; pi <= r.rounds; pi++) prog += '<i class="' + (pi < r.round ? 'did' : pi === r.round ? 'now' : '') + '"></i>';
  $('#prog').innerHTML = prog;
  $('#prog').classList.toggle('hide', !(r.phase === 'pick' || r.phase === 'play'));""")
sub("""  $('#step').classList.toggle('hide', !r || r.phase === 'lobby');""",
"""  $('#step').classList.toggle('hide', !r || r.phase === 'lobby');
  if (!r || r.phase === 'lobby') $('#prog').classList.add('hide');""")

# ── 1등에 크레용 왕관 ──
sub("""        ? '<p class="crown">' + (top.length > 1 ? '공동 <b>1등</b>' : '<b>1등</b>') + '</p>'""",
"""        ? '<p class="crown"><svg viewBox="0 0 40 30" width="34" height="26" aria-hidden="true"><path d="M4 26h32l3-16-9 7-10-13-10 13-9-7z" fill="#ffd43b" stroke="#3d2b1f" stroke-width="2.6" stroke-linejoin="round"/><circle cx="20" cy="18" r="2.4" fill="#f06595"/><circle cx="10" cy="20" r="1.8" fill="#74c0fc"/><circle cx="30" cy="20" r="1.8" fill="#51cf66"/></svg>'
          + (top.length > 1 ? '공동 <b>1등</b>' : '<b>1등</b>') + '</p>'""")

# ── 빈 안내문이 자리만 차지하지 않게 ──
sub(""".lede{font-size:17px;color:var(--dim);margin:0 0 12px}""", """.lede{font-size:17px;color:var(--dim);margin:0 0 12px}\n.lede:empty,.note:empty{display:none}""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
