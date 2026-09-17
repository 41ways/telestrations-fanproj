// node test.js — 공책이 제대로 도는지, 제시어 카드가 말이 되는지 본다
import {
  MIN_PLAYERS, MAX_PLAYERS, LEVELS,
  headOf, pagesOf, kindOfPage, pageOfRound, bookOf, seatOfPage, trim, SECS, secsOf,
} from './src/rules.js';
import { EASY, MEDIUM, HARD, card } from './src/words.js';
import { QUIZ_MIN, LAPS, same, near, scoreOf, hintSlots, maskOf, hintCount } from './src/quiz.js';

const assert = (c, m) => { if (!c) { console.error('실패:', m); process.exit(1); } };

/* ── 스케치퀴즈 셈 ── */
{
  assert(same('가는 날이 장날', '가는날이장날'), '띄어쓰기는 안 따진다');
  assert(same('해파리', '  해파리 '), '앞뒤 빈칸은 안 따진다');
  assert(!same('해파리', '해파리들'), '다른 말은 오답');
  assert(near('문어', '물어') && near('해파리', '해파리들') && !near('문어', '코끼리'), '아까운 답 가리기');

  // 빨리 맞힐수록 점수가 크고, 시간이 다 가도 최소는 준다
  assert(scoreOf(60, 60) > scoreOf(30, 60) && scoreOf(0, 60) === 50, '맞힌 점수');

  // 힌트는 세 글자에 한 자꼴, 시간이 갈수록 는다
  const w = '모래시계', slots = hintSlots(w, () => .5);
  assert(slots.length >= 1 && slots.length <= Math.ceil(w.length / 3), '힌트 자리 수');
  assert(hintCount(60, 60, slots.length) === 0 && hintCount(1, 60, slots.length) === slots.length, '힌트 여는 차례');
  assert(maskOf(w, []) === '○○○○' && maskOf(w, [0]) === '모○○○', '힌트 모양');
  assert(maskOf('가는 날이 장날', []) === '○○ ○○ ○○', '띄어쓰기는 그대로 보인다');

  // 차례는 사람 수 × 바퀴. 모두가 같은 수만큼 그린다
  for (let n = QUIZ_MIN; n <= MAX_PLAYERS; n++) for (const laps of LAPS) {
    const drew = new Array(n).fill(0);
    for (let t = 0; t < n * laps; t++) drew[t % n] += 1;
    assert(drew.every(c => c === laps), n + '명 ' + laps + '바퀴: 그리는 횟수가 다름');
  }
}

/* ── 공책 돌리기 ── */
for (let n = MIN_PLAYERS; n <= MAX_PLAYERS; n++) {
  const head = headOf(n), last = pagesOf(n) - 1;

  // 짝수면 제시어와 그림 둘, 홀수면 제시어 하나로 시작한다
  assert(head === (n % 2 === 0 ? 2 : 1), n + '명 첫 장 수');
  assert(pagesOf(n) === (n % 2 === 0 ? n + 1 : n), n + '명 쪽 수');

  // 공책은 늘 '답'으로 끝나야 한다 — 첫 말과 견줘야 하니까
  assert(kindOfPage(0) === 'word', '0쪽은 고른 말');
  assert(kindOfPage(last) === 'word', n + '명: 마지막 쪽이 답이 아님 (' + kindOfPage(last) + ')');

  // 한 라운드에 한 사람이 한 권씩, 겹치지 않게
  for (let r = 1; r <= n; r++) {
    const books = new Set();
    for (let s = 0; s < n; s++) books.add(bookOf(s, r, n));
    assert(books.size === n, n + '명 ' + r + '라운드에 공책이 겹침');
  }
  for (let s = 0; s < n; s++) assert(bookOf(s, 1, n) === s, '1라운드는 자기 공책');

  // 판이 끝나면 모든 공책의 모든 쪽이 꼭 한 번씩 채워진다
  const filled = Array.from({ length: n }, () => new Array(pagesOf(n)).fill(0));
  for (let b = 0; b < n; b++) for (let i = 0; i < head; i++) filled[b][i] += 1;   // 첫 장은 주인이
  for (let r = 2; r <= n; r++) for (let s = 0; s < n; s++) filled[bookOf(s, r, n)][pageOfRound(r, n)] += 1;
  assert(filled.every(bk => bk.every(c => c === 1)), n + '명: 빈 쪽이나 겹친 쪽이 있음');

  // 내 공책은 주인 바로 앞 사람에게서 멈춘다 — 도중에 나에게 돌아오지 않는다
  for (let s = 0; s < n; s++)
    for (let r = 2; r <= n; r++)
      assert(bookOf(s, r, n) !== s, '자기 공책이 판 도중에 돌아옴 (' + n + '명, ' + r + '라운드)');

  // 한 공책 안에서 같은 사람이 두 번 쓰지 않는다 (첫 장 두 쪽은 주인 몫이라 빼고 센다)
  for (let b = 0; b < n; b++) {
    const seats = new Set();
    for (let i = head; i <= last; i++) seats.add(seatOfPage(b, i, n));
    assert(seats.size === n - 1 && !seats.has(b), b + '권에 같은 사람이 두 번');
    for (let i = 0; i < head; i++) assert(seatOfPage(b, i, n) === b, '첫 장은 주인 몫');
  }

  // seatOfPage 가 bookOf 와 맞물려야 — 별과 점수가 이 식을 쓴다
  for (let r = 2; r <= n; r++) for (let s = 0; s < n; s++)
    assert(seatOfPage(bookOf(s, r, n), pageOfRound(r, n), n) === s, '쪽 주인 식이 어긋남');
}

/* ── 그림·말이 번갈아 ── */
assert(kindOfPage(1) === 'draw' && kindOfPage(2) === 'word' && kindOfPage(3) === 'draw', '번갈아 나오지 않음');

/* ── 제시어 ── */
const all = [...EASY, ...MEDIUM, ...HARD];
assert(new Set(all).size === all.length, '제시어 중복');
assert(all.every(w => w.trim() === w && w.length > 0 && w.length <= 20), '제시어 길이·공백');
for (const [key, lv] of Object.entries(LEVELS)) {
  if (!lv.mix) continue;                                  // 「직접」은 카드가 없다
  const sum = lv.mix.easy + lv.mix.medium + lv.mix.hard;
  assert(sum === 6, key + ' 난이도가 여섯 장이 아님 (' + sum + ')');
  for (let i = 0; i < 200; i++) {
    const six = card(Math.random, lv.mix);
    assert(six.length === 6, key + ' 카드가 여섯 장이 아님');
    assert(new Set(six).size === 6, key + ' 카드 안에서 겹침');
    assert(six.filter(w => EASY.includes(w)).length === lv.mix.easy, key + ' 쉬움 장수가 다름');
    assert(six.filter(w => HARD.includes(w)).length === lv.mix.hard, key + ' 어려움 장수가 다름');
  }
}

/* ── 그림 자르기 ── */
assert(trim(null).length === 0 && trim('x').length === 0, '이상한 값은 빈 그림');
assert(trim([{ c: 99, w: 99, p: [-5, 2000, 10, 10] }])[0].c === 15, '색 번호가 안 잘림');
assert(trim([{ c: 0, w: 0, p: [-5, 2000, 10, 10] }])[0].p.join() === '0,1023,10,10', '좌표가 안 잘림');
assert(trim([{ c: 0, w: 0, p: [1] }]).length === 0, '점 하나짜리 획은 버린다');
const huge = Array.from({ length: 900 }, () => ({ c: 1, w: 1, p: Array(3000).fill(500) }));
assert(trim(huge).reduce((a, s) => a + s.p.length, 0) <= 9000 * 2 + 1200, '한 쪽 먹물 한도를 넘김');

console.log('공책', MIN_PLAYERS + '~' + MAX_PLAYERS + '명 모두 제자리 — 짝수는 첫 장에 그림까지, 모두 답으로 끝남');
console.log('제시어', all.length + '개 (쉬움 ' + EASY.length + ' 보통 ' + MEDIUM.length + ' 어려움 ' + HARD.length + ')');
for (const [key, lv] of Object.entries(LEVELS)) console.log('  ' + lv.name.padEnd(4), card(Math.random, lv.mix).join(' · '));
console.log('통과');

/* ── 시간 ── */
for (const d of SECS) {
  assert(secsOf(d, 'draw') === d, '그리는 시간 ' + d);
  assert(secsOf(d, 'guess') >= 20 && secsOf(d, 'guess') <= d, '맞히는 시간 ' + d);
  assert(secsOf(d, 'pickdraw') > d, '고르고 그리기 ' + d);
}
assert(secsOf(999, 'draw') === 60, '모르는 값은 기본으로');
console.log('시간 통과');
