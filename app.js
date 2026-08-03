// 🏈 NFL DFS Dashboard (v1.1 — nflverse data layer)
// Vanilla JS, Google Sheets backend. No build step.

// ============================================================================
// CONFIG
// ============================================================================

const SHEET_ID = '1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0';

// Sheet tabs are addressed by NAME, not gid. Gids are opaque integers that
// change when a tab is recreated, so name-based gviz URLs stay valid across
// engine runs that add or rebuild tabs.
const sheetUrl = (tabName) =>
  `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv&sheet=${encodeURIComponent(tabName)}`;

// Must match the tab names the engine writes (see NFLEnginev1.py main()).
const TABS = {
  games: 'Games',
  teams: 'Teams',
  playerForm: 'PlayerForm',
  injuries: 'Injuries',
};

// ============================================================================
// STATE
// ============================================================================

let data = { games: [], teams: [], playerForm: [], injuries: [] };
let activeTab = 'dashboard';
let loadState = 'loading'; // loading | ready | error
let loadError = '';
let selectedWeek = null;

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadTab(key) {
  const response = await fetch(sheetUrl(TABS[key]));
  if (!response.ok) throw new Error(`${TABS[key]}: HTTP ${response.status}`);
  const csv = await response.text();

  // A missing or unshared tab returns an HTML error page, not CSV. Detect that
  // explicitly — otherwise PapaParse happily "parses" the HTML into junk rows.
  if (csv.trimStart().startsWith('<')) {
    throw new Error(`${TABS[key]}: tab not found or sheet not public`);
  }

  const parsed = Papa.parse(csv, { header: true, dynamicTyping: true, skipEmptyLines: true });
  return parsed.data.filter((row) => Object.values(row).some((v) => v !== null && v !== ''));
}

async function loadAll() {
  try {
    const keys = Object.keys(TABS);
    const results = await Promise.allSettled(keys.map(loadTab));

    const failures = [];
    results.forEach((result, i) => {
      if (result.status === 'fulfilled') {
        data[keys[i]] = result.value;
      } else {
        data[keys[i]] = [];
        failures.push(result.reason.message);
      }
    });

    // Games is the spine — without it there's no dashboard. Everything else
    // degrades to an empty section rather than failing the whole page.
    if (!data.games.length) {
      loadState = 'error';
      loadError = failures.join(' · ') || 'No game data available';
      return;
    }

    if (failures.length) console.warn('Some tabs failed to load:', failures);
    loadState = 'ready';

    const weeks = [...new Set(data.games.map((g) => g.week))].filter(Boolean).sort((a, b) => a - b);
    selectedWeek = weeks[0] ?? null;
  } catch (err) {
    loadState = 'error';
    loadError = err.message;
  }
}

// ============================================================================
// HELPERS
// ============================================================================

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const num = (v) => (v === null || v === undefined || v === '' || Number.isNaN(Number(v)) ? null : Number(v));

const pct = (v) => (num(v) === null ? '—' : `${(num(v) * 100).toFixed(0)}%`);

const dec = (v, places = 1) => (num(v) === null ? '—' : num(v).toFixed(places));

/** nflverse spread_line is positive when the HOME team is favored. Render it
 *  the way a book would: the favorite carries the negative number. */
function formatSpread(game) {
  const line = num(game.spread_line);
  if (line === null) return '—';
  if (line === 0) return 'PK';
  return line > 0
    ? `${esc(game.home_team)} -${Math.abs(line)}`
    : `${esc(game.away_team)} -${Math.abs(line)}`;
}

function formatKickoff(game) {
  const day = game.weekday ? String(game.weekday).slice(0, 3) : '';
  const date = game.gameday ? String(game.gameday).slice(5) : '';
  const time = game.gametime || '';
  return [day, date, time].filter(Boolean).join(' ');
}

// ============================================================================
// VIEW RENDERERS (one per tab; render() stays a thin orchestrator)
// ============================================================================

function renderDashboardView() {
  const weeks = [...new Set(data.games.map((g) => g.week))].filter(Boolean).sort((a, b) => a - b);
  const games = data.games.filter((g) => g.week === selectedWeek);

  const weekPicker = weeks
    .map(
      (w) =>
        `<button class="week-chip ${w === selectedWeek ? 'active' : ''}" onclick="selectWeek(${w})">${w}</button>`
    )
    .join('');

  const rows = games
    .map(
      (g) => `
      <tr>
        <td class="matchup">${esc(g.away_team)} <span class="at">@</span> ${esc(g.home_team)}</td>
        <td>${esc(formatKickoff(g))}</td>
        <td class="spread">${formatSpread(g)}</td>
        <td>${dec(g.total_line)}</td>
        <td>${g.roof === 'dome' ? '🏟️' : '☁️'} ${esc(g.roof ?? '')}</td>
        <td class="muted">${esc(g.stadium ?? '')}</td>
      </tr>`
    )
    .join('');

  return `
    <section class="view">
      <header class="view-header">
        <h1>Week ${selectedWeek ?? '—'}</h1>
        <p class="subtitle">${games.length} games · lines from nflverse, overlaid with live book pricing when available</p>
      </header>
      <div class="week-picker">${weekPicker}</div>
      <table class="data-table">
        <thead>
          <tr><th>Matchup</th><th>Kickoff</th><th>Spread</th><th>Total</th><th>Roof</th><th>Stadium</th></tr>
        </thead>
        <tbody>${rows || '<tr><td colspan="6" class="muted">No games this week.</td></tr>'}</tbody>
      </table>
    </section>`;
}

function renderPlayerFormView() {
  const rows = data.playerForm
    .slice(0, 100)
    .map(
      (p) => `
      <tr>
        <td class="player">${esc(p.player_display_name)}</td>
        <td><span class="pos pos-${esc(p.position)}">${esc(p.position)}</span></td>
        <td>${esc(p.team)}</td>
        <td>${esc(p.week)}</td>
        <td>${pct(p.offense_pct)}</td>
        <td>${pct(p.target_share)}</td>
        <td>${dec(p.wopr, 2)}</td>
        <td class="num">${dec(p.fantasy_points_ppr)}</td>
      </tr>`
    )
    .join('');

  return `
    <section class="view">
      <header class="view-header">
        <h1>Player Form</h1>
        <p class="subtitle">Recent usage and share metrics — the input surface for projections</p>
      </header>
      <table class="data-table">
        <thead>
          <tr><th>Player</th><th>Pos</th><th>Team</th><th>Wk</th><th>Snap%</th><th>Tgt Share</th><th>WOPR</th><th>PPR</th></tr>
        </thead>
        <tbody>${rows || '<tr><td colspan="8" class="muted">No player data loaded.</td></tr>'}</tbody>
      </table>
    </section>`;
}

function renderTeamsView() {
  const byDivision = {};
  data.teams.forEach((t) => {
    const div = `${t.team_conf ?? '?'} ${t.team_division ?? ''}`.trim();
    (byDivision[div] ||= []).push(t);
  });

  const groups = Object.entries(byDivision)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(
      ([div, teams]) => `
      <div class="division">
        <h2>${esc(div)}</h2>
        <div class="team-grid">
          ${teams
            .map(
              (t) => `
            <div class="team-card" style="border-left-color:${esc(t.team_color ?? '#666')}">
              <div class="team-abbr">${esc(t.team_abbr)}</div>
              <div class="team-name">${esc(t.team_name)}</div>
            </div>`
            )
            .join('')}
        </div>
      </div>`
    )
    .join('');

  return `
    <section class="view">
      <header class="view-header">
        <h1>Teams</h1>
        <p class="subtitle">${data.teams.length} entries — includes relocated franchises, so this is not a clean 32</p>
      </header>
      ${groups || '<p class="muted">No team data loaded.</p>'}
    </section>`;
}

function renderInjuriesView() {
  const severity = { Out: 0, Doubtful: 1, Questionable: 2 };
  const sorted = [...data.injuries].sort(
    (a, b) => (severity[a.report_status] ?? 9) - (severity[b.report_status] ?? 9)
  );

  const rows = sorted
    .slice(0, 100)
    .map(
      (p) => `
      <tr>
        <td class="player">${esc(p.full_name)}</td>
        <td><span class="pos">${esc(p.position)}</span></td>
        <td>${esc(p.team)}</td>
        <td><span class="status status-${esc(String(p.report_status ?? '').toLowerCase())}">${esc(p.report_status ?? '—')}</span></td>
        <td>${esc(p.report_primary_injury ?? '—')}</td>
        <td class="muted">${esc(p.practice_status ?? '—')}</td>
      </tr>`
    )
    .join('');

  return `
    <section class="view">
      <header class="view-header">
        <h1>Injuries</h1>
        <p class="subtitle">Latest report and practice status</p>
      </header>
      <table class="data-table">
        <thead>
          <tr><th>Player</th><th>Pos</th><th>Team</th><th>Status</th><th>Injury</th><th>Practice</th></tr>
        </thead>
        <tbody>${rows || '<tr><td colspan="6" class="muted">No injury data loaded.</td></tr>'}</tbody>
      </table>
    </section>`;
}

function renderPicksView() {
  // Deliberately not shipping placeholder picks. Fake heuristics ("always take
  // the home team") look like signal on a dashboard and are worse than nothing.
  return `
    <section class="view">
      <header class="view-header">
        <h1>Picks</h1>
      </header>
      <div class="empty-state">
        <p>Not built yet — waiting on the projection model.</p>
        <p class="muted">Inputs are in place: usage and share metrics, snap counts, injuries,
        and opponent context. Next step is the projection model itself, then picks derived from it.</p>
      </div>
    </section>`;
}

function renderInfoView() {
  return `
    <section class="view">
      <header class="view-header">
        <h1>Info</h1>
      </header>
      <h2>Data sources</h2>
      <ul>
        <li><strong>nflverse</strong> — schedule, player stats, snap counts, injuries, rosters. Public, no auth.</li>
        <li><strong>The Odds API</strong> — multi-book pricing and player props.</li>
      </ul>
      <h2>Notes</h2>
      <ul>
        <li>Baseline spreads, totals, and moneylines come from nflverse at no API cost.</li>
        <li>nflverse <code>spread_line</code> is positive when the home team is favored; book spreads
            use the opposite sign. Displayed here in book convention.</li>
        <li>Snap counts are keyed on <code>pfr_player_id</code> and joined to <code>gsis_id</code>
            through the players crosswalk (~99.8% match).</li>
      </ul>
      <p class="muted">Personal research tool. Not betting advice.</p>`;
}

// ============================================================================
// ORCHESTRATOR
// ============================================================================

const VIEWS = {
  dashboard: { label: 'Slate', render: renderDashboardView },
  form: { label: 'Player Form', render: renderPlayerFormView },
  picks: { label: 'Picks', render: renderPicksView },
  teams: { label: 'Teams', render: renderTeamsView },
  injuries: { label: 'Injuries', render: renderInjuriesView },
  info: { label: 'Info', render: renderInfoView },
};

function render() {
  const app = document.getElementById('app');

  if (loadState === 'loading') {
    app.innerHTML = `<div class="loading">Loading the slate…</div>`;
    return;
  }

  if (loadState === 'error') {
    app.innerHTML = `
      <div class="error-state">
        <h1>Couldn't load the slate</h1>
        <p class="muted">${esc(loadError)}</p>
        <p class="muted">Check that the engine has run and the Sheet is shared as
        "Anyone with the link can view".</p>
      </div>`;
    return;
  }

  const nav = Object.entries(VIEWS)
    .map(
      ([key, view]) =>
        `<button class="nav-item ${activeTab === key ? 'active' : ''}" onclick="switchTab('${key}')">${view.label}</button>`
    )
    .join('');

  app.innerHTML = `
    <div class="dashboard">
      <nav class="nav">${nav}</nav>
      <main>${(VIEWS[activeTab] ?? VIEWS.dashboard).render()}</main>
    </div>`;
}

function switchTab(tab) {
  activeTab = tab;
  render();
  window.scrollTo(0, 0);
}

function selectWeek(week) {
  selectedWeek = week;
  render();
}

// ============================================================================
// INIT
// ============================================================================

async function init() {
  render();
  await loadAll();
  render();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
