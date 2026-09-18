/**
 * 서버가 실제로 도는지 밖에서 두들겨 본다.  node smoke.js [주소]
 *
 *   node smoke.js                         http://127.0.0.1:8787 (npx wrangler dev)
 *   node smoke.js https://telestrations.41ways.workers.dev
 *
 * 스케치퀴즈 한 차례를 끝까지 돌린다 — 방 만들기, 목록에 뜨는지, 제시어 고르기,
 * 획 중계, 맞히기와 점수, 힌트가 새지 않는지, 나가기까지.
 */
const base = (process.argv[2] || 'http://127.0.0.1:8787').replace(/\/+$/, '');
const wsBase = base.replace(/^http/, 'ws');
const sleep = ms => new Promise(r => setTimeout(r, ms));
let bad = 0;
const ok = (c, m) => { console.log((c ? '  ✓ ' : '  ✗ ') + m); if (!c) bad++; };

/** 사람 하나 — 붙어서 오는 소식을 쌓아 둔다 */
function seat(code, name, make) {
  const pid = 'smoke-' + name + '-' + Date.now() + Math.random().toString(36).slice(2, 6);
  const url = `${wsBase}/room?code=${code}&pid=${pid}&name=${encodeURIComponent(name)}`
    + (make ? `&game=${make}` : '');
  const me = { pid, name, v: null, chat: [], ink: 0, open: false };
  const sock = new WebSocket(url);
  me.sock = sock;
  sock.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.t === 'room') me.v = m;
    else if (m.t === 'err') { me.err = m.m; console.log('    (' + name + ' 에게 온 말: ' + m.m + ')'); }
    else if (m.t === 'chat') me.chat.push(m);
    else if (m.t === 'ink' || m.t === 'ink0') me.ink += m.s ? (m.s.length || 1) : 0;
  };
  sock.onopen = () => { me.open = true; };
  me.say = o => sock.readyState === 1 && sock.send(JSON.stringify(o));
  return me;
}
const till = async (f, ms = 6000) => {
  for (let i = 0; i < ms / 100; i++) { if (f()) return true; await sleep(100); }
  return false;
};

const run = async () => {
  console.log('스케치퀴즈');
  const { code } = await fetch(base + '/new').then(r => r.json());
  const a = seat(code, '가', 'quiz');
  await till(() => a.v);
  const b = seat(code, '나');
  await till(() => a.v && a.v.players.length === 2);
  ok(a.v.game === 'quiz' && a.v.min === 2, '스케치퀴즈 방이 열린다 (' + code + ')');

  const list = await fetch(base + '/rooms').then(r => r.json());
  ok(list.rooms.some(x => x.code === code && x.game === 'quiz'), '열린 방 목록에 뜬다');

  a.say({ t: 'start' });
  ok(await till(() => a.v.phase === 'qpick'), '시작하면 제시어를 고른다');

  const drawer = a.v.q.mine ? a : b, guess = drawer === a ? b : a;
  drawer.say({ t: 'qpick', i: 1 });
  ok(await till(() => drawer.v.phase === 'qplay'), '고르면 그리기로 넘어간다');

  const word = drawer.v.q.word;
  ok(!!word, '그리는 사람은 제시어를 본다 (' + word + ')');
  ok(!guess.v.q.word && /○/.test(guess.v.q.hint), '맞히는 사람에게는 글자 수만 보인다 (' + guess.v.q.hint + ')');

  drawer.say({ t: 'ink', s: { c: 1, w: 1, p: [100, 100, 500, 500, 900, 200] } });
  ok(await till(() => guess.ink > 0), '획이 곧바로 건너간다');

  guess.say({ t: 'say', w: '엉뚱한 답' });
  await sleep(300);
  ok(guess.chat.some(c => c.text === '엉뚱한 답'), '틀린 답은 그냥 한마디로 뜬다');

  drawer.say({ t: 'say', w: word });
  await sleep(300);
  ok(!guess.chat.some(c => c.text === word), '그리는 사람이 정답을 쳐도 안 퍼진다');

  guess.say({ t: 'say', w: word });
  ok(await till(() => guess.v.q.iSolved), '맞히면 맞힌 사람으로 잡힌다');
  const mine = guess.v.q.scores.find(x => x.pid === guess.pid);
  const his = guess.v.q.scores.find(x => x.pid === drawer.pid);
  ok(mine.score > 0 && his.score > 0, '맞힌 사람과 그린 사람 모두 점수를 받는다 (' + mine.score + ' · ' + his.score + ')');
  ok(await till(() => guess.v.phase === 'qend'), '다 맞히면 차례가 끝난다');
  ok(guess.v.q.word === word, '차례가 끝나면 정답이 보인다');
  ok(await till(() => guess.v.phase === 'qpick' && guess.v.q.turn === 2, 9000), '다음 차례로 넘어간다');

  guess.say({ t: 'say', w: '이제 알겠지' });
  await sleep(300);
  ok(drawer.chat.some(c => c.text === '이제 알겠지'), '맞힌 사람 말은 그리는 사람에게 간다');

  console.log('나가기');
  guess.say({ t: 'leave' });
  ok(await till(() => drawer.v.players.length === 1), '나가면 자리가 빈다');
  a.sock.close(); b.sock.close();
  await sleep(300);

  console.log('텔레스트레이션');
  const t = await fetch(base + '/new').then(r => r.json());
  const p = [];
  for (let i = 0; i < 4; i++) { p.push(seat(t.code, '사람' + i, i ? null : 'tele')); await sleep(120); }
  ok(await till(() => p[0].v && p[0].v.players.length === 4), '넷이 모인다');
  p[0].say({ t: 'start' });
  ok(await till(() => p[0].v.phase === 'pick'), '시작하면 제시어를 고른다');
  p.forEach(x => x.say({ t: 'pick', i: 0 }));
  await sleep(400);
  p.forEach(x => x.say({ t: 'head', s: [{ c: 1, w: 1, p: [10, 10, 900, 900] }] }));
  ok(await till(() => p[0].v.phase === 'play' && p[0].v.round === 2), '넷이 다 내면 다음 라운드');
  /* 채팅은 두 게임 다 되고, 그림 중계 같은 퀴즈 전용 말은 안 먹는다 */
  p[1].say({ t: 'say', w: '여기서 떠들기' });
  p[1].say({ t: 'ink', s: { c: 1, w: 1, p: [1, 1, 900, 900] } });
  await sleep(400);
  ok(p[0].chat.some(c => c.text === '여기서 떠들기'), '텔레스트레이션 방에서도 채팅이 된다');
  ok(!p[0].ink, '텔레스트레이션 방에서는 퀴즈 그림 중계가 안 먹는다');
  p.forEach(x => x.sock.close());

  console.log(bad ? bad + '군데 어긋납니다' : '모두 통과');
  process.exit(bad ? 1 : 0);
};
run().catch(e => { console.error('터졌습니다:', e); process.exit(1); });
