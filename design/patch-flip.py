# -*- coding: utf-8 -*-
"""공개 화면: 새 쪽이 스케치북 장 넘기듯 위에서 젖혀지며 나온다. 쪽 위엔 테이프 대신 스프링 고리."""
import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

sub('.chain{display:flex;flex-direction:column;gap:11px}',
    '.chain{display:flex;flex-direction:column;gap:14px;perspective:1100px}')
sub('''.pg:last-child{animation:rise .3s ease-out}
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.pg:last-child{animation:none}}''',
'''/* 막 넘긴 쪽이 스케치북 장처럼 위 고리를 축으로 젖혀 내려온다 */
.pg:last-child{animation:flip .62s cubic-bezier(.2,.75,.25,1);transform-origin:50% 0}
@keyframes flip{from{transform:rotateX(-96deg);opacity:.15}60%{opacity:1}to{transform:rotateX(0);opacity:1}}
@media (prefers-reduced-motion:reduce){.pg:last-child{animation:none}}''')
sub('''.pg::before{content:"";position:absolute;top:-9px;left:50%;width:74px;height:18px;transform:translateX(-50%) rotate(-2deg);
  background:rgba(255,212,59,.78);border:2px solid rgba(61,43,31,.28);border-radius:2px}
.pg:nth-child(2n)::before{transform:translateX(-50%) rotate(2.5deg)}''',
'''.pg::before{content:"";position:absolute;top:-13px;left:18px;right:18px;height:24px;pointer-events:none;
  background:radial-gradient(circle at 50% 50%,transparent 4.2px,var(--ink) 5px,var(--ink) 7.4px,transparent 8.2px) 0 0/30px 24px repeat-x}''')
sub('.pg{position:relative;border:3px solid var(--ink);border-radius:16px;padding:16px 13px 11px;',
    '.pg{position:relative;border:3px solid var(--ink);border-radius:14px;padding:18px 13px 11px;margin-top:6px;')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
