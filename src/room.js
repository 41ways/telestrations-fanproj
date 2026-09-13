/**
 * 방 하나 = Durable Object 하나.
 *
 * 판이 어떻게 도는지는 rules.js 에 적어 두었다 — 짝수·홀수가 갈리는 까닭까지.
 * 여기는 그 규칙대로 쪽을 채우고, 시계를 재고, 사람마다 다른 화면을 내려보내는 일을 한다.
 *
 * 연결은 WebSocket Hibernation 으로 받는다. 아무도 손대지 않는 동안 방은 잠들고,
 * 깨어나면 저장소에서 판을 다시 읽는다. 그래서 판은 메모리가 아니라 저장소가 원본이다.
 * 그림은 한 쪽에 하나씩 따로 둔다 — 한 칸에 넣을 수 있는 크기(128KiB)가 정해져 있어서
 * 판 전체를 한 덩어리로 두면 그림 몇 장에 금방 넘친다.
 */
import { DurableObject } from 'cloudflare:workers';
import { card } from './words.js';
import {
  MIN_PLAYERS, MAX_PLAYERS, MAX_NAME, MAX_GUESS, MAX_CONN,
  SECS, DEFAULT_SECS, secsOf, SEC_VOTE, IDLE_MS,
  LEVELS, DEFAULT_LEVEL,
  clean, headOf, pagesOf, kindOfPage, pageOfRound, bookOf, seatOfPage, trim,
} from './rules.js';

export class Room extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.r = null;                                   // 판. 잠에서 깨면 저장소에서 다시 읽는다
    ctx.blockConcurrencyWhile(async () => { this.r = await ctx.storage.get('r') || null; });
  }

  /* ── 저장 ── */
  async save() { await this.ctx.storage.put('r', this.r); }
  async page(b, i) { return (await this.ctx.storage.get('p:' + b + ':' + i)) || null; }
  async setPage(b, i, v) { await this.ctx.storage.put('p:' + b + ':' + i, v); }

  /* ── 들어오기 ── */
  async fetch(req) {
    const url = new URL(req.url);
    /* 들머리가 빈 번호를 고를 때 물어보는 곳. 방을 새로 만들지는 않는다 */
    if (url.pathname === '/probe') return Response.json({ free: !this.r || !this.r.players.length });

    const code = clean(url.searchParams.get('code'), 8).toUpperCase();
    const pid = clean(url.searchParams.get('pid'), 40);
    const name = clean(url.searchParams.get('name'), MAX_NAME) || '아무개';
    if (!code || !pid) return new Response('bad', { status: 400 });
    if (this.ctx.getWebSockets().length >= MAX_CONN) return new Response('붐빔', { status: 429 });

    if (!this.r) {                                   // 첫 사람이 방을 연다
      this.r = {
        code, host: pid, phase: 'lobby', round: 0, deadline: 0,
        level: DEFAULT_LEVEL, secs: DEFAULT_SECS,
        players: [], cards: {}, done: [], reveal: { b: 0, i: -1 }, votes: {}, touched: Date.now(),
      };
    }

    const me = this.r.players.find(p => p.pid === pid);
    if (me) me.name = name;                          // 돌아온 사람 — 자리는 그대로
    else if (this.r.phase === 'lobby') {
      if (this.r.players.length >= MAX_PLAYERS) return new Response('꽉 참', { status: 409 });
      this.r.players.push({ pid, name });
    }
    // 판이 이미 돌고 있는데 처음 보는 사람이면 구경만 한다

    const pair = new WebSocketPair();
    this.ctx.acceptWebSocket(pair[1]);
    pair[1].serializeAttachment({ pid, name });

    this.r.touched = Date.now();
    await this.handoff(null);                        // 방장이 이미 나가 있었다면 방금 온 사람이 받는다
    await this.save();
    if (!this.r.deadline) await this.ctx.storage.setAlarm(Date.now() + IDLE_MS);
    await this.pushAll();
    return new Response(null, { status: 101, webSocket: pair[0] });
  }

  /* ── 보내기 ── */
  who(ws) { try { return ws.deserializeAttachment() || {}; } catch { return {}; } }

  async pushAll() {
    for (const ws of this.ctx.getWebSockets()) {
      const { pid } = this.who(ws);
      try { ws.send(JSON.stringify(await this.view(pid))); } catch {}
    }
  }

  /** 사람마다 보는 게 다르다 — 자기 앞에 놓인 쪽만 받는다. 남의 공책은 넘겨보지 못한다 */
  async view(pid) {
    const r = this.r;
    const n = r.players.length;
    const s = r.players.findIndex(p => p.pid === pid);
    const live = new Set(this.ctx.getWebSockets().map(w => this.who(w).pid));
    const v = {
      t: 'room', code: r.code, phase: r.phase, round: r.round, rounds: n,
      host: r.host, me: pid, seat: s, level: r.level, secs: r.secs || DEFAULT_SECS,
      players: r.players.map(p => ({ pid: p.pid, name: p.name, on: live.has(p.pid) })),
      left: Math.max(0, Math.round((r.deadline - Date.now()) / 1000)),
      waiting: r.players.filter(p => !r.done.includes(p.pid)).map(p => p.pid),
      done: r.done.includes(pid),
    };

    /* 첫 라운드 — 카드를 고른다. 짝수 인원이면 고른 뒤 곧바로 자기가 그린다 */
    if (r.phase === 'pick' && s >= 0) {
      v.card = r.cards[pid] || [];
      v.custom = r.level === 'custom';
      v.andDraw = headOf(n) === 2;
      v.picked = (await this.page(s, 0)) || null;      // 골라 둔 말 (짝수 인원이면 그리는 중에도 보인다)
    }

    if (r.phase === 'play' && s >= 0) {
      const b = bookOf(s, r.round, n);
      const i = pageOfRound(r.round, n);
      v.kind = kindOfPage(i);
      v.prev = await this.page(b, i - 1);              // 바로 앞 쪽만 보여 준다
      v.owner = r.players[b] ? r.players[b].name : '';
    }

    /* 공개 — 한 권씩. i 는 -1(표지: 누구 공책인지만) → 0..last(쪽) → last+1(끝 도장) */
    if (r.phase === 'reveal') {
      const { b, i } = r.reveal;
      v.reveal = { b, i, owner: r.players[b] ? r.players[b].name : '', of: n, pages: pagesOf(n) };
      v.pages = [];
      for (let k = 0; k <= i && k < pagesOf(n); k++) {
        const pg = await this.page(b, k);
        v.pages.push(pg && { ...pg, by: r.players[pg.s] ? r.players[pg.s].name : '' });
      }
    }

    /* 투표·끝 — 공책 전체는 크니까 여기 실지 않고, 화면이 한 번만 따로 청한다(album) */
    if (r.phase === 'vote' || r.phase === 'done') {
      v.album = { key: this.albumKey(), of: n, pages: pagesOf(n) };
      v.myVote = r.votes[pid] || null;
      v.voted = Object.keys(r.votes).length;
      v.voters = r.players.filter(p => live.has(p.pid) || r.votes[p.pid]).length;
    }
    if (r.phase === 'done') v.top = await this.winner();
    return v;
  }

  albumKey() { return this.r.code + ':' + (this.r.started || 0); }

  /** 공책 전부 — 한 권에 한 통씩. 투표할 때와 끝나고 다시 볼 때 */
  async album(ws) {
    const r = this.r, n = r.players.length, key = this.albumKey();
    for (let b = 0; b < n; b++) {
      const pages = [];
      for (let k = 0; k < pagesOf(n); k++) {
        const pg = await this.page(b, k);
        pages.push(pg && { ...pg, by: r.players[pg.s] ? r.players[pg.s].name : '' });
      }
      try { ws.send(JSON.stringify({ t: 'book', key, b, of: n, owner: r.players[b] ? r.players[b].name : '', pages })); } catch {}
    }
  }

  /* ── 받기 ── */
  async webSocketMessage(ws, raw) {
    const { pid } = this.who(ws);
    if (!pid || !this.r) return;
    let m; try { m = JSON.parse(raw); } catch { return; }
    const r = this.r;
    r.touched = Date.now();
    const isHost = pid === r.host;

    try {
      if (m.t === 'start' && isHost && r.phase === 'lobby') await this.start();
      else if (m.t === 'set' && isHost && r.phase === 'lobby') this.set(m);
      else if (m.t === 'pick' && r.phase === 'pick') await this.pick(pid, m.i, m.w);
      else if (m.t === 'head' && r.phase === 'pick') await this.head(pid, m.s);
      else if (m.t === 'draw' && r.phase === 'play') await this.hand(pid, { strokes: m.s });
      else if (m.t === 'guess' && r.phase === 'play') await this.hand(pid, { word: clean(m.w, MAX_GUESS) });
      else if (m.t === 'turn' && isHost && r.phase === 'reveal') await this.turn(m.d);
      else if (m.t === 'album' && (r.phase === 'vote' || r.phase === 'done')) { await this.album(ws); return; }
      else if (m.t === 'vote' && r.phase === 'vote') await this.vote(pid, m.b, m.i);
      else if (m.t === 'again' && isHost && r.phase === 'done') await this.again();
      else if (m.t === 'pass' && isHost) await this.pass(pid, m.to);
      else return;
    } catch (e) {
      try { ws.send(JSON.stringify({ t: 'err', m: String(e.message || e) })); } catch {}
      return;
    }
    await this.save();
    await this.pushAll();
  }

  /* 연결이 끊겨도 바로 방장을 넘기지 않는다 — 새로고침이나 서버 재시작이면 몇 초 안에 돌아온다.
     그때마다 방장이 봇이나 남에게 넘어갔다 오면 시작·넘기기 단추가 들썩인다 */
  async webSocketClose(ws) { await this.tidy(ws); }
  async webSocketError(ws) { await this.tidy(ws); }
  async tidy(ws) {
    const r = this.r;
    if (r && r.phase === 'lobby') await this.handoff(ws);          // 시작 전엔 자리를 바로 비운다
    else setTimeout(() => { this.handoff(null).then(() => this.settle()).then(() => this.pushAll()).catch(() => {}); }, 4000);
    await this.pushAll();
  }

  /**
   * 나간 사람을 정리한다.
   *
   * 아직 시작 전이면 자리를 아예 비운다 — 잠깐 들렀다 간 사람 몫까지 공책을 돌릴 이유가 없다.
   * 판이 돌기 시작한 뒤에는 자리를 지켜 준다. 새로고침하고 돌아올 수 있어야 하니까.
   *
   * 방장이 없어졌으면 남은 사람에게 넘긴다. 시작도 공개도 방장만 몰 수 있어서,
   * 방장이 탭을 닫고 가면 방이 그대로 멈춘다.
   */
  async handoff(gone) {
    const r = this.r;
    if (!r) return;
    const live = new Set(this.ctx.getWebSockets().filter(w => w !== gone).map(w => this.who(w).pid));
    if (r.phase === 'lobby') r.players = r.players.filter(p => live.has(p.pid));
    if (live.has(r.host)) return;
    const next = r.players.find(p => live.has(p.pid));
    if (next) { r.host = next.pid; await this.save(); }
  }

  /** 방장 자리를 넘긴다. 봇이 먼저 들어와 방장이 된 판을 사람에게 돌려줄 때 쓴다 */
  async pass(pid, to) {
    const r = this.r;
    const live = new Set(this.ctx.getWebSockets().map(w => this.who(w).pid));
    const next = r.players.find(p => p.pid === to && p.pid !== pid && live.has(p.pid));
    if (next) r.host = next.pid;
  }

  /** 대기실에서 방장이 고르는 것 — 제시어 난이도, 그리는 시간 */
  set(m) {
    if (LEVELS[m.level]) this.r.level = m.level;
    if (SECS.includes(m.secs | 0)) this.r.secs = m.secs | 0;
  }

  /* ── 판 ── */
  async start() {
    const r = this.r, n = r.players.length;
    if (n < MIN_PLAYERS) throw new Error(MIN_PLAYERS + '명은 모여야 시작합니다');
    const old = [...(await this.ctx.storage.list({ prefix: 'p:' })).keys()];
    if (old.length) await this.ctx.storage.delete(old);
    const mix = (LEVELS[r.level] || LEVELS[DEFAULT_LEVEL]).mix;
    r.cards = {};
    if (mix) for (const p of r.players) r.cards[p.pid] = card(Math.random, mix);   // 「직접」이면 카드 없이 각자 적는다
    r.phase = 'pick'; r.round = 1; r.done = []; r.votes = {}; r.reveal = { b: 0, i: -1 }; r.started = Date.now();
    await this.clock(secsOf(r.secs, headOf(n) === 2 ? 'pickdraw' : 'pick'));
  }

  /** 카드에서 말을 고른다 — 자기 공책 0쪽 */
  /** 카드에서 골랐으면 i, 직접 적었으면 w */
  async pick(pid, i, w) {
    const r = this.r, n = r.players.length;
    w = r.level === 'custom' ? clean(w, MAX_GUESS) : (r.cards[pid] || [])[i | 0];
    if (!w || r.done.includes(pid)) return;
    const s = r.players.findIndex(p => p.pid === pid);
    if (s < 0) return;
    await this.setPage(s, 0, { kind: 'word', word: w, s });
    if (headOf(n) === 2) return;                      // 짝수 인원은 그림까지 그려야 한 차례가 끝난다
    r.done.push(pid);
    if (r.done.length >= n) await this.next();
  }

  /** 짝수 인원의 첫 라운드 — 고른 말을 자기가 그려서 1쪽에 붙인다 */
  async head(pid, strokes) {
    const r = this.r, n = r.players.length;
    if (headOf(n) !== 2 || r.done.includes(pid)) return;
    const s = r.players.findIndex(p => p.pid === pid);
    if (s < 0 || !(await this.page(s, 0))) return;     // 아직 말을 안 골랐다
    await this.setPage(s, 1, { kind: 'draw', strokes: trim(strokes), s });
    r.done.push(pid);
    if (r.done.length >= n) await this.next();
  }

  /** 이번 라운드에 내 앞에 놓인 쪽을 채운다 */
  async hand(pid, v) {
    const r = this.r, n = r.players.length;
    const s = r.players.findIndex(p => p.pid === pid);
    if (s < 0 || r.done.includes(pid)) return;
    const i = pageOfRound(r.round, n);
    const pg = kindOfPage(i) === 'draw'
      ? { kind: 'draw', strokes: trim(v.strokes), s }
      : { kind: 'word', word: v.word || '…', s };
    await this.setPage(bookOf(s, r.round, n), i, pg);
    r.done.push(pid);
    if (r.done.length >= n) await this.next();
  }

  /** 다음 라운드로. 다 돌았으면 공개로 넘어간다 */
  async next() {
    const r = this.r, n = r.players.length;
    if (r.round >= n) {
      r.phase = 'reveal'; r.round = n; r.deadline = 0; r.reveal = { b: 0, i: -1 };
      await this.ctx.storage.setAlarm(Date.now() + IDLE_MS);
      return;
    }
    r.round += 1; r.phase = 'play'; r.done = [];
    await this.clock(secsOf(r.secs, kindOfPage(pageOfRound(r.round, n))));
  }

  /** 시간이 다 됐다 — 안 낸 자리는 빈 쪽으로 메운다. 한 사람 때문에 판이 멈추지 않게 */
  async fill() {
    const r = this.r, n = r.players.length;
    for (let s = 0; s < n; s++) {
      const p = r.players[s];
      if (r.done.includes(p.pid)) continue;
      if (r.phase === 'pick') {
        if (!(await this.page(s, 0))) await this.setPage(s, 0, { kind: 'word', word: (r.cards[p.pid] || ['…'])[0], s });
        if (headOf(n) === 2) await this.setPage(s, 1, { kind: 'draw', strokes: [], s });
      } else {
        const i = pageOfRound(r.round, n);
        await this.setPage(bookOf(s, r.round, n), i,
          kindOfPage(i) === 'draw' ? { kind: 'draw', strokes: [], s } : { kind: 'word', word: '…', s });
      }
      r.done.push(p.pid);
    }
    await this.next();
  }

  /**
   * 방장이 한 걸음 넘긴다. 한 권은 표지(-1) → 쪽들 → 끝(last+1) 순으로 지나가고,
   * 마지막 권의 끝을 넘기면 투표로 간다.
   */
  async turn(d) {
    const r = this.r, n = r.players.length, last = pagesOf(n) - 1;
    let { b, i } = r.reveal;
    if (d > 0) { i += 1; if (i > last + 1) { b += 1; i = -1; } }
    else { i -= 1; if (i < -1) { b -= 1; i = last + 1; } }
    if (b >= n) { r.phase = 'vote'; r.reveal = { b: n - 1, i: last + 1 }; r.votes = {}; await this.clock(SEC_VOTE); return; }
    if (b < 0) { b = 0; i = -1; }
    r.reveal = { b, i };
  }

  /**
   * 한 사람이 한 표. 판 전체에서 제일 마음에 든 쪽 하나를 뽑는다 — 그림인지 답인지는 가리지 않는다.
   * 한 번 내면 못 바꾼다(화면에서 확인을 거친다). 붙어 있는 사람이 다 내면 바로 결과로 간다.
   */
  async vote(pid, b, i) {
    const r = this.r, n = r.players.length;
    if (r.players.findIndex(p => p.pid === pid) < 0 || r.votes[pid]) return;   // 구경꾼은 못 뽑는다
    b |= 0; i |= 0;
    if (b < 0 || b >= n || i < 0 || i >= pagesOf(n)) return;
    r.votes[pid] = b + ':' + i;
    await this.settle();
  }

  /** 붙어 있는 사람이 다 냈으면 결과로. 누가 나갔을 때도 다시 본다 */
  async settle() {
    const r = this.r;
    if (!r || r.phase !== 'vote') return;
    const live = new Set(this.ctx.getWebSockets().map(w => this.who(w).pid));
    const voters = r.players.filter(p => live.has(p.pid) || r.votes[p.pid]);
    if (voters.length && voters.every(p => r.votes[p.pid])) { await this.finish(); await this.save(); }
  }

  async finish() {
    const r = this.r;
    r.phase = 'done'; r.deadline = 0;
    await this.ctx.storage.setAlarm(Date.now() + IDLE_MS);
  }

  /** 표를 제일 많이 받은 쪽. 같은 표로 갈리면 갈린 대로 다 돌려준다 */
  async winner() {
    const r = this.r, n = r.players.length;
    const count = {};
    for (const k of Object.values(r.votes)) count[k] = (count[k] || 0) + 1;
    const best = Math.max(0, ...Object.values(count));
    if (!best) return [];

    const out = [];
    for (const [k, c] of Object.entries(count)) {
      if (c !== best) continue;
      const [b, i] = k.split(':').map(Number);
      const pg = await this.page(b, i);
      if (!pg) continue;
      const seat = seatOfPage(b, i, n);
      out.push({
        b, i, votes: c, kind: pg.kind, word: pg.word, strokes: pg.strokes,
        by: r.players[seat] ? r.players[seat].name : '',
        book: r.players[b] ? r.players[b].name : '',
      });
    }
    return out;
  }

  async again() {
    const r = this.r;
    r.phase = 'lobby'; r.round = 0; r.deadline = 0; r.done = []; r.votes = {}; r.cards = {};
    const first = r.players.shift(); if (first) r.players.push(first);   // 자리를 돌려 짝이 바뀌게
    /* 판 도중에 나간 사람은 자리를 비우고, 구경만 하던 사람은 이제 자리에 앉는다 */
    const live = new Set(this.ctx.getWebSockets().map(w => this.who(w).pid));
    r.players = r.players.filter(p => live.has(p.pid));
    for (const ws of this.ctx.getWebSockets()) {
      const { pid, name } = this.who(ws);
      if (pid && !r.players.some(p => p.pid === pid) && r.players.length < MAX_PLAYERS) r.players.push({ pid, name: name || '아무개' });
    }
    if (!live.has(r.host) && r.players[0]) r.host = r.players[0].pid;
    await this.ctx.storage.setAlarm(Date.now() + IDLE_MS);
  }

  async clock(sec) {
    this.r.deadline = Date.now() + sec * 1000;
    await this.ctx.storage.setAlarm(this.r.deadline);
  }

  /* 시계가 울렸다 — 라운드 마감이거나, 오래 비어 있던 방을 치우는 때다 */
  async alarm() {
    const r = this.r;
    if (!r) return;
    if (Date.now() - r.touched > IDLE_MS) { await this.ctx.storage.deleteAll(); this.r = null; return; }
    if ((r.phase === 'pick' || r.phase === 'play') && r.deadline && Date.now() >= r.deadline - 500) {
      await this.fill();
      await this.save();
      await this.pushAll();
    } else if (r.phase === 'vote' && r.deadline && Date.now() >= r.deadline - 500) {
      await this.finish();                           // 표를 안 낸 사람은 기권
      await this.save();
      await this.pushAll();
    } else {
      await this.ctx.storage.setAlarm(Date.now() + IDLE_MS);
    }
  }
}
