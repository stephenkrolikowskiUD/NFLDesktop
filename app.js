// ⚡ NFL DFS Dashboard (v1.0 — Vanilla JS, Google Sheets backend)
// Baseline: 2026-08-02

// ============================================================================
// GLOBAL STATE
// ============================================================================

let dashboardData = {
  games: [],
  picks: [],
  teams: [],
  standings: [],
  playerProps: [],
  spreadPicks: [],
  teamCombos: [],
};

let activeTab = 'dashboard';
let isLoading = true;

const SHEET_ID = '1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0';
const SHEET_BASE_URL = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid=`;
const TABS_GID = {
  games: 0,
  picks: 1,
  teams: 2,
  standings: 3,
  playerProps: 4,
  spreadPicks: 5,
  teamCombos: 6,
};

// ============================================================================
// DATA LOADING
// ============================================================================

async function loadSheetData(tabKey) {
  const gid = TABS_GID[tabKey];
  const url = `${SHEET_BASE_URL}${gid}`;
  try {
    const response = await fetch(url);
    const csv = await response.text();
    const data = Papa.parse(csv, { header: true, dynamicTyping: false });
    return data.data.filter(row => Object.values(row).some(v => v)); // filter empty rows
  } catch (error) {
    console.error(`Failed to load ${tabKey}:`, error);
    return [];
  }
}

async function initializeDashboard() {
  isLoading = true;
  try {
    const [games, picks, teams, standings, playerProps, spreadPicks, teamCombos] = await Promise.all([
      loadSheetData('games'),
      loadSheetData('picks'),
      loadSheetData('teams'),
      loadSheetData('standings'),
      loadSheetData('playerProps'),
      loadSheetData('spreadPicks'),
      loadSheetData('teamCombos'),
    ]);

    dashboardData = { games, picks, teams, standings, playerProps, spreadPicks, teamCombos };
    console.log('✅ Dashboard data loaded:', dashboardData);
  } catch (error) {
    console.error('Failed to initialize dashboard:', error);
  } finally {
    isLoading = false;
  }
}

// ============================================================================
// RENDER FUNCTIONS (Named per tab, thin orchestrator)
// ============================================================================

function renderDashboardTab() {
  const { games, teams } = dashboardData;
  return `
    <div class="tab-content">
      <h1>NFL Slate Dashboard</h1>
      <div class="slate-info">
        <p>${games.length} games • ${teams.length} teams</p>
        <p class="subtitle">Team matchups, spreads, and picks</p>
      </div>
      <div class="games-grid">
        ${games.length > 0
          ? games.map(game => `
              <div class="game-card">
                <div class="game-matchup">${game.away_team} @ ${game.home_team}</div>
                <div class="game-spread">${game.spread || '—'}</div>
                <div class="game-time">${game.start_time || '—'}</div>
              </div>
            `).join('')
          : '<p>No games loaded yet.</p>'
        }
      </div>
    </div>
  `;
}

function renderPicksTab() {
  const { picks, spreadPicks } = dashboardData;
  return `
    <div class="tab-content">
      <h1>NFL Picks</h1>
      <div class="picks-section">
        <h2>Moneyline Picks</h2>
        <div class="picks-list">
          ${picks.length > 0
            ? picks.map(pick => `
                <div class="pick-item">
                  <div class="pick-team">${pick.team}</div>
                  <div class="pick-confidence">${pick.confidence || '—'}</div>
                </div>
              `).join('')
            : '<p>No picks generated yet.</p>'
          }
        </div>
      </div>
      <div class="picks-section">
        <h2>Spread Picks</h2>
        <div class="picks-list">
          ${spreadPicks.length > 0
            ? spreadPicks.map(pick => `
                <div class="pick-item">
                  <div class="pick-spread">${pick.team} ${pick.spread}</div>
                  <div class="pick-confidence">${pick.confidence || '—'}</div>
                </div>
              `).join('')
            : '<p>No spread picks generated yet.</p>'
          }
        </div>
      </div>
    </div>
  `;
}

function renderTeamsTab() {
  const { teams, standings } = dashboardData;
  return `
    <div class="tab-content">
      <h1>Team Selections</h1>
      <div class="teams-grid">
        ${teams.length > 0
          ? teams.map(team => `
              <div class="team-card" data-team="${team.abbreviation}">
                <div class="team-name">${team.name}</div>
                <div class="team-record">${team.wins || '0'}–${team.losses || '0'}</div>
              </div>
            `).join('')
          : '<p>No teams loaded.</p>'
        }
      </div>
    </div>
  `;
}

function renderLookupTab() {
  return `
    <div class="tab-content">
      <h1>Team Lookup</h1>
      <p>Search and filter teams by matchup, spread, or trends.</p>
    </div>
  `;
}

function renderStatsTab() {
  return `
    <div class="tab-content">
      <h1>Pick Performance</h1>
      <p>Hit rate, ROI, and confidence tier analysis.</p>
    </div>
  `;
}

function renderInfoTab() {
  return `
    <div class="tab-content">
      <h1>Dashboard Info</h1>
      <p>NFL DFS Dashboard — vanilla JS, Google Sheets backend.</p>
      <h2>Tabs</h2>
      <ul>
        <li><strong>Dashboard:</strong> Today's slate and matchups</li>
        <li><strong>Picks:</strong> Moneyline and spread picks</li>
        <li><strong>Teams:</strong> Team selection and combos</li>
        <li><strong>Lookup:</strong> Team search and filters</li>
        <li><strong>Stats:</strong> Pick performance tracking</li>
      </ul>
    </div>
  `;
}

// ============================================================================
// MAIN RENDER ORCHESTRATOR
// ============================================================================

function render() {
  const app = document.getElementById('app');

  if (isLoading) {
    app.innerHTML = `<div class="loading">Loading slate...</div>`;
    return;
  }

  let tabContent = '';
  switch (activeTab) {
    case 'dashboard':
      tabContent = renderDashboardTab();
      break;
    case 'picks':
      tabContent = renderPicksTab();
      break;
    case 'teams':
      tabContent = renderTeamsTab();
      break;
    case 'lookup':
      tabContent = renderLookupTab();
      break;
    case 'stats':
      tabContent = renderStatsTab();
      break;
    case 'info':
      tabContent = renderInfoTab();
      break;
    default:
      tabContent = renderDashboardTab();
  }

  app.innerHTML = `
    <div class="dashboard">
      <nav class="nav">
        <button class="nav-item ${activeTab === 'dashboard' ? 'active' : ''}" onclick="switchTab('dashboard')">Dashboard</button>
        <button class="nav-item ${activeTab === 'picks' ? 'active' : ''}" onclick="switchTab('picks')">Picks</button>
        <button class="nav-item ${activeTab === 'teams' ? 'active' : ''}" onclick="switchTab('teams')">Teams</button>
        <button class="nav-item ${activeTab === 'lookup' ? 'active' : ''}" onclick="switchTab('lookup')">Lookup</button>
        <button class="nav-item ${activeTab === 'stats' ? 'active' : ''}" onclick="switchTab('stats')">Stats</button>
        <button class="nav-item ${activeTab === 'info' ? 'active' : ''}" onclick="switchTab('info')">Info</button>
      </nav>
      ${tabContent}
    </div>
  `;
}

function switchTab(tab) {
  activeTab = tab;
  render();
}

// ============================================================================
// INITIALIZATION
// ============================================================================

async function init() {
  await initializeDashboard();
  render();
}

// Start on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
