# -*- coding: utf-8 -*-
"""가독성: 선을 얇게·간격을 넓게, 입력창과 단추를 확실히 다르게, 판은 좁은 화면일 땐 가운데 모으고, 팬 프로젝트 문구."""
import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 선은 얇게, 간격은 넓게 ──
sub('''.card{
  background:#fff radial-gradient(#ede3cf 1.1px,transparent 1.3px) 0 0/20px 20px;border:4px solid var(--ink);border-radius:20px;
  padding:16px;margin-bottom:14px;box-shadow:5px 5px 0 var(--ink);
}''',
'''.card{
  background:#fff radial-gradient(#ede3cf 1.1px,transparent 1.3px) 0 0/20px 20px;border:3px solid var(--ink);border-radius:20px;
  padding:20px;margin-bottom:16px;box-shadow:4px 4px 0 var(--ink);
}''')
sub('''label{display:block;font-size:16px;font-weight:700;color:var(--dim);margin:0 0 4px}''',
    '''label{display:block;font-size:15px;font-weight:700;color:var(--ink);margin:18px 0 7px}\nlabel:first-child{margin-top:0}''')
# 입력창: 단추와 딴판으로 — 얇은 연갈색 선, 그림자 없음, 안으로 살짝 들어간 느낌, 왼쪽 정렬
sub('''input[type=text]{
  width:100%;font:inherit;font-size:18px;font-weight:700;padding:9px 12px;border-radius:12px;
  border:3px solid var(--ink);background:var(--paper);color:var(--ink);
}
input[type=text]:focus{outline:3px solid var(--orange);outline-offset:1px}
input.code{text-transform:uppercase;letter-spacing:.3em;font-size:24px;text-align:center}''',
'''input[type=text]{
  width:100%;font:inherit;font-size:19px;font-weight:400;padding:12px 14px;border-radius:10px;
  border:2px solid #cdbc9c;background:#fffdf8;color:var(--ink);box-shadow:inset 0 2px 0 rgba(61,43,31,.06);
}
input[type=text]::placeholder{color:#b8a98c}
input[type=text]:focus{outline:0;border-color:var(--orange);box-shadow:inset 0 2px 0 rgba(61,43,31,.06),0 0 0 3px rgba(232,89,12,.18)}
input.code{text-transform:uppercase;letter-spacing:.28em;font-size:24px;font-weight:700;text-align:center}''')
sub('''.row{display:flex;gap:9px;margin-top:11px;flex-wrap:wrap}''', '''.row{display:flex;gap:12px;margin-top:14px;flex-wrap:wrap}''')
sub('''.or{text-align:center;font-size:16px;color:var(--dim);margin:14px 0 10px}''', '''.or{text-align:center;font-size:15px;color:var(--dim);margin:22px 0 4px}''')
# 단추: 꽉 차게, 선은 3px 그대로, 큰 단추는 그림자 4px
sub('''.btn.big{font-size:24px;padding:12px;border-width:4px;box-shadow:5px 5px 0 var(--ink);border-radius:16px}''',
    '''.btn.big{font-size:23px;padding:13px;border-width:3px;box-shadow:4px 4px 0 var(--ink);border-radius:14px;width:100%}''')
sub('''.title .start{margin-top:26px;width:auto;min-width:220px;padding:13px 48px}''',
    '''.title .start{margin-top:26px;width:100%;max-width:520px;padding:13px 48px}''')

# ── 판 폭: 그리기·맞히기·공개만 넓게. 나머지는 560 에 두고 세로 가운데로 ──
sub('''  body:not(.at-title) .wrap{max-width:1040px}''', '''  body.wide .wrap{max-width:1040px}''')
sub('''  body:not(.at-title) .card{padding:14px}''', '''  body.wide .card{padding:14px}''')
sub('''.wrap{max-width:560px;margin:0 auto}''',
'''.wrap{max-width:560px;margin:0 auto}
/* 짧은 화면(문간·대기실·고르기·기다림)은 위에 몰지 않고 세로 가운데에 앉힌다 */
body.mid .wrap{min-height:calc(100vh - 52px);display:flex;flex-direction:column;justify-content:center}
body.mid header{flex:none}
body.mid .card{flex:none}''')
sub("""  document.body.classList.toggle('at-title', !r && !S.entered);   // 타이틀에서는 머리글을 숨긴다 — 큰 제목이 대신 선다""",
    """  document.body.classList.toggle('at-title', !r && !S.entered);   // 타이틀에서는 머리글을 숨긴다 — 큰 제목이 대신 선다
  document.body.classList.toggle('wide', !!r && (r.phase === 'play' || r.phase === 'reveal' || r.phase === 'done'));
  document.body.classList.toggle('mid', (!r && S.entered) || (!!r && (r.phase === 'lobby' || r.phase === 'pick')));""")

# ── 팬 프로젝트 문구 ──
sub('''  <section class="card" id="rulesCard">''',
'''  <p class="legal">비공식 팬 프로젝트입니다. Telestrations는 The Op의 등록 상표이며, 이 사이트는 The Op와 아무 관련이 없습니다.</p>

  <section class="card" id="rulesCard">''')
sub('''.rules{font-size:16px;color:var(--dim);padding-left:20px;margin:8px 0 0}''',
    '''.legal{font-size:13px;color:#a0917a;text-align:center;margin:4px 0 14px;line-height:1.5}
body.wide .legal{display:none}
.rules{font-size:16px;color:var(--dim);padding-left:20px;margin:8px 0 0}''')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
