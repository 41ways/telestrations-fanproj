/**
 * 스케치퀴즈 — 한 사람이 그리고 나머지가 맞힌다. 여기에는 셈만 있다(node test.js 로 돌려 본다).
 *
 * 차례 하나가 한 그림이다. 차례마다 그리는 사람이 한 칸씩 옮겨 가고,
 * 모두 한 번씩 그리면 한 바퀴. 몇 바퀴 돌지는 대기실에서 고른다.
 *
 * 점수는 빨리 맞힐수록 크고, 그린 사람은 맞힌 사람 수만큼 받는다 —
 * 아무도 못 맞히게 어렵게만 그리면 그린 사람도 손해다.
 */
export const QUIZ_MIN = 2;
export const LAPS = [1, 2, 3];                 // 한 사람이 몇 번씩 그리나
export const DEFAULT_LAPS = 2;
export const SEC_QPICK = 15;                   // 제시어 고르는 시간
export const SEC_QEND = 6;                     // 정답 보여 주는 참
export const MAX_SAY = 30;
export const DRAW_BONUS = 40;                  // 한 사람이 맞힐 때마다 그린 사람이 받는 점수

/** 맞혔는지 볼 때는 띄어쓰기와 문장부호를 지우고 견준다 */
export const norm = s => String(s == null ? '' : s).toLowerCase().replace(/[\s·・.,!?~'"’”\-_()[\]]/g, '');
export const same = (a, b) => !!norm(a) && norm(a) === norm(b);

/** 한 글자만 다르거나 한 글자 모자란 답 — "아깝다"고 알려 준다 */
export function near(a, b) {
  const x = norm(a), y = norm(b);
  if (!x || !y || x === y) return false;
  if (Math.abs(x.length - y.length) > 1) return false;
  if (x.length === y.length) {
    let d = 0;
    for (let i = 0; i < x.length; i++) if (x[i] !== y[i]) d++;
    return d === 1;
  }
  const [s, l] = x.length < y.length ? [x, y] : [y, x];   // 한 글자 빠진 것
  for (let i = 0; i < l.length; i++) if (s === l.slice(0, i) + l.slice(i + 1)) return true;
  return false;
}

/** 맞힌 점수 — 남은 시간이 많을수록 크다 */
export const scoreOf = (left, total) => 50 + Math.round(150 * Math.max(0, Math.min(1, total ? left / total : 0)));

/** 힌트로 열어 줄 글자 자리 — 글자가 있는 칸만, 섞어서 */
export function hintSlots(word, rand) {
  const idx = [];
  for (let i = 0; i < word.length; i++) if (word[i].trim()) idx.push(i);
  for (let i = idx.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [idx[i], idx[j]] = [idx[j], idx[i]];
  }
  return idx.slice(0, Math.max(1, Math.floor(idx.length / 3)));   // 많아야 삼분의 일만 연다
}

/** 지금까지 열린 만큼의 힌트. 안 연 글자는 ○, 띄어쓰기는 그대로 */
export function maskOf(word, open) {
  const on = new Set(open || []);
  let out = '';
  for (let i = 0; i < word.length; i++) out += !word[i].trim() ? ' ' : on.has(i) ? word[i] : '○';
  return out;
}

/** 힌트를 몇 개까지 열어 둘 때인가 — 시간이 흐를수록 늘어난다 */
export function hintCount(left, total, slots) {
  if (!total || !slots) return 0;
  const gone = 1 - Math.max(0, Math.min(1, left / total));
  return gone < .4 ? 0 : gone < .7 ? Math.ceil(slots / 2) : slots;
}
