const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'app.js'), 'utf8').replace(/\nloadAllData\(\);\s*$/, '\n');
const css = fs.readFileSync(path.join(root, 'styles.css'), 'utf8');

// Deliberately synthetic values, never fetched or published as football data.
const seed = `
Object.assign(st, {
  player:'Fixture Receiver', mode:'skill', metric:'REC', line:'4.5',
  activeTab:'dashboard', loading:false, dataVersion:1,
  tonight:[{player_name:'Fixture Receiver',team_abbr:'SEA',opp_abbr_tonight:'SF',pos:'WR'}],
  schedule:[
    {home_abbr:'SEA',away_abbr:'SF',game_date:'2026-09-13',game_time:'16:25',stadium:'Fixture stadium',spread_line:3,total_line:44},
    {home_abbr:'PHI',away_abbr:'DAL',game_date:'2026-11-22',game_time:'20:20'}
  ],
  gameLogs:Array.from({length:12},(_,i)=>({
    player_name:'Fixture Receiver',team_abbr:'SEA',opp_abbr:i%3===0?'SF':'ARI',
    game_date:'2025-12-'+String(28-i).padStart(2,'0'),season:2025,week:18-i,
    home_away:i%2?'AWAY':'HOME',REC:i%8,REC_YDS:20+i*7,TGT:4+i%7,RUSH_YDS:0,UD_FP:10+i,ANY_TD:i%2
  })),
  props:[{PLAYER_NAME:'Fixture Receiver',METRIC:'REC',DK_LINE:4.5,OVER_ODDS:-110,UNDER_ODDS:-110,LAST_UPDATED:'2026-09-12'}]
});
resetDerived();
`;
function harness() {
  const FixedDate = class extends Date {
    constructor(...args) { super(...(args.length ? args : ['2026-11-19T12:00:00Z'])); }
    static now() { return Date.parse('2026-11-19T12:00:00Z'); }
  };
  const context = vm.createContext({console, Date:FixedDate, localStorage:{getItem:()=>null,setItem:()=>{}}, window:{}, document:{getElementById:()=>null}});
  vm.runInContext(source + seed, context);
  return context;
}

test('research renders actual equal-column hierarchy, dates, samples and markets', () => {
  const context = harness();
  const html = context.renderDashboardPage();
  assert.match(html,/research-grid/);
  assert.match(html,/10 matching games of 12 loaded/);
  assert.match(html,/H2H vs SF/);
  assert.match(html,/Home \/ Away/);
  assert.match(html,/n=4/);
  assert.match(html,/2026-09-13/);
  assert.match(html,/Locked \/ started/);
  assert.match(html,/2026-11-22/);
  assert.ok(html.indexOf('research-averages-panel') > html.indexOf('research-chart-panel'));
  assert.ok(html.indexOf('research-splits') > html.indexOf('research-averages-panel'));
  assert.ok(html.indexOf('research-matchup') > html.indexOf('research-splits'));
  assert.ok(html.indexOf('research-markets') > html.indexOf('research-matchup'));
  assert.match(html,/<details class="research-context-details">/);
  assert.doesNotMatch(html,/Model context|Skill-player analysis/);
  const averages=html.slice(html.indexOf('research-averages-panel'),html.indexOf('research-splits'));
  assert.match(averages,/Season[\s\S]*L10[\s\S]*L5[\s\S]*Last/);
  assert.match(html,/mini-bars-container/);
  assert.match(css,/\.research-averages\{display:grid;grid-template-columns:repeat\(4,minmax\(0,1fr\)\)/);
  assert.match(css,/\.research-grid\{display:grid;grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
  assert.match(css,/\.analysis-chart\{background:transparent;border:0/);
  if(process.env.NFL_RESEARCH_PREVIEW) {
    const interactive = source + seed + `
      render=function(){document.getElementById('preview').innerHTML=renderDashboardPage()};
    `;
    fs.writeFileSync('/tmp/nfl-research-preview.html', `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NFL Research Fixture</title><style>${css}</style></head><body><p style="padding:12px 16px">SYNTHETIC TEST FIXTURE: 12 logs, SEA/SF locked September matchup. Not live player data.</p><div id="preview">${html}</div><script>${interactive.replaceAll('</script', '<\\/script')}</script></body></html>`);
    console.log('Preview exported: /tmp/nfl-research-preview.html');
  }
});

test('filters compose before range, exclude unknown venues, and do not mutate history', () => {
  const c = harness();
  const rows = vm.runInContext('st.gameLogs',c);
  const before = JSON.stringify(rows);
  assert.equal(c.researchChartLogs(rows,'5','ALL','ALL','SEA').length,5);
  assert.equal(c.researchChartLogs(rows,'SEASON','SF','HOME','SEA').length,2);
  assert.equal(c.researchChartLogs(rows,'SEASON','ALL','AWAY','SEA').length,6);
  assert.equal(c.researchChartLogs(rows,'10','MISSING','ALL','SEA').length,0);
  assert.equal(c.researchChartLogs([{REC:1}],'10','ALL','HOME','SEA').length,0);
  assert.equal(JSON.stringify(rows),before);
  vm.runInContext('render=()=>{};st.oppFilter="ARI";st.showFullLog=true',c);
  c.setResearchFilter('chartRange','5');
  c.setResearchFilter('chartOpponent','SF');
  c.setResearchFilter('chartVenue','HOME');
  const html=c.renderDashboardPage();
  assert.match(html,/2 matching games of 12 loaded/);
  assert.match(html,/n=12/);
  assert.equal(vm.runInContext('st.oppFilter',c),'ARI');
  assert.equal(vm.runInContext('st.showFullLog',c),true);
  assert.match(html,/8 matching games loaded/);
});

test('missing metrics remain unavailable, zero is real, empty filters are honest', () => {
  const c=harness();
  assert.equal(c.researchMetricValue({},'REC'),null);
  assert.equal(c.researchMetricValue({REC:''},'REC'),null);
  assert.equal(c.researchMetricValue({REC:'bad'},'REC'),null);
  assert.equal(c.researchMetricValue({REC:0},'REC'),0);
  vm.runInContext('st.chartOpponent="MISSING"',c);
  assert.match(c.renderDashboardPage(),/No games match these chart filters/);
  vm.runInContext('st.gameLogs=[];st.schedule=[];st.dataVersion++',c);
  const html=c.renderDashboardPage();
  assert.match(html,/n=0/);
  assert.match(html,/Start unconfirmed/);
  assert.doesNotMatch(html,/Upcoming/);
});

test('mixed seasons stay labelled as loaded history and QB metrics render', () => {
  const c=harness();
  vm.runInContext('st.gameLogs[0].season=2024;st.dataVersion++',c);
  let html=c.renderDashboardPage();
  assert.match(html.slice(html.indexOf('research-averages-panel'),html.indexOf('research-splits')),/Loaded history/);
  vm.runInContext(`st.mode='qb';st.metric='PASS_YDS';st.props=[];st.pTonight=st.tonight;
    st.pGameLogs=st.gameLogs.map(row=>({...row,PASS_YDS:240,PASS_TDS:2,COMP:20}));
    st.chartVenue='AWAY';st.line=0;st.dataVersion++;`,c);
  html=c.renderDashboardPage();
  assert.match(html,/6 matching games of 12 loaded/);
  assert.match(html,/240.0/);
  assert.match(html,/Reference line 0/);
  assert.match(html,/n=12/);
});
