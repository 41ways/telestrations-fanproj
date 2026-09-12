# -*- coding: utf-8 -*-
"""타이틀 그림도 글자 다음에 차례로 올라온다: 공책 → 기린(그어지며) → ? → 크레용 셋 → 연필 → 빵빠레.
그리고 스케치북 고리가 종이 위를 덮지 않게 한다 (오른쪽 위가 잘려 보이던 것)."""
import io, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

spec = importlib.util.spec_from_file_location("mt", os.path.join(HERE, "make-title.py"))
mt = importlib.util.module_from_spec(spec); spec.loader.exec_module(mt)
INK, PAPER, YEL, GRN, RED = mt.INK, mt.PAPER, mt.YEL, mt.GRN, mt.RED

# ── 타이틀 그림을 조각마다 감싸서 다시 만든다 ──
rings = ''.join('<circle cx="%s" cy="33" r="6" fill="none" stroke="%s" stroke-width="3"/>' % (x, INK) for x in range(128, 280, 22))
art = ('<g class="a-book"><rect x="112" y="30" width="176" height="150" rx="10" fill="%s" stroke="%s" stroke-width="3.4" transform="rotate(-3 200 105)"/>%s</g>' % (PAPER, INK, rings)
     + '<g class="a-gir">' + mt.giraffe(150, 68, 1.05) + '</g>'
     + '<g class="a-q">' + mt.word(255, 130, "?", 64) + '</g>'
     + '<g class="a-c1">' + mt.crayon(20, 150, RED, -30) + '</g>'
     + '<g class="a-c2">' + mt.crayon(44, 165, YEL, -12) + '</g>'
     + '<g class="a-c3">' + mt.crayon(70, 176, GRN, 6) + '</g>'
     + '<g class="a-pen"><g transform="rotate(35 330 150)"><rect x="300" y="144" width="60" height="12" rx="3" fill="%s" stroke="%s" stroke-width="2.6"/><path d="M360 144l12 6-12 6z" fill="#fff6e0" stroke="%s" stroke-width="2.6"/></g></g>' % (YEL, INK, INK))
i = s.index('    <svg class="art"'); j = s.index('</svg>', i) + len('</svg>')
s = s[:i] + ('    <!-- 스케치북 한 권 — 조각마다 차례로 올라온다 -->\n'
             '    <svg class="art" viewBox="0 0 380 200" fill="none" aria-label="낙서와 물음표가 그려진 스케치북">\n      '
             + art + '\n    </svg>') + s[j:]

# ── 순서: 글자(0~2.1초) → 그림자·밑줄 → 공책 → 기린 → ? → 크레용 → 연필 → 빵빠레 ──
sub('.title .ink .l1{animation-delay:.05s,.45s}.title .ink .l2{animation-delay:.33s,.73s}.title .ink .l3{animation-delay:.61s,1.01s}\n'
    '.title .ink .l4{animation-delay:.89s,1.29s}.title .ink .l5{animation-delay:1.17s,1.57s}.title .ink .l6{animation-delay:1.45s,1.85s}\n'
    '.title .ink .l7{animation-delay:1.73s,2.13s}',
    '.title .ink .l1{animation-delay:.05s,.4s}.title .ink .l2{animation-delay:.29s,.64s}.title .ink .l3{animation-delay:.53s,.88s}\n'
    '.title .ink .l4{animation-delay:.77s,1.12s}.title .ink .l5{animation-delay:1.01s,1.36s}.title .ink .l6{animation-delay:1.25s,1.6s}\n'
    '.title .ink .l7{animation-delay:1.49s,1.84s}')
sub('.title .ink .shade{fill:var(--ink);opacity:0;animation:shade .4s ease-out 2.35s forwards}',
    '.title .ink .shade{fill:var(--ink);opacity:0;animation:shade .4s ease-out 2.05s forwards}')
sub('.title .squig path{stroke-dasharray:300;stroke-dashoffset:300;animation:trace .5s ease-out 2.4s forwards}',
    '''.title .squig path{stroke-dasharray:300;stroke-dashoffset:300;animation:trace .5s ease-out 2.1s forwards}

/* 그림 조각들 — 공책이 툭 올라오고, 기린이 그어지고, ? 가 튀고, 크레용이 하나씩, 연필이 마지막에 */
.title .art g[class^="a-"]{transform-box:fill-box;transform-origin:50% 100%;opacity:0;animation-fill-mode:forwards}
.title .art .a-book{animation:popup .5s cubic-bezier(.2,1.4,.4,1) 2.3s}
.title .art .a-gir{animation:appear .01s linear 2.75s}
.title .art .a-gir path,.title .art .a-gir circle{stroke-dasharray:260;stroke-dashoffset:260;animation:trace .75s ease-out 2.75s forwards}
.title .art .a-gir circle{fill-opacity:0;animation:fillin .3s ease-out 3.35s forwards}
.title .art .a-q{transform-origin:50% 50%;animation:popup .35s cubic-bezier(.2,1.6,.4,1) 3.45s}
.title .art .a-c1{animation:slide-l .35s cubic-bezier(.2,1.2,.4,1) 3.6s}
.title .art .a-c2{animation:slide-l .35s cubic-bezier(.2,1.2,.4,1) 3.72s}
.title .art .a-c3{animation:slide-l .35s cubic-bezier(.2,1.2,.4,1) 3.84s}
.title .art .a-pen{animation:slide-r .4s cubic-bezier(.2,1.2,.4,1) 3.95s}
@keyframes popup{from{opacity:0;transform:translateY(26px) scale(.7)}to{opacity:1;transform:none}}
@keyframes appear{to{opacity:1}}
@keyframes slide-l{from{opacity:0;transform:translateX(-46px) rotate(-14deg)}to{opacity:1;transform:none}}
@keyframes slide-r{from{opacity:0;transform:translateX(46px) rotate(14deg)}to{opacity:1;transform:none}}''')
sub('''  .title .ink tspan,.title .ink .shade,.title .squig path{animation:none;stroke-dashoffset:0;fill-opacity:1;opacity:1}''',
    '''  .title .ink tspan,.title .ink .shade,.title .squig path{animation:none;stroke-dashoffset:0;fill-opacity:1;opacity:1}
  .title .art g[class^="a-"],.title .art .a-gir path,.title .art .a-gir circle{animation:none;opacity:1;stroke-dashoffset:0;fill-opacity:1}''')
sub('setTimeout(fanfare, 2650);', 'setTimeout(fanfare, 4300);')

# ── 고리가 종이를 덮지 않게: 고리는 종이 위에 딱 붙고, 쪽 안 내용은 고리 아래로 ──
sub('.rings{height:24px;margin:0 20px -6px;position:relative;z-index:3;',
    '.rings{height:24px;margin:0 20px -2px;position:relative;z-index:3;')
sub('.book .rings{margin-bottom:-8px}', '.book .rings{margin-bottom:-2px}')
sub('.pg{position:relative;border:3px solid var(--ink);border-radius:14px;padding:14px 13px 11px;',
    '.pg{position:relative;border:3px solid var(--ink);border-radius:14px;padding:12px 13px 11px;')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
