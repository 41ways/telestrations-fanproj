/**
 * 혼자 확인할 때 옆자리를 채워 주는 봇.  node bots.js <방번호> [몇명] [주소]
 *
 *   node bots.js ABCD        봇 셋이 들어온다 (나까지 넷이 되어 바로 시작할 수 있다)
 *   node bots.js ABCD 5      봇 다섯
 *   node bots.js ABCD 2 https://telestrations.41ways.workers.dev
 *   node bots.js ABCD 3 --pass      그림은 안 그리고 빈 쪽으로만 넘긴다 (흐름만 빨리 볼 때)
 *
 * 봇은 제시어를 고르고, 그리고, 맞히고, 공개 때 아무 쪽에나 별을 준다. 한 판 더 해도 계속 따라온다.
 * 사람이 먼저 방을 만들었으면 사람이 방장이다 — 시작과 공개 넘기기는 사람 몫.
 * 봇이 먼저 붙어 방장이 되어 버렸으면 봇이 알아서 시작하고 넘긴다.
 */
const argv = process.argv.slice(2).filter(a => a !== '--pass');
const blank = process.argv.includes('--pass');     // 그림은 안 그리고 빈 쪽으로 넘긴다
const code = (argv[0] || '').toUpperCase();
const many = Math.max(1, Math.min(9, +(argv[1] || 3)));
const base = (argv[2] || 'http://127.0.0.1:8787').replace(/\/+$/, '');

if (!/^[A-HJ-NP-Z2-9]{4}$/.test(code)) {
  console.error('방 번호 네 글자를 주세요.  예)  node bots.js ABCD 2');
  process.exit(1);
}

const NAMES = ['그림봇', '낙서봇', '대충봇', '막눈봇', '헛손봇', '붓대봇', '삐뚤봇', '갸웃봇', '끄적봇'];
const GUESS = ['해파리', '문어발', '외계인', '단추', '거미', '선풍기', '눈사람', '전구', '개구리', '우산',
               '풍선', '두더지', '사다리', '주전자', '달팽이', '연날리기', '허수아비', '트로피'];
const pick = a => a[Math.floor(Math.random() * a.length)];
const ws = base.replace(/^http/, 'ws');
const BOOT = Date.now();          // 이번에 띄운 봇들의 표식. 다시 붙어도 그대로 쓴다

/* 손으로 그린 척하는 낙서 — 동그란 몸에 다리 몇, 점 몇. 좌표는 0~1023 */
function doodle(seed) {
  const c = seed % 8, out = [];
  const cx = 380 + (seed % 3) * 90, cy = 400 + (seed % 2) * 60, rr = 180 + (seed % 4) * 35;
  const body = { c, w: 1, p: [] };
  for (let a = 0; a <= 40; a++) {
    const t = a / 40 * Math.PI * 2;
    body.p.push(Math.round(cx + rr * Math.cos(t) + (Math.random() * 14 - 7)),
                Math.round(cy + rr * Math.sin(t) + (Math.random() * 14 - 7)));
  }
  out.push(body);
  for (let k = 0; k < 2 + seed % 3; k++) {
    const x = cx - rr / 2 + k * (rr / 2);
    out.push({ c, w: 0, p: [Math.round(x), Math.round(cy + rr - 20), Math.round(x + (Math.random() * 40 - 20)), 960] });
  }
  out.push({ c: (c + 3) % 8, w: 0, p: [cx - 60, cy - 40, cx - 52, cy - 34] });
  out.push({ c: (c + 3) % 8, w: 0, p: [cx + 60, cy - 40, cx + 52, cy - 34] });
  return out;
}

for (let i = 0; i < many; i++) seat(i);

/**
 * 봇 하나. 연결이 끊기면 같은 표식으로 다시 붙는다 —
 * `wrangler dev` 는 파일을 고칠 때마다 워커를 다시 올리고, 그때 붙어 있던 연결은 다 떨어진다.
 * 표식이 같으면 판이 돌던 중이라도 제자리로 돌아간다.
 */
function seat(i) {
  const name = NAMES[i % NAMES.length];
  const pid = 'bot-' + i + '-' + BOOT;
  let sock, acted = new Set(), lastBook = -1, starting = false, yielded = 0, tries = 0;

  const hook = () => {
    sock = new WebSocket(`${ws}/room?code=${code}&pid=${pid}&name=${encodeURIComponent(name)}`);
    sock.onopen = () => { console.log(name, tries ? '다시 붙었습니다' : '들어왔습니다'); tries = 0; };
    sock.onerror = () => {};
    sock.onclose = () => {
      tries += 1;
      if (tries > 40) return console.error(name, '— 서버를 못 찾겠습니다.', base, '가 떠 있나요');
      setTimeout(hook, Math.min(4000, 400 * tries));
    };
    sock.onmessage = onmsg;
  };

  function onmsg(e) {
    let v; try { v = JSON.parse(e.data); } catch { return; }
    if (v.t === 'err') return console.log(name, '—', v.m);
    if (v.t !== 'room') return;

    /* 사람보다 봇이 먼저 붙었으면 봇이 방장이 되어 버린다. 그때는 봇이 직접 몰아 준다 —
       안 그러면 시작 단추가 아무에게도 없어서 방이 멈춘다 */
    const boss = v.me === v.host;
    const human = v.players.find(p => p.on && !p.pid.startsWith('bot-'));   // 접속 중인 사람에게만 넘긴다

    /* 봇이 먼저 붙어 방장이 되었는데 사람이 들어왔다 — 자리를 돌려준다.
       시작과 공개 넘기기는 사람이 쥐고 있어야 한다 */
    /* 사람이 새로고침하고 돌아오면 방장이 봇에게 넘어와 있다. 그때마다 다시 돌려준다 —
       "한 번 넘겼다"고 기억해 두면 그 뒤로는 영영 안 넘긴다. 대신 2초에 한 번으로 묶어 둔다 */
    if (boss && human && Date.now() - yielded > 2000) {
      yielded = Date.now();
      console.log(name, '→ 방장을', human.name + '님께 넘겼습니다');
      sock.send(JSON.stringify({ t: 'pass', to: human.pid }));
      return;
    }

    if (v.phase === 'lobby') {
      acted = new Set(); lastBook = -1;                  // 한 판 더 — 기억을 비운다
      if (boss && v.players.length >= 4 && !starting) {
        starting = true;
        console.log(name, '(방장) 3초 뒤 시작합니다 — 더 들어올 사람 있으면 지금');
        setTimeout(() => sock.send(JSON.stringify({ t: 'start' })), 3000);
      }
      return;
    }
    starting = false;

    if (boss && v.phase === 'reveal') {
      const at = 'turn:' + v.reveal.b + ':' + v.reveal.i;
      if (!acted.has(at)) { acted.add(at); setTimeout(() => sock.send(JSON.stringify({ t: 'turn', d: 1 })), 2600); }
    }

    // 공개 때는 가끔 별을 준다. 공책이 넘어갈 때마다 한 번씩
    if (v.phase === 'reveal' && v.reveal && v.reveal.b !== lastBook) {
      lastBook = v.reveal.b;
      if (Math.random() < .7) {
        const k = Math.floor(Math.random() * Math.max(1, (v.pages || []).length));
        setTimeout(() => sock.send(JSON.stringify({ t: 'star', b: v.reveal.b, i: k })), 500 + Math.random() * 900);
      }
      return;
    }

    const key = v.phase + ':' + v.round + (v.phase === 'pick' && v.picked ? ':head' : '');
    if (v.done || v.seat < 0 || acted.has(key)) return;
    acted.add(key);

    if (v.phase === 'pick') {
      /* 짝수 인원이면 고른 뒤 자기가 그림까지 그려야 한 차례가 끝난다 — 안 내면 판이 시계 끝까지 멈춘다 */
      if (v.picked) {
        if (!v.andDraw) return;
        setTimeout(() => {
          sock.send(JSON.stringify({ t: 'head', s: blank ? [] : doodle(i + 1) }));
          console.log(name, blank ? '고른 말은 안 그리고 넘겼습니다' : '고른 말을 그렸습니다 ←', v.picked.word);
        }, blank ? 500 + i * 200 : 1200 + i * 600);
        return;
      }
      acted.delete(key);                      // 고른 뒤 그림 차례에 한 번 더 들어와야 한다
      const i2 = Math.floor(Math.random() * 6);
      setTimeout(() => {
        sock.send(JSON.stringify({ t: 'pick', i: i2 }));
        console.log(name, '제시어 골랐습니다');
      }, 700 + i * 400 + Math.random() * 800);
    } else if (v.phase === 'play') {
      const wait = 1500 + i * 700 + Math.random() * 2500;
      if (v.kind === 'draw') {
        setTimeout(() => {
          sock.send(JSON.stringify({ t: 'draw', s: blank ? [] : doodle(i + v.round) }));
          console.log(name, blank ? '안 그리고 넘겼습니다 ←' : '그렸습니다 ←', v.prev ? v.prev.word : '(빈 쪽)');
        }, blank ? 600 + i * 200 : wait);
      } else {
        const w = pick(GUESS);
        setTimeout(() => {
          sock.send(JSON.stringify({ t: 'guess', w }));
          console.log(name, '찍었습니다 →', w);
        }, wait);
      }
    }
  }

  hook();
}

console.log('방', code, '에 봇', many + '명 —  끝내려면 Ctrl+C');
