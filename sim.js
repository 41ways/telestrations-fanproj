// 서버를 띄워 놓고(npx wrangler dev --port 8787) 넷이 한 판을 끝까지 돈다 — 도중에 들어온 구경꾼, 투표 중 이탈, 「한 판 더」까지.
// node sim.js
const HOST = 'ws://127.0.0.1:8787';
const fail = m => { console.error('실패:', m); process.exit(1); };
const wait = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, what, ms = 20000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (fn()) return; await wait(60); } fail(what); };

const code = await fetch('http://127.0.0.1:8787/new').then(r => r.json()).then(d => d.code);
console.log('방', code);
const dood = () => [{ c: 2, w: 1, p: [100, 100, 500, 500, 900, 100] }];

function join(i, name) {
  const ws = new WebSocket(`${HOST}/room?code=${code}&pid=sim2-${i}&name=${name}`);
  const p = { i, name, ws, v: null, acted: new Set(), books: [] };
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.t === 'err') console.log('  [' + name + '] 오류:', m.m);
    if (m.t === 'book') p.books[m.b] = m;
    if (m.t === 'room') { p.v = m; act(p); }
  };
  return p;
}
function act(p) {
  const v = p.v;
  if (v.seat < 0) return;
  const key = v.phase + ':' + v.round + (v.phase === 'pick' && v.picked ? ':h' : '');
  if (v.done || p.acted.has(key)) return;
  if (v.phase === 'pick') {
    if (!v.picked) { p.acted.add(key); p.ws.send(JSON.stringify({ t: 'pick', i: 0 })); return; }
    if (!v.andDraw) return;
    p.acted.add(key); p.ws.send(JSON.stringify({ t: 'head', s: dood() }));
  } else if (v.phase === 'play') {
    p.acted.add(key);
    p.ws.send(JSON.stringify(v.kind === 'draw' ? { t: 'draw', s: dood() } : { t: 'guess', w: '해파리' + v.round }));
  }
}

const P = [0, 1, 2, 3].map(i => join(i, '사람' + i));
await until(() => P.every(p => p.v && p.v.players.length === 4), '넷 모이기');
const host = P.find(p => p.v.me === p.v.host);
host.ws.send(JSON.stringify({ t: 'start' }));
await until(() => host.v.phase !== 'lobby', '시작');

// 구경꾼 — 판 도중에 들어온다
const spec = join(9, '구경꾼');
await until(() => spec.v && spec.v.seat < 0 && spec.v.phase !== 'lobby', '구경꾼 들어오기');
if (!Array.isArray(spec.v.waiting) || spec.v.waiting.some(x => typeof x !== 'string' || !x.startsWith('sim2-'))) fail('waiting 이 표식이 아님 ' + JSON.stringify(spec.v.waiting));

await until(() => host.v.phase === 'reveal', '공개');
// 방장이 끝까지 넘긴다
for (let t = 0; t < 60 && host.v.phase === 'reveal'; t++) { host.ws.send(JSON.stringify({ t: 'turn', d: 1 })); await wait(40); }
await until(() => host.v.phase === 'vote', '투표');
if (host.v.reveal) console.log('  공개 끝 자리', JSON.stringify(host.v.reveal));

// 구경꾼이 표를 내 봐야 안 받는다
spec.ws.send(JSON.stringify({ t: 'vote', b: 0, i: 0 }));
await wait(200);
if (host.v.voted !== 0) fail('구경꾼 표가 들어감');

// 셋이 내고 하나는 나가 버린다 → 남은 사람이 다 냈으니 결과로 가야 한다
P[0].ws.send(JSON.stringify({ t: 'vote', b: 1, i: 1 }));
P[1].ws.send(JSON.stringify({ t: 'vote', b: 1, i: 1 }));
P[2].ws.send(JSON.stringify({ t: 'vote', b: 2, i: 0 }));
await until(() => host.v.voted === 3, '셋 냄');
if (host.v.voters !== 4) fail('voters 가 4 가 아님 ' + host.v.voters);
P[3].ws.close();
await until(() => spec.v.phase === 'done', '나간 뒤 결과로 (4초 유예)', 12000);
console.log('  1등', spec.v.top.map(t => t.by + ' ' + t.votes + '표').join(', '));
if (spec.v.top.length !== 1 || spec.v.top[0].votes !== 2) fail('1등이 이상함');

// 공책첩 청하기
spec.ws.send(JSON.stringify({ t: 'album' }));
await until(() => spec.books.filter(Boolean).length === 4, '공책첩 4권');
if (spec.books[0].pages.length !== 5) fail('4명이면 5쪽인데 ' + spec.books[0].pages.length);

// 한 판 더 → 구경꾼이 자리에 앉는다 (나간 사람은 대기실에서 빠진다)
const h2 = [P[0], P[1], P[2], spec].find(p => p.v.me === p.v.host);
h2.ws.send(JSON.stringify({ t: 'again' }));
await until(() => spec.v.phase === 'lobby' && spec.v.seat >= 0, '구경꾼 자리 앉기');
console.log('  대기실', spec.v.players.map(p => p.name).join(', '));
if (spec.v.players.length !== 4) fail('대기실 인원 ' + spec.v.players.length);
console.log('통과');
process.exit(0);
