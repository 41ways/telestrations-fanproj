/**
 * 열린 방 목록.
 *
 * 방은 하나에 Durable Object 하나라, 밖에서는 어떤 방이 열려 있는지 알 길이 없다.
 * 그래서 방이 스스로 여기에 자기 형편을 적어 둔다 — 사람이 드나들거나 판이 시작될 때만.
 * 목록은 칸 하나에 통째로 들고 있는다. 방이 몇백 개가 되어도 몇 KB 다.
 *
 * 적어 둔 지 오래된 방은 목록에서 지운다. 방이 잠든 채 지워졌는데
 * 마지막 소식만 남아 있으면, 눌러도 아무도 없는 빈 방으로 들어가게 된다.
 */
import { DurableObject } from 'cloudflare:workers';

const STALE_MS = 20 * 60 * 1000;      // 이만큼 소식이 없으면 목록에서 내린다
const MAX_ROOMS = 300;

export class Lobby extends DurableObject {
  async rooms() { return (await this.ctx.storage.get('rooms')) || {}; }

  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === '/put') {
      const r = await req.json();
      const rooms = await this.rooms();
      if (!r.n) delete rooms[r.code];                       // 아무도 없으면 목록에서 내린다
      else rooms[r.code] = { ...r, at: Date.now() };
      await this.ctx.storage.put('rooms', prune(rooms));
      return Response.json({ ok: true });
    }

    if (url.pathname === '/gone') {
      const { code } = await req.json();
      const rooms = await this.rooms();
      delete rooms[code];
      await this.ctx.storage.put('rooms', rooms);
      return Response.json({ ok: true });
    }

    /* 목록 — 비공개 방과 꽉 찬 방은 빼고, 기다리는 방을 앞에 */
    const rooms = prune(await this.rooms());
    const list = Object.values(rooms)
      .filter(r => !r.priv && r.n > 0)
      .sort((a, b) => (a.phase === 'lobby' ? 0 : 1) - (b.phase === 'lobby' ? 0 : 1) || b.at - a.at)
      .slice(0, 40)
      .map(({ code, game, n, max, phase, host }) => ({ code, game, n, max, phase, host }));
    return Response.json({ rooms: list, people: list.reduce((s, r) => s + r.n, 0) });
  }
}

function prune(rooms) {
  const cut = Date.now() - STALE_MS;
  const live = Object.values(rooms).filter(r => r.at > cut).sort((a, b) => b.at - a.at).slice(0, MAX_ROOMS);
  return Object.fromEntries(live.map(r => [r.code, r]));
}
