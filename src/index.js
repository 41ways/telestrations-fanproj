/**
 * 텔레스트레이션 — 들머리.
 *
 * 페이지(public/index.html)는 Workers 가 그대로 내주고, 이 코드는 방 연결만 맡는다.
 *   GET /new            빈 방 번호 하나 받아 오기
 *   GET /room?code=&pid=&name=   그 방에 웹소켓으로 붙기
 *
 * 방 번호가 곧 Durable Object 이름이다. 같은 번호를 친 사람은 같은 방으로 간다.
 */
import { Room } from './room.js';
export { Room };

/* 헷갈리는 글자(I·O·0·1)는 뺐다. 불러 주기 좋게 네 글자 */
const ALPHA = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
const CODE_RE = /^[A-HJ-NP-Z2-9]{4}$/;
const newCode = () => Array.from({ length: 4 }, () => ALPHA[Math.floor(Math.random() * ALPHA.length)]).join('');

/* 이 페이지와 로컬 개발에서만 받는다. 남의 페이지가 방 서버를 퍼 가 쓰지 못하게 */
const ok = (origin, self) => !origin || origin === self
  || /^https:\/\/41ways\.github\.io$/.test(origin)
  || /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin);

const json = (o, s = 200) => Response.json(o, { status: s });

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const origin = req.headers.get('Origin');
    if (!ok(origin, url.origin)) return new Response('다른 곳에서는 못 붙습니다', { status: 403 });

    /* 아직 아무도 없는 번호를 찾아 준다. 몇 번 헛집으면 그냥 내준다 — 네 글자면 겹칠 일이 드물다 */
    if (url.pathname === '/new') {
      for (let i = 0; i < 4; i++) {
        const code = newCode();
        const id = env.ROOM.idFromName(code);
        const free = await env.ROOM.get(id).fetch('https://r/probe').then(r => r.json()).catch(() => ({ free: true }));
        if (free.free) return json({ code });
      }
      return json({ code: newCode() });
    }

    if (url.pathname === '/room') {
      if (req.headers.get('Upgrade') !== 'websocket') return new Response('웹소켓으로 붙으세요', { status: 426 });
      const code = (url.searchParams.get('code') || '').toUpperCase();
      if (!CODE_RE.test(code)) return new Response('방 번호가 이상합니다', { status: 400 });
      const id = env.ROOM.idFromName(code);
      return env.ROOM.get(id).fetch(req);
    }

    if (url.pathname === '/health') return json({ ok: true });
    return new Response('텔레스트레이션', { status: 404 });
  },
};
