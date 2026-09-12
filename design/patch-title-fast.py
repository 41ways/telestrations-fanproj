# -*- coding: utf-8 -*-
"""타이틀 연출을 빠르게, 그리고 다 그려진 글자가 둥둥 떠다니게. 글자를 하나씩 <g>로 묶어야 떠다닐 수 있다 (tspan 은 못 움직인다)."""
import io, os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

letters = [('텔', '#e03131', -4), ('레', '#e8590c', 3), ('스', '#ffd43b', -2), ('트', '#51cf66', 4), ('레', '#74c0fc', -3), ('이', '#f06595', 2), ('션', '#e8590c', -4)]
STEP, X0 = 71, 26
gs = ''.join(
    '<g class="l%d"><text class="sh" x="%d" y="85" rotate="%d">%s</text><text class="fc" x="%d" y="83" rotate="%d" style="stroke:%s;fill:%s">%s</text></g>'
    % (i + 1, X0 + i * STEP + 2, r, ch, X0 + i * STEP, r, c, c, ch) for i, (ch, c, r) in enumerate(letters))
i = s.index('      <svg class="ink"'); j = s.index('</svg>', i) + len('</svg>')
s = s[:i] + '      <svg class="ink" viewBox="0 0 540 112" font-size="70" aria-hidden="true">' + gs + '</svg>' + s[j:]

# ── CSS: 글자 규칙을 통째로 갈아끼운다 ──
i = s.index('/* 글자 테두리를 크레용으로 한 자씩 긋고(trace)'); j = s.index('.title .squig path{')
s = s[:i] + '''/* 글자마다: 테두리를 크레용으로 긋고(trace) → 속을 칠하며 테두리를 걷고(fillin) → 그림자가 붙고 → 둥둥 떠다닌다(bob) */
.title .ink .fc{stroke-width:6;stroke-linejoin:round;stroke-linecap:round;fill-opacity:0;
  stroke-dasharray:900;stroke-dashoffset:900;animation:trace .45s ease-out forwards,fillin .25s ease-out forwards}
.title .ink .l1 .fc{animation-delay:.05s,.5s}.title .ink .l2 .fc{animation-delay:.25s,.7s}.title .ink .l3 .fc{animation-delay:.45s,.9s}
.title .ink .l4 .fc{animation-delay:.65s,1.1s}.title .ink .l5 .fc{animation-delay:.85s,1.3s}.title .ink .l6 .fc{animation-delay:1.05s,1.5s}
.title .ink .l7 .fc{animation-delay:1.25s,1.7s}
@keyframes trace{to{stroke-dashoffset:0}}
@keyframes fillin{to{fill-opacity:1;stroke-width:0}}
.title .ink .sh{fill:var(--ink);opacity:0;animation:shade .3s ease-out 1.95s forwards}
@keyframes shade{to{opacity:1}}
.title .ink g[class^="l"]{transform-box:fill-box;transform-origin:50% 50%;animation:bob 2.6s ease-in-out infinite}
.title .ink .l1{animation-delay:2.1s}.title .ink .l2{animation-delay:2.22s}.title .ink .l3{animation-delay:2.34s}.title .ink .l4{animation-delay:2.46s}
.title .ink .l5{animation-delay:2.58s}.title .ink .l6{animation-delay:2.7s}.title .ink .l7{animation-delay:2.82s}
@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
''' + s[j:]
sub('  .title .ink .face tspan,.title .ink .shade,.title .squig path{animation:none;stroke-dashoffset:0;fill-opacity:1;opacity:1;stroke-width:0}',
    '  .title .ink .fc,.title .ink .sh,.title .squig path{animation:none;stroke-dashoffset:0;fill-opacity:1;opacity:1;stroke-width:0}\n  .title .ink g[class^="l"]{animation:none}')

# ── 뒤따르는 것들 당기기 ──
for a, b in [('animation:trace .5s ease-out 2.75s forwards', 'animation:trace .4s ease-out 2s forwards'),
             ('cubic-bezier(.2,1.4,.4,1) 2.95s', 'cubic-bezier(.2,1.4,.4,1) 2.15s'),
             ('animation:appear .01s linear 3.4s', 'animation:appear .01s linear 2.5s'),
             ('animation:trace .75s ease-out 3.4s forwards', 'animation:trace .6s ease-out 2.5s forwards'),
             ('animation:fillin .3s ease-out 4s forwards', 'animation:fillin .25s ease-out 3s forwards'),
             ('cubic-bezier(.2,1.6,.4,1) 4.1s', 'cubic-bezier(.2,1.6,.4,1) 3.1s'),
             ('cubic-bezier(.2,1.2,.4,1) 4.25s', 'cubic-bezier(.2,1.2,.4,1) 3.2s'),
             ('cubic-bezier(.2,1.2,.4,1) 4.37s', 'cubic-bezier(.2,1.2,.4,1) 3.3s'),
             ('cubic-bezier(.2,1.2,.4,1) 4.49s', 'cubic-bezier(.2,1.2,.4,1) 3.4s'),
             ('cubic-bezier(.2,1.2,.4,1) 4.6s', 'cubic-bezier(.2,1.2,.4,1) 3.5s'),
             ('setTimeout(fanfare, 4950);', 'setTimeout(fanfare, 3800);')]:
    sub(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', 'tspan' in s[s.index('<section class="title"'):s.index('</section>', s.index('<section class="title"'))])
