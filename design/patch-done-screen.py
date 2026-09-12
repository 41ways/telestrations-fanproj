# -*- coding: utf-8 -*-
"""휠 스크롤 복구, 1등은 제 화면으로, 팬 프로젝트 문구는 형제 프로젝트(다빈치코드·허브) 문구 그대로."""
import io, os, re
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'index.html')
s = io.open(p, encoding='utf-8').read()
def sub(a, b):
    global s
    assert a in s, '못 찾음: ' + a[:70]
    s = s.replace(a, b, 1)

# ── 1. 휠 스크롤: html·body 둘 다에 overflow-x:hidden 을 두면 크롬에서 휠이 죽는다. 햇살이 사라졌으니 둘 다 뺀다 ──
sub('html{-webkit-text-size-adjust:100%;overflow-x:hidden}\nbody{overflow-x:hidden}', 'html{-webkit-text-size-adjust:100%}')
sub('  overscroll-behavior-y:contain;\n', '')

# ── 2. 1등은 제 화면. 공책은 「공책 다시 보기」로 따로 ──
sub('''    <div class="row"><button class="btn go big" id="bAgain">한 판 더</button></div>
    <p class="note" id="doneNote"></p>
  </section>''',
'''    <div class="row"><button class="btn go big" id="bAgain">한 판 더</button></div>
    <div class="row"><button class="btn sm" id="bPeek">공책 다시 보기</button></div>
    <p class="note" id="doneNote"></p>
  </section>''')
sub('''    <div class="row" id="revBtns">
      <button class="btn sm" id="bPrev">뒤로</button>
      <button class="btn go" id="bNext">다음</button>
    </div>''',
'''    <div class="row" id="revBtns">
      <button class="btn sm" id="bPrev">뒤로</button>
      <button class="btn go" id="bNext">다음</button>
    </div>
    <div class="row hide" id="peekBtns"><button class="btn sm" id="bWinner">1등 보기</button></div>''')
sub("""$('#bAgain').onclick = function(){ send({ t:'again' }); };""",
    """$('#bAgain').onclick = function(){ send({ t:'again' }); };
$('#bPeek').onclick = function(){ S.peek = true; draw(); };      // 끝난 뒤 공책을 다시 넘겨 본다
$('#bWinner').onclick = function(){ S.peek = false; draw(); };""")
sub("""    } else {
      show('#sReveal', '#sDone');                 // 공책을 그대로 두고 그 밑에 점수를 붙인다
      $('#revNote').textContent = r.myVote ? '' : '제일 마음에 드는 걸 고르세요!';""",
"""    } else {
      /* 끝: 1등을 제 화면에 크게. 공책은 「공책 다시 보기」로 — 아래에 이어 붙이면 스크롤을 하게 된다 */
      show(S.peek ? '#sReveal' : '#sDone');
      $('#peekBtns').classList.remove('hide');
      $('#revNote').textContent = r.myVote ? '' : '제일 마음에 드는 걸 고르세요!';""")
sub("""    if (r.phase === 'reveal') {
      show('#sReveal');""",
"""    if (r.phase === 'reveal') {
      S.peek = false;
      $('#peekBtns').classList.add('hide');
      show('#sReveal');""")
# 방이 바뀌거나 대기실로 가면 peek 도 푼다
sub("""  if (r.phase === 'lobby') {
    show('#sLobby');""", """  if (r.phase === 'lobby') {
    S.peek = false;
    show('#sLobby');""")
# 넓은 화면에서 끝 화면은 좁게(1등 한 장이면 충분하다) — 공책 다시 볼 때만 넓게
sub("""  document.body.classList.toggle('wide', !!r && (r.phase === 'play' || r.phase === 'reveal' || r.phase === 'done'));""",
    """  document.body.classList.toggle('wide', !!r && (r.phase === 'play' || r.phase === 'reveal' || (r.phase === 'done' && S.peek)));""")
sub("""  document.body.classList.toggle('mid', (!r && S.entered) || (!!r && (r.phase === 'lobby' || r.phase === 'pick')));""",
    """  document.body.classList.toggle('mid', (!r && S.entered) || (!!r && (r.phase === 'lobby' || r.phase === 'pick' || (r.phase === 'done' && !S.peek))));""")

# ── 3. 팬 프로젝트 문구 — 다빈치코드·허브와 같은 말로, 규칙 안에 ──
s = re.sub(r'  <p class="legal">[^\n]*</p>\n\n', '', s)
s = re.sub(r'\.legal\{[^}]*\}\nbody\.wide \.legal\{display:none\}\n', '', s)
sub('''        <li>보드게임 <b>Telestrations</b>(The Op)를 웹으로 옮긴 팬 프로젝트입니다.</li>
      </ul>''',
'''      </ul>
      <p class="disclaimer">
        이 프로젝트는 보드게임 『텔레스트레이션』을 구현한 학습 목적의 비공식 팬 프로젝트입니다.<br>
        본 프로젝트는 비영리이며, 어떠한 수익도 발생시키지 않습니다.<br>
        『텔레스트레이션』의 명칭 및 관련 상표에 대한 모든 권리는 원권리자에게 있습니다.<br>
        원권리자의 요청이 있을 경우 즉시 프로젝트를 비공개 전환 또는 삭제하겠습니다.<br>
        문의: <a href="mailto:gyolno2@naver.com">gyolno2@naver.com</a>
      </p>''')
sub('''.rules{font-size:16px;color:var(--dim);padding-left:20px;margin:8px 0 0}''',
    '''.rules{font-size:16px;color:var(--dim);padding-left:20px;margin:8px 0 0}
.disclaimer{font-size:13px;color:#a0917a;line-height:1.6;margin:14px 0 0;padding-top:12px;border-top:2px dotted #e0d2b8}
.disclaimer a{color:inherit}''')

io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', 'legal' in s, 'overflow-x' in s)
