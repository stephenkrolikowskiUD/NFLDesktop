const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../app.js'), 'utf8');

function loadFunction(name, dependencies = {}) {
  const start = source.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `Missing function ${name}`);
  const end = source.indexOf('\nfunction ', start + 1);
  const context = vm.createContext({...dependencies});
  vm.runInContext(source.slice(start, end < 0 ? undefined : end), context);
  return context[name];
}

test('shortlist order follows estimated return even when streak scores disagree', () => {
  const compare = loadFunction('compareModelCandidates');
  const higher = {name: 'Higher EV', edge: .08, total: 20, conviction: 1};
  const streak = {name: 'Long streak', edge: .04, total: 30, conviction: 99};
  assert.deepEqual([streak, higher].sort(compare), [higher, streak]);
});

test('an old pick stays locked even if the player slate has rolled to next week', () => {
  const started = loadFunction('isPickStarted', {
    scheduleRowStartMs: () => null, rowField: (r, k) => r[k],
    entryTodayISO: () => '2026-09-28', getLockInfo: () => ({started: false}),
  });
  assert.equal(started({GAME_DATE: '2026-09-27', player: 'Test'}, false), true);
  assert.equal(started({GAME_DATE: '2026-09-29', player: 'Test'}, false), false);
});

test('adding to tray preserves the captured price and its actual sportsbook', () => {
  const row = {name: 'Test Player', metric: 'REC', dkLine: '3.5', lean: 'UNDER',
    odds: -125, edge: .04, hitRate: .58, team: 'A', opp: 'B', isP: false,
    prop: {PICK_BOOK: 'betmgm'}};
  const state = {};
  const add = loadFunction('toggleShortlistTray', {
    getTonightShortlist: () => [row], normalizePlayerName: x => x,
    normalizePropMetric: x => x, getActiveShortlistTray: () => [],
    shortlistLegKey: x => x.name, currentShortlistSlateKey: () => 'test',
    rowField: (r, k) => r[k], formatBookName: x => x,
    persistShortlistTray: () => {}, render: () => {}, st: state,
  });
  add('Test Player', 'REC', '3.5', 'UNDER');
  assert.equal(state.shortlistTray[0].book, 'betmgm');
  assert.equal(state.shortlistTray[0].odds, -125);
});

test('estimate row distinguishes observations, captured price and model assumptions', () => {
  const renderRow = loadFunction('renderShortlistEstimateRow', {
    rowField: (r, k) => r[k], optionalRowNumber: (r, k) => r[k] ?? null,
    gameStartTimeForTeams: () => '', isInShortlistTray: () => false,
    esc: x => String(x).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;'),
    renderPlayerHeadshot: () => '', playerLink: () => 'Test player',
    formatBookName: x => x, fmtOdds: x => String(x), propTypeLabel: x => x,
    getShortlistMatchupEvidence: () => 'Matchup unavailable',
  });
  const html = renderRow({name: 'Test player', metric: 'REC', dkLine: '3.5',
    lean: 'UNDER', odds: -125, edge: .044, hitRate: .58, impliedProb: .5556,
    total: 24, team: 'A', opp: 'B', prop: {PICK_BOOK: 'betmgm', CURRENT_SEASON_GAMES: 2}}, 0);
  assert.match(html, /captured price/);
  assert.match(html, /Kickoff unavailable/);
  assert.match(html, /Price break-even/);
  assert.match(html, /2 current-season games/);
  assert.match(html, /not independent games/);
  assert.doesNotMatch(html, /VALIDATED|SMASH|elite|no-vig/);
});
