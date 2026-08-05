const ICONS = {
  dash:   '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="5" height="7"/><rect x="9" y="2" width="5" height="4"/><rect x="9" y="8" width="5" height="6"/><rect x="2" y="11" width="5" height="3"/></svg>',
  log:    '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h10v10H3z"/><path d="M5.5 6h5M5.5 8.5h5M5.5 11h3"/></svg>',
  picks:  '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5.5"/><circle cx="8" cy="8" r="2"/></svg>',
  stats:  '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 13V6"/><path d="M6 13V3"/><path d="M10 13V8"/><path d="M14 13V5"/></svg>',
  leaders:'<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 13h12"/><path d="M3 13V9h3v4M6.5 13V5h3v8M10 13V7h3v6"/></svg>',
  entry:  '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2 5.5h12v5H2z"/><path d="M6 5.5v5M10 5.5v5"/></svg>',
  lookup: '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="7" cy="7" r="4.5"/><path d="M10.5 10.5L14 14"/></svg>',
  info:   '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"/><path d="M8 7v4M8 5v0.1"/></svg>',
  refresh: '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M13 8a5 5 0 1 1-1.5-3.5"/><path d="M13 3v3h-3"/></svg>',
  moon:   '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M13 9.5A5.5 5.5 0 1 1 6.5 3a4.5 4.5 0 0 0 6.5 6.5z"/></svg>',
  sun:    '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="3"/><path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.3 3.3l1.4 1.4M11.3 11.3l1.4 1.4M3.3 12.7l1.4-1.4M11.3 4.7l1.4-1.4"/></svg>',
  bat:    '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 13.5L11 5"/><path d="M9 3l4 4"/></svg>',
  ball:   '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="5.5"/><path d="M4.5 5.5c1.5 0.5 2.5 1.5 3 3M11.5 10.5c-1.5-0.5-2.5-1.5-3-3"/></svg>',
  lock:   '<svg viewBox="0 0 16 16" width="10" height="10" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="7" width="9" height="6" rx="1"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2"/></svg>',
  warn:   '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2l6 11H2z"/><path d="M8 6.5v3.5M8 12v0.1"/></svg>'
};
function icon(name){return `<span class="icon-inline">${ICONS[name]||''}</span>`}
const SHEET_ID="1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0";

const GAME_ENTRY_TIER_WEIGHTS = { SMASH: 1.5, STRONG: 1.0, LEAN: 0.7 };
const GAME_ENTRY_DEFAULT_WLB = 0.42;
const GAME_ENTRY_MIN_LEGS = 2;
const GAME_ENTRY_MAX_LEGS = 8;
const GAME_ENTRY_DEFAULT_LEGS = 5;
const GAME_ENTRY_MAX_LEGS_PER_PLAYER = 3;
const SOFT_LINE_CENTS_THRESHOLD = 5;
const SOFT_LINE_PP_THRESHOLD = 3.0;
const SOFT_LINE_MIN_AGREEMENT = 2;
const SOFT_LINE_MIN_BOOKS = 2;
const SOFT_LINE_BOOKS = ['fanduel', 'betmgm', 'espnbet'];
const MARKET_EDGE_MIN_ODDS = -250;
const METRICS=["REC","REC_YDS","TGT","RUSH_YDS","CARRIES","REC_TDS","RUSH_TDS","ANY_TD","UD_FP"];
const P_METRICS=["PASS_YDS","PASS_TDS","COMP","ATT","INT","RUSH_YDS","UD_FP"];
const MLB_API="https://statsapi.mlb.com/api/v1";
const SHORTLIST_TRAY_KEY="nfl-shortlist-tray";
const DRAFT_SLATE_KEY="nfl-draft-slate-v1";

function loadShortlistTray(){
  try{
    const parsed=JSON.parse(localStorage.getItem(SHORTLIST_TRAY_KEY)||"[]");
    return Array.isArray(parsed)?parsed:[];
  }catch(e){return[]}
}

function loadDraftSlate(){
  try{
    const parsed=JSON.parse(localStorage.getItem(DRAFT_SLATE_KEY)||"{}");
    return{
      signature:String(parsed.signature||""),
      selectedIds:new Set(Array.isArray(parsed.selectedIds)?parsed.selectedIds.map(String):[])
    };
  }catch(e){return{signature:"",selectedIds:new Set()}}
}

const BEST_BALL_DRAFTED_KEY="nfl-bestball-drafted-v1";
const BEST_BALL_TAKEN_KEY="nfl-bestball-taken-v1";
const BEST_BALL_QUEUE_KEY="nfl-bestball-queue-v1";
function loadBestBallDrafted(){
  try{
    const parsed=JSON.parse(localStorage.getItem(BEST_BALL_DRAFTED_KEY)||"[]");
    return new Set(Array.isArray(parsed)?parsed.map(String):[]);
  }catch(e){return new Set()}
}
function saveBestBallDrafted(){
  try{localStorage.setItem(BEST_BALL_DRAFTED_KEY,JSON.stringify([...st.bbDrafted]))}catch(e){}
}
function loadBestBallTaken(){
  try{
    const parsed=JSON.parse(localStorage.getItem(BEST_BALL_TAKEN_KEY)||"[]");
    return new Set(Array.isArray(parsed)?parsed.map(String):[]);
  }catch(e){return new Set()}
}
function saveBestBallTaken(){
  try{localStorage.setItem(BEST_BALL_TAKEN_KEY,JSON.stringify([...st.bbTaken]))}catch(e){}
}
function loadBestBallQueue(){
  try{
    const parsed=JSON.parse(localStorage.getItem(BEST_BALL_QUEUE_KEY)||"[]");
    return new Set(Array.isArray(parsed)?parsed.map(String):[]);
  }catch(e){return new Set()}
}
function saveBestBallQueue(){
  try{localStorage.setItem(BEST_BALL_QUEUE_KEY,JSON.stringify([...st.bbQueue]))}catch(e){}
}

const initialDraftSlate=loadDraftSlate();
let st={
  tonight:[],gameLogs:[],splits:[],weather:[],pitchers:[],schedule:[],
  pTonight:[],pGameLogs:[],pSplits:[],
  picks:[],picksHistory:[],props:[],allBooksProps:[],teamRankings:[],
  pickPerformance:[],pickPerformanceSnaps:[],statsTimeWindow:"last_30d",statsLeaderMetric:"REC",leaderMode:"final",leaderDateOffset:0,gameEntry:{selectedGame:null,legCount:GAME_ENTRY_DEFAULT_LEGS,entry:null},
  shortlistTray:loadShortlistTray(),shortlistTrayNotice:"",
  mode:"skill",
  player:"",metric:"REC",line:"",activeTab:"picks",oppFilter:"",showFullLog:false,
  playerSearch:"",playerSuggestions:[],showPlayerSugs:false,
  loading:true,error:null,dataWarnings:[],lookupError:"",loadedAt:null,latestPickDate:"",pickGuard:null,
  picksView:"shortlist",propsMetric:"ALL",propsSearch:"",propsTeam:"ALL",propsSort:"EDGE",propsMinHit:"0",propsMinEdge:"5",
  streakFilter:"all",drafted:new Set(),slipLegs:"3",
  draftSlate:{signature:initialDraftSlate.signature,selectedIds:initialDraftSlate.selectedIds,panelOpen:false},
  projections:[],bbPos:"ALL",bbSort:"VORP",bbHideDrafted:false,bbDrafted:loadBestBallDrafted(),bbTaken:loadBestBallTaken(),bbQueue:loadBestBallQueue(),bbSearch:"",bbTeam:"ALL",bbDraftableOnly:true,bbScoring:"half",
  vsSP:[],
  lkPlayer:null,lkResults:[],lkQuery:"",lkSubTab:"career",lkPlayerType:"skill",
  lkCareer:null,lkYby:null,lkVsTeamStats:null,lkVsPlayerId:null,
  lkVsPlayerName:"",lkVsPlayerResults:[],lkVsPlayerStats:null,
  lkVsTeamId:null,lkLoading:{},lkTeamList:[],
  dataVersion:0,
  theme:(localStorage.getItem("nfl-dashboard-theme")||"dark")
};
function reportNonFatal(context,error,userMessage=""){
  console.warn(`⚠️ ${context}`,error);
  if(userMessage&&!st.dataWarnings.includes(userMessage))st.dataWarnings.push(userMessage);
}
function fetchOptionalSheet(name,userMessage=""){
  return fetchSheet(name).catch(error=>{
    reportNonFatal(`Optional sheet unavailable: ${name}`,error,userMessage);
    return[];
  });
}
function renderDataWarnings(){
  if(!st.dataWarnings.length)return"";
  const visible=st.dataWarnings.slice(0,2);
  const extra=st.dataWarnings.length-visible.length;
  return `<div class="data-warning" role="status"><strong>Limited data:</strong> ${visible.map(esc).join(" " )}${extra?` <span>+${extra} more source${extra===1?"":"s"} unavailable.</span>`:""}<button type="button" onclick="loadAllData()">Retry</button></div>`;
}
function applyTheme(){document.body.classList.toggle("light-theme",st.theme==="light")}
function toggleTheme(){st.theme=st.theme==="light"?"dark":"light";localStorage.setItem("nfl-dashboard-theme",st.theme);applyTheme();render()}

let derived={
  version:-1,
  batterLogsByName:new Map(),
  pitcherLogsByName:new Map(),
  propsByName:new Map(),
  tonightByName:new Map(),
  pTonightByName:new Map(),
  latestPickDate:"",
  latestPickRun:0,
  picksByNameLatest:new Map(),
  memo:new Map()
};

function resetDerived(){
  derived={
    version:-1,
    batterLogsByName:new Map(),
    pitcherLogsByName:new Map(),
    propsByName:new Map(),
    tonightByName:new Map(),
    pTonightByName:new Map(),
    latestPickDate:"",
    latestPickRun:0,
    picksByNameLatest:new Map(),
    memo:new Map()
  };
}

function indexRowsByName(rows,nameKey){
  const map=new Map();
  for(const row of rows||[]){
    const key=normalizePlayerName(row?.[nameKey]);
    if(!key)continue;
    if(!map.has(key))map.set(key,[]);
    map.get(key).push(row);
  }
  return map;
}

function ensureDerived(){
  if(derived.version===st.dataVersion)return;
  resetDerived();
  derived.version=st.dataVersion;
  derived.batterLogsByName=indexRowsByName(st.gameLogs,"player_name");
  derived.pitcherLogsByName=indexRowsByName(st.pGameLogs,"player_name");
  for(const logs of derived.batterLogsByName.values())logs.sort((a,b)=>(b.game_date||"").localeCompare(a.game_date||""));
  for(const logs of derived.pitcherLogsByName.values())logs.sort((a,b)=>(b.game_date||"").localeCompare(a.game_date||""));
  derived.propsByName=indexRowsByName(st.props,"PLAYER_NAME");
  for(const row of st.tonight||[]){
    const key=normalizePlayerName(row?.player_name);
    if(key&&!derived.tonightByName.has(key))derived.tonightByName.set(key,row);
  }
  for(const row of st.pTonight||[]){
    const key=normalizePlayerName(row?.player_name);
    if(key&&!derived.pTonightByName.has(key))derived.pTonightByName.set(key,row);
  }
  const allDates=[...new Set((st.picks||[]).map(p=>normalizeDate(rowField(p,"DATE"))).filter(Boolean))].sort();
  derived.latestPickDate=allDates.length?allDates[allDates.length-1]:"";
  const sameDatePicks=(st.picks||[]).filter(p=>normalizeDate(rowField(p,"DATE"))===derived.latestPickDate);
  derived.latestPickRun=sameDatePicks.length?Math.max(...sameDatePicks.map(p=>toNum(rowField(p,"RUN_NUMBER")))):0;
  for(const p of st.picks||[]){
    const key=normalizePlayerName(p?.player);
    if(!key)continue;
    if(normalizeDate(rowField(p,"DATE"))===derived.latestPickDate && toNum(rowField(p,"RUN_NUMBER"))===derived.latestPickRun && !derived.picksByNameLatest.has(key)){
      derived.picksByNameLatest.set(key,p);
    }
  }
}

function getMemo(key,build){
  ensureDerived();
  const memoKey=`${st.dataVersion}:${key}`;
  if(derived.memo.has(memoKey))return derived.memo.get(memoKey);
  const value=build();
  derived.memo.set(memoKey,value);
  return value;
}

function getPlayerLogs(name,isP){
  ensureDerived();
  const key=normalizePlayerName(name);
  return (isP?derived.pitcherLogsByName:derived.batterLogsByName).get(key)||[];
}

function getTonightPlayerRow(name,isP){
  ensureDerived();
  const key=normalizePlayerName(name);
  return (isP?derived.pTonightByName:derived.tonightByName).get(key)||null;
}

function cleanRows(rows){
  if(!rows||!rows.length)return rows;
  return rows.map(row=>{
    const clean={};
    for(const[k,v]of Object.entries(row)){
      const ck=k.replace(/^\uFEFF/,'').replace(/[\u200B-\u200D\uFEFF]/g,'').trim();
      clean[ck]=v;
    }
    return clean;
  });
}

function normalizeKeys(rows){
  if(!rows||!rows.length)return rows;
  return rows.map(row=>{
    const clean={};
    for(const[k,v]of Object.entries(row)){
      const trimmed=String(k||'')
        .replace(/^\uFEFF/,'')
        .replace(/[\u200B-\u200D\uFEFF]/g,'')
        .trim();
      clean[trimmed]=v;
    }
    return clean;
  });
}

function canonicalFieldKey(key){
  return String(key||"")
    .replace(/^\uFEFF/,'')
    .replace(/[\u200B-\u200D\uFEFF]/g,'')
    .trim()
    .replace(/([a-z0-9])([A-Z])/g,'$1_$2')
    .replace(/[^A-Za-z0-9]+/g,'_')
    .replace(/^_+|_+$/g,'')
    .toLowerCase();
}

function rowField(row,...names){
  if(!row)return "";
  for(const name of names){
    if(Object.prototype.hasOwnProperty.call(row,name))return row[name];
  }
  const lookup={};
  for(const [key,value] of Object.entries(row)){
    const ck=canonicalFieldKey(key);
    if(ck&&!Object.prototype.hasOwnProperty.call(lookup,ck))lookup[ck]=value;
  }
  for(const name of names){
    const ck=canonicalFieldKey(name);
    if(Object.prototype.hasOwnProperty.call(lookup,ck))return lookup[ck];
  }
  return "";
}

// Asking gviz for a tab that does not exist returns HTTP 200 containing the
// FIRST sheet's data — it does not 404. Without a check, every missing tab
// silently loads the wrong rows, which is worse than an error because nothing
// looks broken. Column fingerprints aren't enough either: Schedule and Games
// share game_id, so an overlap would false-pass. The engine therefore stamps
// every tab with a `_tab` sentinel column naming itself, and we verify it.
function verifyTabIdentity(name,rows,fields){
  if(!rows.length)return;
  // Fail CLOSED. The engine stamps _tab on every tab it writes, so a missing
  // sentinel means we were served something else — most likely the first sheet
  // via the gviz fallback, or a tab written by an older engine build. Returning
  // early here would silently accept exactly the wrong data we're guarding
  // against, which is how "every tab has 272 rows" happens.
  if(!fields||!fields.includes("_tab")){
    throw new Error(`Unverifiable sheet "${name}": no _tab sentinel. Re-run the engine.`);
  }
  const got=String(rows[0]._tab||"").trim();
  if(got!==name){
    throw new Error(`Wrong sheet: asked for "${name}", got "${got}" (tab likely missing)`);
  }
}

function fetchSheet(name,attempt=1){
  return new Promise((res,rej)=>{
    const url=`https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv&headers=1&sheet=${encodeURIComponent(name)}&cacheBust=${Date.now()}_${attempt}`;
    fetch(url,{cache:"no-store"})
    .then(r=>{
      if(!r.ok){console.error(`❌ Sheet fetch failed: ${name} (${r.status})`);throw new Error(`Failed: ${name} (${r.status})`)}
      return r.text()
    })
    .then(text=>{
      if(!text||!text.trim())throw new Error(`Empty response: ${name}`);
      Papa.parse(text,{header:true,skipEmptyLines:true,dynamicTyping:true,complete:r=>{
        try{verifyTabIdentity(name,r.data,r.meta.fields)}catch(e){rej(e);return}
        console.log(`✅ ${name}: ${r.data.length} rows, cols: ${r.meta.fields?.slice(0,5).join(', ')}...`);
        res(r.data);
      },error:e=>{console.error(`❌ Parse error: ${name}`,e);rej(e)}});
    })
    .catch(e=>{
      console.error(`❌ Fetch error: ${name} (attempt ${attempt})`,e);
      if(attempt<3){
        setTimeout(()=>fetchSheet(name,attempt+1).then(res).catch(rej),300*attempt);
      }else{
        rej(new Error(`Sheet load failed: ${name}`));
      }
    });
  });
}

const toNum=v=>parseFloat(v)||0;
function outsToIPStr(outs){const w=Math.floor(outs/3);const r=outs%3;return r===0?w+".0":w+"."+r;}
const clearsPropLine=(v,l,lean="OVER")=>lean==="UNDER"?v<l:v>l;
const barColor=(v,l,lean="OVER")=>!l?"var(--accent)":v===l?"var(--push)":clearsPropLine(v,l,lean)?"var(--over)":"var(--under)";
const avgColor=(v,l,lean="OVER")=>!l?"var(--accent)":clearsPropLine(v,l,lean)?"var(--accent)":"#f97316";
const esc=s=>{if(!s)return"";return String(s).replace(/[&<>'"]/g,t=>({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[t]))};
const fmtOdds=v=>{if(!v&&v!==0)return"—";v=parseInt(v);return v>0?`+${v}`:`${v}`};
function cleanName(v){return String(v||"").trim()}
function normalizeDate(val){
  const s=String(val||"").trim();
  if(!s)return"";
  if(/^\d{4}-\d{2}-\d{2}$/.test(s))return s;
  if(/^\d{4}\/\d{2}\/\d{2}$/.test(s))return s.replace(/\//g,"-");
  const mdy=s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if(mdy){const[,m,d,y]=mdy;return`${y}-${String(m).padStart(2,"0")}-${String(d).padStart(2,"0")}`;}
  const parsed=new Date(s);
  if(!Number.isNaN(parsed.getTime()))return`${parsed.getFullYear()}-${String(parsed.getMonth()+1).padStart(2,"0")}-${String(parsed.getDate()).padStart(2,"0")}`;
  return s;
}
function fmtNowEastern(){
  return new Date().toLocaleString("en-US",{timeZone:"America/New_York",month:"2-digit",day:"2-digit",year:"numeric",hour:"numeric",minute:"2-digit",hour12:true}).replace(",","") + " EST";
}
function parseStartMs(v){
  if(!v)return null;
  const d=new Date(v);
  return Number.isNaN(d.getTime())?null:d.getTime();
}
function getScheduleRow(team,opp){
  const t=String(team||"").trim().toUpperCase();
  const o=String(opp||"").trim().toUpperCase();
  if(!t||!o||!Array.isArray(st.schedule))return null;
  return st.schedule.find(r=>{
    const home=String(rowField(r,"home_abbr")).trim().toUpperCase();
    const away=String(rowField(r,"away_abbr")).trim().toUpperCase();
    return (home===t&&away===o)||(home===o&&away===t);
  })||null;
}
function getScheduleStartMs(team,opp){
  const row=getScheduleRow(team,opp)||{};
  return parseStartMs(rowField(row,"game_time","commence_time","start_time"));
}
function getLockInfo(name,isP){
  const row=getTonightPlayerRow(name,!!isP)||{};
  const startMs=getScheduleStartMs(rowField(row,"team_abbr"),rowField(row,"opp_abbr_tonight","tonight_opp","opp_abbr"));
  return{started:!!(startMs&&Date.now()>=startMs),startMs,row};
}
function lockBadge(name,isP){
  return getLockInfo(name,isP).started?`<span class="locked-badge">${icon('lock')}LOCKED</span>`:"";
}
function isTruthyFlag(v){return v===true||v===1||String(v||"").trim().toUpperCase()==="TRUE"}
function getSampleFlags(name,isP){
  const row=getTonightPlayerRow(name,!!isP)||{};
  return{
    returning:isTruthyFlag(rowField(row,"RETURNING")),
    limited:isTruthyFlag(rowField(row,"LIMITED_SAMPLE")),
    l5Games:toNum(rowField(row,"L5_GAMES_PLAYED")),
    gamesLast7d:toNum(rowField(row,"GAMES_LAST_7D"))
  };
}
function riskBadges(name,isP,{showLimited=true}={}){
  const f=getSampleFlags(name,isP);const out=[];
  if(f.returning)out.push(`<span class="risk-badge risk-returning">${icon('warn')}RETURNING</span>`);
  if(showLimited&&f.limited)out.push(`<span class="risk-badge risk-limited">${icon('warn')}LIMITED SAMPLE</span>`);
  return out.join("");
}
function pickFooterStatus(locked,flags,pending){
  const states=[];
  if(locked)states.push("LOCKED");
  if(flags.returning)states.push("RETURNING");
  if(flags.limited)states.push("LIMITED SAMPLE");
  if(pending)states.push("PENDING");
  return states.length?`<div class="pick-footer"><span class="pick-footer-status">${states.join(" · ")}</span></div>`:"";
}
function normalizePlayerName(name){
  return cleanName(name).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[’'`\.]/g,'').replace(/[^a-z0-9]+/g,' ').replace(/\s+/g,' ').trim();
}
function normalizePropMetric(metric){
  const m=String(metric||"").trim().toUpperCase().replace(/\s+/g,"");
  return m==="BATTER_SO"?"SO":m;
}
function propTypeLabel(metric){
  const m=String(metric||"").trim().toUpperCase();
  const labels={H:"hits",R:"runs",P_SO:"strikeouts",P_ER:"earned runs",P_BB:"walks"};
  return labels[m]||m.toLowerCase();
}
function normalizeLeanText(lean){
  const l=String(lean||"").trim().toUpperCase();
  return l==="FADE"?"UNDER":l;
}
function normalizeConfidence(conf){
  const v=cleanName(conf).toUpperCase();
  return v==="SMASH"||v==="STRONG"||v==="LEAN"?v:"LEAN";
}
function aiAgreesWithBet(aiPick,betLikeObject){
  if(!aiPick||!betLikeObject)return false;
  return normalizePlayerName(rowField(aiPick,"player","PLAYER_NAME"))===normalizePlayerName(rowField(betLikeObject,"name","player","PLAYER_NAME"))
    && normalizePropMetric(rowField(aiPick,"prop_type","METRIC"))===normalizePropMetric(rowField(betLikeObject,"metric","prop_type","METRIC"))
    && normalizeLeanText(rowField(aiPick,"lean"))===normalizeLeanText(rowField(betLikeObject,"lean"));
}
function easternTodayISO(){return new Date().toLocaleDateString('en-CA',{timeZone:'America/New_York'})}
function getPickGuard(latestDate,picksCount){
  const tonightCount=st.mode==="qb"?st.pTonight.length:st.tonight.length;
  if(!tonightCount)return null;
  const today=easternTodayISO();
  if(!picksCount){
    return st.props.length
      ?{level:"warn",text:"Engine issue — model picks are missing or incomplete for this week's slate."}
      :{level:"info",text:"No model picks for this week yet. Props may still be loading."};
  }
  if(latestDate&&latestDate!==today)return{level:"warn",text:`Showing stale model picks from ${latestDate}. Engine may be incomplete.`};
  if(picksCount<3&&st.props.length>=12)return{level:"warn",text:`Model picks look incomplete for this week (${picksCount} loaded).`};
  return null;
}
function renderPickGuard(guard){
  if(!guard)return"";
  const border=guard.level==="warn"?"var(--warn)":"var(--ink-muted)";
  const text=guard.level==="warn"?"#fcd34d":"var(--ink-1)";
  return `<div class="section" style="margin-bottom:12px"><div class="card" style="border-left:3px solid ${border}"><div style="font-size:var(--t-xs);color:${text};font-weight:600">${esc(guard.text)}</div></div></div>`;
}
function parseEasternTimestamp(value){
  const raw=String(value||"").trim();
  if(!raw)return null;
  const match=raw.match(/^(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?\s*(?:EST|EDT)?$/i);
  if(match){
    let hour=Number(match[4]);
    const ampm=(match[7]||"").toUpperCase();
    if(ampm==="PM"&&hour<12)hour+=12;
    if(ampm==="AM"&&hour===12)hour=0;
    const wallUtc=Date.UTC(Number(match[1]),Number(match[2])-1,Number(match[3]),hour,Number(match[5]),Number(match[6]||0));
    const probe=new Date(wallUtc);
    const easternParts=new Intl.DateTimeFormat("en-US",{timeZone:"America/New_York",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",hourCycle:"h23"}).formatToParts(probe);
    const part=type=>Number(easternParts.find(p=>p.type===type)?.value||0);
    const represented=Date.UTC(part("year"),part("month")-1,part("day"),part("hour"),part("minute"),part("second"));
    return wallUtc+(wallUtc-represented);
  }
  const parsed=new Date(raw);
  return Number.isNaN(parsed.getTime())?null:parsed.getTime();
}
function latestDataTimestamp(rows,fields=["LAST_UPDATED"]){
  let latest=null;
  for(const row of rows||[]){
    for(const field of fields){
      const ms=parseEasternTimestamp(rowField(row,field));
      if(ms!==null&&(latest===null||ms>latest))latest=ms;
    }
  }
  return latest;
}
function freshnessAgeLabel(ms){
  if(ms===null)return"No data";
  const minutes=Math.max(0,Math.round((Date.now()-ms)/60000));
  if(minutes<2)return"just now";
  if(minutes<60)return`${minutes}m ago`;
  const hours=Math.round(minutes/60);
  if(hours<24)return`${hours}h ago`;
  return`${Math.round(hours/24)}d ago`;
}
function freshnessSignal(label,rows,{warnHours,staleHours,fields=["LAST_UPDATED"]}){
  const ms=latestDataTimestamp(rows,fields);
  if(ms===null)return{label,level:"missing",value:"No data"};
  const ageHours=Math.max(0,(Date.now()-ms)/3600000);
  const level=ageHours>=staleHours?"stale":ageHours>=warnHours?"warn":"fresh";
  return{label,level,value:freshnessAgeLabel(ms)};
}
function getModelFreshness(){
  const latestDate=getLatestPickDate(),latestRun=getLatestPickRun();
  const currentPicks=(st.picks||[]).filter(p=>normalizeDate(rowField(p,"DATE"))===latestDate&&toNum(rowField(p,"RUN_NUMBER"))===latestRun);
  return[
    freshnessSignal("Model picks",currentPicks,{warnHours:8,staleHours:20,fields:["LAST_UPDATED","RUN_TIME"]}),
    freshnessSignal("Sportsbook markets",st.props,{warnHours:3,staleHours:8}),
    freshnessSignal("Batter logs",st.gameLogs,{warnHours:18,staleHours:36}),
    freshnessSignal("Probable starters",st.pTonight,{warnHours:4,staleHours:10}),
  ];
}
function renderModelFreshness(){
  return `<div class="freshness-strip">${getModelFreshness().map(signal=>`<div class="freshness-item ${signal.level}"><div class="freshness-label">${esc(signal.label)}</div><div class="freshness-value"><span class="freshness-dot"></span>${esc(signal.value)}</div></div>`).join("")}</div>`;
}
function compactRunTime(value){
  const ms=parseEasternTimestamp(value);
  if(ms===null)return value?String(value):"Time unavailable";
  return new Date(ms).toLocaleString("en-US",{
    timeZone:"America/New_York",month:"short",day:"numeric",
    hour:"numeric",minute:"2-digit",hour12:true
  });
}
function getModelRunHealth(rows){
  const picks=rows||[];
  if(!picks.length)return[
    {label:"Engine run",value:"No snapshot",meta:"Waiting for current picks",level:"missing"},
    {label:"Snapshot",value:"0 picks",meta:"No active cohort",level:"missing"},
    {label:"Playable",value:"0",meta:"No slate-ready picks",level:"missing"},
    {label:"Validated / research",value:"0 / 0",meta:"No selections",level:"missing"},
    {label:"Gemini delivery",value:"No output",meta:"Target 14 reviewed picks",level:"missing"},
  ];
  const runNumber=Math.max(...picks.map(p=>toNum(rowField(p,"RUN_NUMBER"))||0));
  const runTime=picks.map(p=>rowField(p,"RUN_TIME")||rowField(p,"LAST_UPDATED")).find(Boolean);
  const playable=picks.filter(p=>String(rowField(p,"RECOMMENDATION_STATUS")).trim().toUpperCase()==="PLAYABLE").length;
  const research=picks.filter(p=>String(rowField(p,"RECOMMENDATION_STATUS")).trim().toUpperCase()==="RESEARCH").length;
  const validated=picks.filter(p=>String(rowField(p,"SELECTION_METHOD")||rowField(p,"CONSENSUS_TAG")).toUpperCase().includes("VALIDATED")).length;
  const backfills=picks.filter(p=>{
    const text=`${rowField(p,"CONSENSUS_TAG")} ${rowField(p,"rationale")} ${rowField(p,"reasoning")}`.toUpperCase();
    return text.includes("BACKFILL");
  }).length;
  const geminiReviewed=Math.max(0,picks.length-validated);
  const target=14;
  const deliveryLevel=geminiReviewed>=target?"good":backfills?"warn":"missing";
  const deliveryValue=geminiReviewed>=target?`${geminiReviewed}/${target} met`:`${geminiReviewed}/${target}`;
  const deliveryMeta=backfills?`${backfills} validated backfill${backfills===1?"":"s"}`:"No backfill required";
  return[
    {label:"Engine run",value:runNumber?`#${runNumber}`:"Current",meta:compactRunTime(runTime),level:"good"},
    {label:"Snapshot",value:`${picks.length} picks`,meta:"Complete current cohort",level:picks.length?"good":"missing"},
    {label:"Playable",value:String(playable),meta:`${picks.length?Math.round(playable/picks.length*100):0}% of snapshot`,level:playable?"good":"warn"},
    {label:"Validated / research",value:`${validated} / ${research}`,meta:"Model / learning cohort",level:""},
    {label:"Gemini delivery",value:deliveryValue,meta:deliveryMeta,level:deliveryLevel},
  ];
}
function renderModelRunHealth(rows){
  return `<div class="run-health-strip">${getModelRunHealth(rows).map(item=>`<div class="run-health-item ${item.level||""}"><div class="run-health-label">${esc(item.label)}</div><div class="run-health-value">${esc(item.value)}</div><div class="run-health-meta">${esc(item.meta)}</div></div>`).join("")}</div>`;
}

const COMBO_STATS={
  "H+R+RBI":["H","R","RBI"],
  "H+R":["H","R"],
  "R+RBI":["R","RBI"],
  "H+RBI":["H","RBI"],
  "1B+2B":["1B","2B"],
  "BB+H":["BB","H"],
};

function getMetricVal(g,m){
  if(COMBO_STATS[m])return COMBO_STATS[m].reduce((s,k)=>s+toNum(g[k]),0);
  return toNum(g[m]);
}
function getRollingVal(row,prefix,m){
  if(COMBO_STATS[m])return COMBO_STATS[m].reduce((s,k)=>s+toNum(row[`${prefix}${k}`]),0);
  return toNum(row[`${prefix}${m}`]);
}

function hasLogs(name,isP){return getPlayerLogs(name,isP).length>0}
function getProps(name){if(!name||!st.props.length)return[];ensureDerived();return derived.propsByName.get(normalizePlayerName(name))||[]}
function getLatestPickDate(){ensureDerived();return derived.latestPickDate}
function getLatestPickRun(){ensureDerived();return derived.latestPickRun}
function getActivePicks(){const latestDate=getLatestPickDate(),latestRun=getLatestPickRun();return (st.picks||[]).filter(p=>normalizeDate(rowField(p,"DATE"))===latestDate&&toNum(rowField(p,"RUN_NUMBER"))===latestRun)}
function getPick(name){if(!name||!st.picks.length)return null;ensureDerived();return derived.picksByNameLatest.get(normalizePlayerName(name))||null}

function firstValidPlayer(arr){
  if(!arr||!arr.length)return "";
  for(let i=0;i<Math.min(arr.length,30);i++){
    const row=arr[i];if(!row)continue;
    const n=row.player_name;
    if(n&&String(n).trim().length>1)return String(n).trim();
  }
  const first=arr[0];if(!first)return "";
  const key=Object.keys(first).find(k=>k.replace(/[^a-zA-Z_]/g,'').toLowerCase()==="player_name"||k.includes("player_name"));
  if(key){
    for(let i=0;i<Math.min(arr.length,30);i++){
      const v=arr[i]?.[key];
      if(v&&String(v).trim().length>1)return String(v).trim();
    }
  }
  console.warn("⚠️ Could not find player_name. Keys:",Object.keys(first).slice(0,5));
  return "";
}

let _restoring=false;
function saveFocus(){const el=document.activeElement;if(el&&el.id)return{id:el.id,pos:el.selectionStart,val:el.value};return null}
function restoreFocus(f){if(!f)return;const el=document.getElementById(f.id);if(el){_restoring=true;el.focus();if(f.val!==undefined)el.value=f.val;if(el.setSelectionRange&&f.pos!==undefined)try{el.setSelectionRange(f.pos,f.pos)}catch(e){}_restoring=false}}

let useProxy=false;
const LOOKUP_PORTED=false; // flip when Lookup is rebuilt on nflverse
async function mlbFetch(url){
  // Deliberately inert. This called statsapi.mlb.com, which has no NFL data;
  // leaving it live would search baseball players for football names.
  if(!LOOKUP_PORTED)throw new Error("Lookup is not yet ported to nflverse.");
  try{const r=await fetch(url);if(!r.ok)throw new Error(r.status);return r.json()}
  catch(e){if(!useProxy){useProxy=true;return(await fetch("https://corsproxy.io/?"+encodeURIComponent(url))).json()}throw e}
}

function switchTab(t){st.activeTab=t==="gamelog"?"dashboard":t;render()}
function switchMode(m){
  st.mode=m;
  st.metric=m==="pitcher"?"SO":"H";
  st.line="";st.oppFilter="";st.showFullLog=false;st.playerSearch="";st.playerSuggestions=[];st.showPlayerSugs=false;
  const src=m==="pitcher"?st.pTonight:st.tonight;
  st.player=firstValidPlayer(src);
  console.log(`Mode → ${m}, default player: "${st.player}", source has ${src.length} entries`);
  render();
}
function switchPicksView(v){st.picksView=v;render()}
function setPropsMetric(m){st.propsMetric=m;render()}
function setPropsTeam(v){st.propsTeam=v;render()}
function setPropsSort(v){st.propsSort=v;render()}
function setPropsMinHit(v){st.propsMinHit=v;render()}
function setPropsMinEdge(v){st.propsMinEdge=v;render()}
function getTeamRanking(teamAbbr){
  const target=String(teamAbbr||"").trim().toUpperCase();
  if(!target)return null;
  return (st.teamRankings||[]).find(row=>String(rowField(row,"TEAM_ABBR","team_abbr")||"").trim().toUpperCase()===target)||null;
}
function ordinalRank(value){
  const n=Math.round(toNum(value));
  if(!n)return"—";
  const mod100=n%100;
  const suffix=mod100>=11&&mod100<=13?"th":n%10===1?"st":n%10===2?"nd":n%10===3?"rd":"th";
  return`${n}${suffix}`;
}
function teamRankValue(row,valueKey,rankKey,{digits=2,suffix="",direction="most"}={}){
  if(!row)return"—";
  const raw=rowField(row,valueKey);
  const value=raw===""||raw===null||raw===undefined?NaN:Number(raw);
  const shown=Number.isFinite(value)?value.toFixed(digits):"—";
  const rank=ordinalRank(rowField(row,rankKey));
  return`${shown}${suffix}${rank!=="—"?` · ${rank} ${direction}`:""}`;
}
function teamDisplayName(teamAbbr){
  const abbr=String(teamAbbr||"").trim().toUpperCase();
  const row=getTeamRanking(abbr);
  return String(rowField(row,"TEAM","TEAM_NAME","team_name")||abbr).trim();
}
function optionalRowNumber(row,key){
  const raw=rowField(row,key);
  if(raw===null||raw===undefined||raw==="")return null;
  const value=Number(raw);
  return Number.isFinite(value)?value:null;
}

function getDingerBoard(){
  return getMemo("dingerBoard",()=>{
  const rows=[];
  for(const p of st.tonight){
    const name=p.player_name;if(!name)continue;
    const seasHR=toNum(p.Seas_HR);
    const l7HR=toNum(p.L7_HR);
    const l14HR=toNum(p.L14_HR);
    const pLogs=getPlayerLogs(name,false);
    if(!pLogs.length)continue;
    const totalAB=pLogs.reduce((s,g)=>s+toNum(g.AB),0);
    if(totalAB===0)continue;
    const seasHRtotal=pLogs.reduce((s,g)=>s+toNum(g.HR),0);
    const hrRate=totalAB>0?seasHRtotal/totalAB:0;
    const gamesPlayed=pLogs.length;
    const hrPerGame=gamesPlayed>0?seasHRtotal/gamesPlayed:0;
    const hrProp=st.props.find(pr=>normalizePlayerName(pr.PLAYER_NAME)===normalizePlayerName(name)&&normalizePropMetric(pr.METRIC)==="HR");
    const dkLine=hrProp?hrProp.DK_LINE:null;
    const overOdds=hrProp?parseInt(hrProp.OVER_ODDS)||null:null;
    let score=0;
    score+=hrRate*100;
    score+=l7HR*15;
    score+=l14HR*8;
    score+=seasHR*5;
    score+=hrPerGame*20;
    if(overOdds&&overOdds<0)score+=10;
    if(overOdds&&overOdds>0&&overOdds<=200)score+=5;
    const legacyScore=score;
    const modelEdgeScore=optionalRowNumber(p,"POWER_EDGE_SCORE");
    const modelOpponentAdjustment=optionalRowNumber(p,"POWER_OPP_ADJ");
    score=modelEdgeScore===null?legacyScore:modelEdgeScore;
    rows.push({
      name,team:p.team_abbr||"",opp:p.opp_abbr_tonight||"",pitcher:p.opp_pitcher_name||"TBD",
      hand:p.opp_pitcher_hand||"?",venue:p.venue_tonight||"",
      seasHR:seasHRtotal,totalAB,hrRate,hrPerGame,gamesPlayed,
      l7HR,l14HR,seasAvgHR:seasHR,
      modelOpponentAdjustment,
      dkLine,overOdds,score
    });
  }
  rows.sort((a,b)=>b.score-a.score);
  return rows.slice(0,30);
  });
}

function getKsBoard(){
  return getMemo("ksBoard",()=>{
  const rows=[];
  const leagueKPcts=(st.teamRankings||[])
    .map(row=>optionalRowNumber(row,"OFF_K_PCT"))
    .filter(value=>value!==null&&value>0);
  const leagueKPct=leagueKPcts.length
    ?leagueKPcts.reduce((sum,value)=>sum+value,0)/leagueKPcts.length
    :null;
  for(const p of st.pTonight){
    const name=p.player_name;if(!name)continue;
    const pLogs=getPlayerLogs(name,true);
    if(!pLogs.length)continue;
    const most=pLogs[0]||{};
    const seasSO=pLogs.reduce((s,g)=>s+toNum(g.SO),0);
    const totalOuts=pLogs.reduce((s,g)=>s+toNum(g.IP_OUTS),0);
    if(totalOuts===0)continue;
    const ipEquiv=totalOuts/3;
    const k9=ipEquiv>0?(seasSO*9)/ipEquiv:0;
    const gamesStarted=pLogs.length;
    const soPerStart=gamesStarted>0?seasSO/gamesStarted:0;
    const l3SO=toNum(most.L3_SO);
    const l7SO=toNum(most.L7_SO);
    const seasSOavg=toNum(most.Seas_SO);
    const seasonBaseline=seasSOavg||soPerStart;
    const recent7=l7SO||seasonBaseline;
    const recent3=l3SO||recent7;
    const projectedSO=(seasonBaseline*0.5)+(recent7*0.3)+(recent3*0.2);
    const opponentRanking=getTeamRanking(p.opp_abbr_tonight);
    const opponentKPct=optionalRowNumber(opponentRanking,"OFF_K_PCT");
    const hasMatchupRate=opponentKPct!==null&&opponentKPct>0&&Number.isFinite(leagueKPct)&&leagueKPct>0;
    const matchupFactor=hasMatchupRate
      ?Math.max(0.75,Math.min(1.25,opponentKPct/leagueKPct))
      :1;
    const adjustedProjection=projectedSO*matchupFactor;
    const projectionAdjustment=adjustedProjection-projectedSO;
    const modelEdgeScore=optionalRowNumber(p,"P_SO_EDGE_SCORE");
    const modelOpponentAdjustment=optionalRowNumber(p,"P_SO_OPP_ADJ");
    const soProp=st.props.find(pr=>normalizePlayerName(pr.PLAYER_NAME)===normalizePlayerName(name)&&normalizePropMetric(pr.METRIC)==="P_SO");
    const dkLine=soProp?soProp.DK_LINE:null;
    const overOdds=soProp?parseInt(soProp.OVER_ODDS)||null:null;
    let score=0;
    score+=k9*3;
    score+=soPerStart*4;
    score+=l3SO*2.5;
    score+=l7SO*1.5;
    if(dkLine&&soPerStart>parseFloat(dkLine))score+=8;
    if(overOdds&&overOdds<0)score+=5;
    const legacyScore=score;
    score=modelEdgeScore===null?legacyScore:modelEdgeScore;
    if(dkLine&&Number.isFinite(parseFloat(dkLine))){
      score+=(adjustedProjection-parseFloat(dkLine))*3;
    }
    rows.push({
      name,team:p.team_abbr||"",opp:p.opp_abbr_tonight||"",
      venue:p.venue_tonight||"",hand:p.throws||p.player_hand||"?",
      seasSO,totalOuts,ipEquiv,k9,soPerStart,gamesStarted,
      l3SO,l7SO,seasSOavg,projectedSO,adjustedProjection,projectionAdjustment,
      opponentKPct:hasMatchupRate?opponentKPct:null,
      modelOpponentAdjustment,
      dkLine,overOdds,score
    });
  }
  rows.sort((a,b)=>b.score-a.score);
  return rows.slice(0,15);
  });
}

// ═══ +EV ENGINE ═══
function impliedProb(odds){
  if(!odds&&odds!==0)return null;
  const o=parseInt(odds);if(isNaN(o))return null;
  return o<0?Math.abs(o)/(Math.abs(o)+100):100/(o+100);
}
function computeMedian(arr){const vals=(arr||[]).map(Number).filter(Number.isFinite).sort((a,b)=>a-b);if(!vals.length)return null;const mid=Math.floor(vals.length/2);return vals.length%2?vals[mid]:(vals[mid-1]+vals[mid])/2}
function impliedToAmerican(p){const prob=Number(p);if(!Number.isFinite(prob)||prob<=0||prob>=1)return null;return prob>=0.5?Math.round(-100*prob/(1-prob)):Math.round(100*(1-prob)/prob)}
function americanCentsDiff(odds1,odds2){const a=parseInt(odds1),b=parseInt(odds2);if(!Number.isFinite(a)||!Number.isFinite(b))return null;return Math.abs(a-b)}

function getHitRate(name,metric,line,isP){
  const logs=getPlayerLogs(name,isP);
  if(logs.length<3)return null;
  const ln=parseFloat(line);if(isNaN(ln))return null;
  const combo=COMBO_STATS[metric];
  let over=0,under=0,push=0;
  for(const g of logs){
    const val=combo?combo.reduce((s,k)=>s+toNum(g[k]),0):metric==="P_OUTS"?toNum(g.IP_OUTS):toNum(g[metric]);
    if(val>ln)over++;
    else if(val<ln)under++;
    else push++;
  }
  const nonPush=over+under;
  return{
    overRate:nonPush?over/nonPush:0,
    underRate:nonPush?under/nonPush:0,
    pushRate:logs.length?push/logs.length:0,
    over,under,push,nonPush,total:logs.length
  };
}

function propToLogCol(metric){
  if(COMBO_STATS[metric])return metric;
  const map={H:"H",TB:"TB",HR:"HR",RBI:"RBI",R:"R",SB:"SB",BB:"BB","1B":"1B","2B":"2B",Batter_SO:"SO",P_SO:"SO",P_H:"H",P_BB:"BB",P_ER:"ER",P_OUTS:"P_OUTS"};
  return map[metric]||metric;
}

function isPitcherProp(metric){return(metric||"").startsWith("P_")}
function isActionableMarketEdgeSide(metric,lean,odds){
  if(metric==="HR"&&lean!=="OVER")return false;
  const price=Number(odds);
  return Number.isFinite(price)&&price>=MARKET_EDGE_MIN_ODDS;
}

function getMarketEdges(){
  return getMemo("marketEdges",()=>{
  if(!st.props.length)return[];
  const bets=[];
  for(const p of st.props){
    const name=p.PLAYER_NAME;if(!name)continue;
    const metric=p.METRIC;
    const line=parseFloat(p.DK_LINE);if(isNaN(line))continue;
    const overOdds=parseInt(p.OVER_ODDS);
    const underOdds=parseInt(p.UNDER_ODDS);
    if(isNaN(overOdds)&&isNaN(underOdds))continue;

    const logCol=propToLogCol(metric);
    const isP=isPitcherProp(metric);
    const hr=getHitRate(name,logCol,line,isP);
    if(!hr||hr.total<3||!hr.nonPush)continue;

    const overIP=impliedProb(overOdds);
    const underIP=impliedProb(underOdds);

    let overEdge=null,underEdge=null;
    if(overIP!==null)overEdge=hr.overRate-overIP;
    if(underIP!==null)underEdge=hr.underRate-underIP;

    const candidates=[];
    if(overEdge!==null&&isActionableMarketEdgeSide(metric,"OVER",overOdds))candidates.push({lean:"OVER",edge:overEdge,odds:overOdds,ip:overIP,hitRate:hr.overRate});
    if(underEdge!==null&&isActionableMarketEdgeSide(metric,"UNDER",underOdds))candidates.push({lean:"UNDER",edge:underEdge,odds:underOdds,ip:underIP,hitRate:hr.underRate});
    if(!candidates.length)continue;
    candidates.sort((a,b)=>b.edge-a.edge||b.hitRate-a.hitRate);
    const {lean,edge,odds,ip,hitRate}=candidates[0];

    const pT=getTonightPlayerRow(name,false)||getTonightPlayerRow(name,true)||{};

    const flags=getSampleFlags(name,isP);
    bets.push({
      name,metric,line,lean,edge,odds,
      impliedProb:ip,hitRate,
      hits:lean==="OVER"?hr.over:hr.under,
      total:hr.nonPush,
      team:pT.team_abbr||"",
      opp:pT.opp_abbr_tonight||"",
      pitcher:pT.opp_pitcher_name||"",
      hand:pT.opp_pitcher_hand||"",
      dkLine:p.DK_LINE,
      overOdds:p.OVER_ODDS,
      underOdds:p.UNDER_ODDS,
      prop:p,
      isP,
      teamSlot:`${pT.team_abbr||""}${isP?":P":":B"}`,
      returning:flags.returning,
      limitedSample:flags.limited
    });
  }
  bets.sort((a,b)=>(a.returning===b.returning?b.edge-a.edge:(a.returning?1:-1)));
  return bets;
  });
}

// ═══ SMART SLIP GENERATOR ═══
function getConvictionLegs(){
  const SLIP_WORTHY=new Set(["H","HR","RBI","R","TB","SB","BB","H+R+RBI","H+R","R+RBI","P_SO","P_H","P_BB","P_ER","P_OUTS","UD_FP"]); const bets=getMarketEdges().filter(b=>b.edge>=0.05&&!b.returning&&!getLockInfo(b.name,b.isP).started).filter(b=>{   if(!SLIP_WORTHY.has(b.metric))return false;   if(b.lean==="UNDER"&&parseFloat(b.dkLine)<=0.5)return false;   return true; });
  if(!bets.length)return[];

  const latestDate=getLatestPickDate();
  const latestRun=getLatestPickRun();
  const aiMap=new Map();
  st.picks.filter(pk=>normalizeDate(rowField(pk,"DATE"))===latestDate&&toNum(rowField(pk,"RUN_NUMBER"))===latestRun).forEach(pk=>{if(pk.player){const playerKey=normalizePlayerName(pk.player);aiMap.set(playerKey,pk);aiMap.set(`${playerKey}|${normalizePropMetric(pk.prop_type)}|${normalizeLeanText(pk.lean)}`,pk)}});
  const streakMap=new Map();
  try{
    const streaks=getStreaks();
    streaks.forEach(s=>{const k=`${normalizePlayerName(s.player)}|${normalizePropMetric(s.stat)}`;streakMap.set(k,s)});
  }catch(e){reportNonFatal("Slip streak enrichment unavailable; continuing without streak context.",e)}

  const legs=[];
  for(const b of bets){
    const nl=normalizePlayerName(b.name);
    const evScore=Math.min(b.edge*40,10);
    let aiScore=0;
    const aiPick=aiMap.get(`${nl}|${normalizePropMetric(b.metric)}|${b.lean}`)||aiMap.get(nl);
    const selectionMethod=!aiPick?"MARKET_MODEL":String(rowField(aiPick,"SELECTION_METHOD")||rowField(aiPick,"CONSENSUS_TAG")).toUpperCase().includes("VALIDATED")?"VALIDATED_MODEL":"GEMINI";
    const explicitStatus=String(rowField(aiPick||{},"RECOMMENDATION_STATUS")||"").toUpperCase();
    const recommendationStatus=explicitStatus||(selectionMethod==="VALIDATED_MODEL"&&b.metric==="H"&&b.lean==="OVER"?"PLAYABLE":selectionMethod==="GEMINI"&&b.lean==="UNDER"&&["P_BB","P_ER"].includes(b.metric)?"PLAYABLE":"RESEARCH");
    let aiConflictLevel="",aiDisagreementText="";
    if(aiPick){
        const conf=normalizeConfidence(aiPick.confidence);
        const aiLean=normalizeLeanText(aiPick.lean);
        const aiMetric=normalizePropMetric(aiPick.prop_type);
        const betMetric=normalizePropMetric(b.metric);
        const aiComps=COMBO_STATS[aiMetric]||[aiMetric];
        const betComps=COMBO_STATS[betMetric]||[betMetric];
        const metricsRelated=betComps.some(c=>aiComps.includes(c))||aiComps.some(c=>betComps.includes(c));
        if(metricsRelated && aiLean && aiLean!==b.lean){
          aiConflictLevel=aiMetric===betMetric?"strong":"soft";
          aiDisagreementText=aiMetric===betMetric?`AI says ${aiLean} ${aiMetric}`:`AI leans ${aiLean} ${aiMetric}`;
          aiScore-=selectionMethod==="VALIDATED_MODEL"?2:0.75;
        }else if(aiAgreesWithBet(aiPick,b)){
          // Gemini conviction is context, not the ranking engine. The
          // deterministic validated model earns materially more weight.
          aiScore=selectionMethod==="VALIDATED_MODEL"?4:0.5;
        }
      }
    let streakScore=0;
    const logCol=propToLogCol(b.metric);
    const sk=`${nl}|${normalizePropMetric(logCol)}`;
    const streak=streakMap.get(sk);
    if(streak){
      if(streak.streak>=7)streakScore=3;
      else if(streak.streak>=5)streakScore=2;
      else if(streak.streak>=3)streakScore=1;
    }
    const reliabilityScore=Math.min(b.total/10,2);
    const hrScore=b.hitRate>=0.8?2:b.hitRate>=0.65?1:0;

    let calibrationScore=0;
    if(selectionMethod==="VALIDATED_MODEL"&&b.metric==="H"&&b.lean==="OVER")calibrationScore=4;
    else if(selectionMethod==="GEMINI"&&b.lean==="UNDER"&&b.metric==="P_BB")calibrationScore=4;
    else if(selectionMethod==="GEMINI"&&b.lean==="UNDER"&&b.metric==="P_ER")calibrationScore=2;
    else if(selectionMethod==="GEMINI"&&b.lean==="OVER"&&["H","R","P_SO"].includes(b.metric))calibrationScore=-2;

    const conviction=evScore+aiScore+calibrationScore+streakScore+reliabilityScore+hrScore;

    let signals=[];
    if(aiAgreesWithBet(aiPick,b)){const c=normalizeConfidence(aiPick.confidence);signals.push(selectionMethod==="VALIDATED_MODEL"?"VALIDATED":c==="SMASH"?"SMASH":c==="STRONG"?"STRONG":"AI")}
    if(aiConflictLevel==="strong")signals.push(`${icon('warn')}AI conflict`);
    else if(aiConflictLevel==="soft")signals.push(`${icon('warn')}AI cross-check`);
    if(streak)signals.push(`🔥 ${streak.streak}G streak`);
    if(b.edge>=0.15)signals.push("💎 Elite EV");
    else if(b.edge>=0.08)signals.push("📈 Strong EV");
    if(b.hitRate>=0.8)signals.push(`✅ ${(b.hitRate*100).toFixed(0)}% hit`);

    const scheduleRow=getScheduleRow(b.team,b.opp)||{};
    const gameTotal=toNum(scheduleRow.over_under||scheduleRow.game_total);
    const gameKey=[b.team||"",b.opp||""].sort().join("|");
    const lineupRisk=String(aiPick?.injury_context||"").toUpperCase().startsWith("LINEUP RISK");
    legs.push({...b,conviction,evScore,aiScore,calibrationScore,selectionMethod,recommendationStatus,streakScore,reliabilityScore,hrScore,signals,hasAI:aiAgreesWithBet(aiPick,b),aiConfidence:aiPick?(selectionMethod==="VALIDATED_MODEL"?"VALIDATED":normalizeConfidence(aiPick.confidence)):"",hasAIConflict:!!aiConflictLevel,aiConflictLevel,aiDisagreementText,lineupRisk,hasStreak:!!streak,streakLength:streak?.streak||0,teamSlot:b.teamSlot||`${b.team}${b.isP?":P":":B"}`,gameTotal,gameKey});
  }
  legs.sort((a,b)=>b.conviction-a.conviction);
  return legs;
}

function getShortlistMatchupEvidence(leg){
  const opponent=getTeamRanking(leg.opp);
  if(!opponent)return `${leg.opp||"Opponent"} profile available on player page`;
  if(leg.metric==="P_SO")return `${leg.opp} strikes out ${teamRankValue(opponent,"OFF_K_PCT","OFF_K_PCT_MOST_RANK",{digits:1,suffix:"%",direction:"most"})}`;
  if(leg.metric==="HR")return `${leg.opp} allows ${teamRankValue(opponent,"PIT_HR9","PIT_HR9_MOST_RANK",{digits:2,suffix:" HR/9",direction:"most"})}`;
  if(leg.isP)return `${leg.opp} OPS ${teamRankValue(opponent,"OFF_OPS","OFF_OPS_BEST_RANK",{digits:3,direction:"highest"})}`;
  return `${leg.opp} staff WHIP ${teamRankValue(opponent,"PIT_WHIP","PIT_WHIP_BEST_RANK",{digits:2,direction:"best"})}`;
}

function getShortlistOpponentEffect(leg){
  const source=(leg.isP?st.pTonight:st.tonight).find(row=>normalizePlayerName(row.player_name)===normalizePlayerName(leg.name));
  if(!source)return null;
  const raw=getPropOpponentAdjustment(source,leg.metric);
  if(raw===null)return null;
  const effect=leg.lean==="UNDER"?-raw:raw;
  const label=effect>=2?"Favorable matchup":effect<=-2?"Tough matchup":"Neutral matchup";
  return{effect,label};
}

function getTonightShortlist(){
  return getMemo("tonightShortlist",()=>{
    const qualified=getConvictionLegs().filter(leg=>
      leg.recommendationStatus==="PLAYABLE"&&
      leg.edge>=0.05&&
      leg.total>=5&&
      !!leg.team&&
      !!leg.opp&&
      !leg.returning&&
      !leg.limitedSample&&
      !leg.hasAIConflict&&
      !leg.lineupRisk&&
      !getLockInfo(leg.name,leg.isP).started
    );
    const bestByPlayer=new Map();
    for(const leg of qualified){
      const key=normalizePlayerName(leg.name);
      const current=bestByPlayer.get(key);
      if(!current||leg.conviction>current.conviction||(leg.conviction===current.conviction&&leg.edge>current.edge))bestByPlayer.set(key,leg);
    }
    return [...bestByPlayer.values()]
      .map(leg=>({...leg,opponentEffect:getShortlistOpponentEffect(leg)}))
      .sort((a,b)=>b.conviction-a.conviction||b.edge-a.edge||b.hitRate-a.hitRate)
      .slice(0,12);
  });
}

function shortlistLegKey(item){return`${normalizePlayerName(item.name)}|${normalizePropMetric(item.metric)}|${item.dkLine}|${item.lean}`}
function currentShortlistSlateKey(){return getLatestPickDate()||"current"}
function persistShortlistTray(){localStorage.setItem(SHORTLIST_TRAY_KEY,JSON.stringify(st.shortlistTray||[]))}
function getActiveShortlistTray(){
  const slateKey=currentShortlistSlateKey();
  const active=(st.shortlistTray||[]).filter(item=>item.slateKey===slateKey);
  if(active.length!==(st.shortlistTray||[]).length){st.shortlistTray=active;persistShortlistTray()}
  return active;
}
function isInShortlistTray(row){const key=shortlistLegKey(row);return getActiveShortlistTray().some(item=>shortlistLegKey(item)===key)}
function toggleShortlistTray(name,metric,line,lean){
  const row=getTonightShortlist().find(item=>normalizePlayerName(item.name)===normalizePlayerName(name)&&normalizePropMetric(item.metric)===normalizePropMetric(metric)&&String(item.dkLine)===String(line)&&item.lean===lean);
  if(!row)return;
  const items=getActiveShortlistTray();
  const key=shortlistLegKey(row);
  const existing=items.findIndex(item=>shortlistLegKey(item)===key);
  if(existing>=0){items.splice(existing,1);st.shortlistTray=items;st.shortlistTrayNotice="";persistShortlistTray();render();return}
  if(items.some(item=>normalizePlayerName(item.name)===normalizePlayerName(row.name))){st.shortlistTrayNotice=`${row.name} already has a leg in the tray.`;render();return}
  if(items.length>=8){st.shortlistTrayNotice="The tray is capped at eight legs.";render();return}
  const bestBook=getBestBookForLean(row.prop,row.lean);
  items.push({slateKey:currentShortlistSlateKey(),name:row.name,metric:row.metric,dkLine:row.dkLine,lean:row.lean,odds:Number(bestBook?.odds||row.odds),book:bestBook?formatBookName(bestBook.book):"DK",edge:row.edge,hitRate:row.hitRate,team:row.team,opp:row.opp,isP:row.isP});
  st.shortlistTray=items;st.shortlistTrayNotice="";persistShortlistTray();render();
}
function removeShortlistTrayLeg(key){st.shortlistTray=getActiveShortlistTray().filter(item=>shortlistLegKey(item)!==key);st.shortlistTrayNotice="";persistShortlistTray();render()}
function clearShortlistTray(){st.shortlistTray=[];st.shortlistTrayNotice="";persistShortlistTray();render()}
function shortlistTrayCopyText(items){
  const math=calculateParlayMath(items);
  const combined=math.american>0?`+${math.american}`:`${math.american}`;
  return`MLB Shortlist Entry — ${items.length} legs\n${items.map((item,index)=>`${index+1}. ${item.name} — ${item.metric} ${item.lean} ${item.dkLine} (${fmtOdds(item.odds)}, ${item.book})`).join("\n")}\nCombined ${combined} | $10 → $${math.return10.toFixed(2)}\nBuilt ${new Date().toLocaleString()}`;
}
function copyShortlistTray(){
  const items=getActiveShortlistTray();if(!items.length)return;
  const text=shortlistTrayCopyText(items);
  const done=()=>{window.__shortlistTrayCopied=true;render();setTimeout(()=>{window.__shortlistTrayCopied=false;render()},1200)};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(text).then(done).catch(()=>entryShowCopyFallback(text));
  else entryShowCopyFallback(text);
}
function renderShortlistTray(){
  const items=getActiveShortlistTray();
  if(!items.length)return`<aside class="shortlist-tray"><div class="shortlist-tray-head"><div><div class="shortlist-tray-title">My Shortlist Tray <span>0</span></div><div class="shortlist-tray-empty">Add qualified legs below to assemble your final entry. One leg per player.</div></div></div>${st.shortlistTrayNotice?`<div class="shortlist-tray-body"><div class="shortlist-tray-notice">${esc(st.shortlistTrayNotice)}</div></div>`:""}</aside>`;
  const math=calculateParlayMath(items);
  const combined=math.american>0?`+${math.american}`:`${math.american}`;
  const avgEdge=items.reduce((sum,item)=>sum+item.edge,0)/items.length;
  const weakest=items.reduce((min,item)=>item.edge<min.edge?item:min,items[0]);
  const books=[...new Set(items.map(item=>item.book).filter(Boolean))];
  const gameCounts=new Map();
  items.forEach(item=>{const key=[item.team,item.opp].sort().join("|");gameCounts.set(key,(gameCounts.get(key)||0)+1)});
  const correlated=[...gameCounts.values()].some(count=>count>1);
  const warnings=[];
  if(correlated)warnings.push("Same-game legs detected; the combined probability is not independent.");
  if(books.length>1)warnings.push(`Cross-book entry: best prices are split across ${books.join(", ")}.`);
  if(weakest.edge<0.08)warnings.push(`Weakest leg is ${weakest.name} at +${(weakest.edge*100).toFixed(1)}% edge.`);
  return`<aside class="shortlist-tray"><div class="shortlist-tray-head"><div class="shortlist-tray-title">My Shortlist Tray <span>${items.length}</span></div><div class="shortlist-tray-actions"><button class="shortlist-tray-btn" onclick="clearShortlistTray()">Clear</button><button class="shortlist-tray-btn primary" onclick="copyShortlistTray()">${window.__shortlistTrayCopied?"Copied":"Copy entry"}</button></div></div><div class="shortlist-tray-body"><div class="shortlist-tray-legs">${items.map(item=>`<div class="shortlist-tray-leg"><strong>${esc(item.name)}</strong><span>${esc(item.metric)} ${item.lean} ${esc(item.dkLine)} · ${fmtOdds(item.odds)}</span><button class="shortlist-tray-remove" title="Remove ${esc(item.name)}" onclick="removeShortlistTrayLeg('${esc(shortlistLegKey(item))}')">×</button></div>`).join("")}</div><div class="shortlist-tray-metrics"><div class="shortlist-tray-metric"><strong>${combined}</strong><span>Combined odds</span></div><div class="shortlist-tray-metric"><strong>$${math.return10.toFixed(2)}</strong><span>$10 return</span></div><div class="shortlist-tray-metric"><strong>+${(avgEdge*100).toFixed(1)}%</strong><span>Average edge</span></div><div class="shortlist-tray-metric"><strong>+${(weakest.edge*100).toFixed(1)}%</strong><span>Weakest leg</span></div></div>${warnings.map(warning=>`<div class="shortlist-tray-warning">${icon("warn")}${esc(warning)}</div>`).join("")}${st.shortlistTrayNotice?`<div class="shortlist-tray-notice">${esc(st.shortlistTrayNotice)}</div>`:""}</div></aside>`;
}

function renderTonightShortlist(){
  const rows=getTonightShortlist();
  if(!rows.length)return`<section class="shortlist-shell"><div class="shortlist-head"><div><div class="analysis-eyebrow">This week's decision board</div><div class="shortlist-title">This Week's Shortlist</div><div class="shortlist-sub">Only unlocked, adequately sampled props with actionable prices, +5% edge, and no active model or lineup warning qualify.</div></div><div class="shortlist-rule">Strict mode · passing allowed</div></div>${renderShortlistTray()}<div class="props-pass" style="margin:0"><div class="props-pass-title">No play clears every gate this week</div><div class="props-pass-copy">The data loaded correctly; the board is declining to promote a weak or conflicted option. Prop Explorer still contains the wider research set.</div></div></section>`;
  const avgEdge=rows.reduce((sum,row)=>sum+row.edge,0)/rows.length;
  const aiBacked=rows.filter(row=>row.hasAI).length;
  const markets=new Set(rows.map(row=>row.metric)).size;
  return`<section class="shortlist-shell"><div class="shortlist-head"><div><div class="analysis-eyebrow">This week's decision board</div><div class="shortlist-title">This Week's Shortlist</div><div class="shortlist-sub">Qualified opportunities only: +5% modeled edge, playable price, 5+ decisive games, no sample warning, no lineup risk, no model disagreement, and not locked.</div></div><div class="shortlist-rule">Ranked by conviction</div></div><div class="shortlist-kpis"><div class="shortlist-kpi"><strong>${rows.length}</strong><span>Qualified</span></div><div class="shortlist-kpi"><strong>+${(avgEdge*100).toFixed(1)}%</strong><span>Average edge</span></div><div class="shortlist-kpi"><strong>${aiBacked}</strong><span>AI backed</span></div><div class="shortlist-kpi"><strong>${markets}</strong><span>Markets</span></div></div>${renderShortlistTray()}<div class="shortlist-grid">${rows.map((row,index)=>{
    const edgePct=(row.edge*100).toFixed(1);
    const hitPct=(row.hitRate*100).toFixed(0);
    const impliedPct=(row.impliedProb*100).toFixed(0);
    const callClass=row.lean==="OVER"?"prop-over":"prop-under";
    const matchup=getShortlistMatchupEvidence(row);
    const opponentEffect=row.opponentEffect;
    const tags=[row.hasAI?`${row.aiConfidence||"AI"} backed`:"Market model",row.hasStreak?`${row.streakLength}G streak`:"Stable sample",row.edge>=0.15?"Elite edge":row.edge>=0.08?"Strong edge":"Qualified edge"];
    if(opponentEffect)tags.push(opponentEffect.label);
    const inTray=isInShortlistTray(row);
    const gameTime=gameStartTimeForTeams(row.team,row.opp);
    const opponentEffectText=opponentEffect?`<span><strong>Opponent effect:</strong> ${opponentEffect.effect>=0?"+":""}${opponentEffect.effect.toFixed(1)} model points for this ${row.lean.toLowerCase()}</span>`:"";
    return`<article class="shortlist-card${index===0?" top":""}" onclick="streakToDash('${esc(row.name)}','${propToLogCol(row.metric)}','${row.dkLine}')"><div><div class="shortlist-rank">${index===0?"Top play":`#${String(index+1).padStart(2,"0")}`}</div><div class="shortlist-name">${playerLink(row.name,row.metric,row.dkLine)}</div><div class="shortlist-meta">${esc(row.team)} vs ${esc(row.opp||"TBD")}${gameTime?` · ${esc(gameTime)}`:""} · ${esc(propTypeLabel(row.metric))} · ${row.hits}/${row.total} decisive games</div></div><div class="shortlist-call"><span class="shortlist-market">${esc(propTypeLabel(row.metric))}</span><strong class="${callClass}">${row.lean} ${esc(row.dkLine)}</strong><span>${fmtOdds(row.odds)} · +${edgePct}% edge</span></div><div class="shortlist-evidence"><span><strong>${hitPct}% historical hit rate</strong> across the available sample</span><span><strong>${edgePct} points above market</strong> (${hitPct}% model vs ${impliedPct}% implied)</span><span><strong>Opponent profile:</strong> ${esc(matchup)}</span>${opponentEffectText}<span><strong>Playable price:</strong> ${fmtOdds(row.odds)}${row.hasAI?` · ${esc(row.aiConfidence||"AI")} agrees`:" · no AI conflict"}</span></div><div class="shortlist-tags">${tags.map(tag=>`<span class="shortlist-tag">${esc(tag)}</span>`).join("")}<button class="shortlist-action${inTray?" added":""}" onclick="event.stopPropagation();toggleShortlistTray('${esc(row.name)}','${esc(row.metric)}','${esc(row.dkLine)}','${row.lean}')">${inTray?"Remove":"Add to tray"}</button></div></article>`;
  }).join("")}</div></section>`;
}

function generateSlips(legs,legCount){
  if(legs.length<legCount)return[];
  const slips=[];
  const maxIter=legCount<=3?500:300;

  function gen(start,current,usedPlayers,teamCounts){
    if(current.length===legCount){
      let score=current.reduce((s,l)=>s+l.conviction,0);
      const avgEdge=current.reduce((s,l)=>s+l.edge,0)/legCount;
      const avgHitRate=current.reduce((s,l)=>s+l.hitRate,0)/legCount;
      const teams=[...new Set(current.map(l=>l.teamSlot||l.team))];
      const signals=current.reduce((s,l)=>s+l.signals.length,0);
      const slipTags=[];
      for(let i=0;i<current.length;i++){for(let j=i+1;j<current.length;j++){const a=current[i],b=current[j];if(a.gameKey&&a.gameKey===b.gameKey&&a.team!==b.team&&Math.max(toNum(a.gameTotal),toNum(b.gameTotal))>9.5){score*=1.10;slipTags.push("⚡ GAME STACK")}}}
      slips.push({legs:current.slice(),score,avgEdge,avgHitRate,teams,signalCount:signals,legCount,slipTags:[...new Set(slipTags)]});
      return;
    }
    for(let i=start;i<pool.length&&slips.length<maxIter;i++){
      const leg=pool[i];
      if(usedPlayers.has(leg.name.toLowerCase()))continue;
      const slot=leg.teamSlot||leg.team;
      const tc=teamCounts.get(slot)||0;
      if(tc>=2)continue;

      usedPlayers.add(leg.name.toLowerCase());
      teamCounts.set(slot,(tc||0)+1);
      current.push(leg);
      gen(i+1,current,usedPlayers,teamCounts);
      current.pop();
      usedPlayers.delete(leg.name.toLowerCase());
      teamCounts.set(slot,tc);
    }
  }
  const pool=legs.slice(0,legCount<=3?15:legCount<=4?18:20);
  gen(0,[],new Set(),new Map());
  slips.sort((a,b)=>b.score-a.score);

  // Player diversity: try strictest cap first, relax only as needed to hit 8 slips.
  const MAX_SLIPS=8;
  let selected=[];
  for(let cap=2;cap<=MAX_SLIPS;cap++){
    selected=[];
    const playerUsageCount=new Map();
    for(const slip of slips){
      if(selected.length>=MAX_SLIPS)break;
      const overUsed=slip.legs.some(l=>(playerUsageCount.get(l.name.toLowerCase())||0)>=cap);
      if(overUsed)continue;
      selected.push(slip);
      slip.legs.forEach(l=>{
        const n=l.name.toLowerCase();
        playerUsageCount.set(n,(playerUsageCount.get(n)||0)+1);
      });
    }
    if(selected.length>=MAX_SLIPS)break;
  }
  return selected.slice(0,MAX_SLIPS);
}

function getSmartSlips(){
  return getMemo("smartSlips",()=>{
  const legs=getConvictionLegs();
  if(!legs.length)return{legs:[],slips3:[],slips4:[],slips5:[]};
  return{
    legs,
    slips3:generateSlips(legs,3),
    slips4:generateSlips(legs,4),
    slips5:generateSlips(legs,5)
  };
  });
}

function pickDashPlayer(name){
  st.player=name;st.oppFilter="";st.showFullLog=false;
  console.log("Selected:",name);
  render();
}

function toggleFullLog(){st.showFullLog=!st.showFullLog;render()}
function setStreakFilter(f){st.streakFilter=f;render()}
function setSlipLegs(n){st.slipLegs=n;render()}
function toggleDrafted(name){if(st.drafted.has(name))st.drafted.delete(name);else st.drafted.add(name);render()}
function resetDrafted(){st.drafted.clear();render()}
function streakToDash(name,metric,line){
  const metricKey=String(metric||"").toUpperCase();
  const pitcherMetric=metricKey.startsWith("P_")||["SO","ER","IP","IP_OUTS"].includes(metricKey);
  const b=st.tonight.find(t=>normalizePlayerName(t.player_name)===normalizePlayerName(name));
  const p=st.pTonight.find(t=>normalizePlayerName(t.player_name)===normalizePlayerName(name));
  if(pitcherMetric){
    st.mode="qb";
    st.metric=metricKey==="P_SO"?"SO":metricKey.replace(/^P_/,"")||"SO";
    st.player=p?.player_name||name;
  }else if(b){
    st.mode="skill";st.metric=metric||"REC";st.player=b.player_name;
  }else if(p){
    st.mode="qb";st.metric=metric||"PASS_YDS";st.player=p.player_name;
  }
  if(line!==undefined&&line!=="")st.line=String(line);
  else st.line="";
  st.activeTab="dashboard";render();
}
function playerLink(name,metric="",line="",label=""){const n=cleanName(label||name||"");return `<span class="player-link" onclick="event.stopPropagation();streakToDash('${esc(name)}','${esc(metric)}','${esc(line)}')">${esc(n)}</span>`}

// ═══ STREAKS ═══
function getStreakHeat(s){if(s>=10)return{l:"INFERNO",c:"var(--under)",cls:"inferno"};if(s>=5)return{l:"ON FIRE",c:"#ff6b35",cls:"fire"};if(s>=3)return{l:"HOT",c:"#ffaa00",cls:"hot"};return{l:"WARM",c:"#ffd966",cls:"warm"}}
function miniChart(vals,thr){const mx=Math.max(...vals,thr+1);return vals.slice().reverse().map(v=>{const h=Math.max(3,(v/mx)*26);return`<div class="streak-chart-bar" style="height:${h}px;background:${v>=thr?'var(--over)':'var(--under)'};opacity:.85"></div>`}).join("")}

function getStreaks(){
  return getMemo("streaks",()=>{
  const streaks=[];
  const BAT=[{key:"H",threshold:1,label:"Hit Streak",emoji:"🔥",desc:"games w/ a hit"},{key:"HR",threshold:1,label:"HR Streak",emoji:"💣",desc:"games w/ a HR"},{key:"H",threshold:2,label:"Multi-Hit",emoji:"🔥🔥",desc:"games w/ 2+ hits"},{key:"RBI",threshold:1,label:"RBI Streak",emoji:"💰",desc:"games w/ an RBI"},{key:"TB",threshold:3,label:"Power Surge",emoji:"⚡",desc:"games w/ 3+ TB"},{key:"R",threshold:1,label:"Runs Streak",emoji:"🏃",desc:"games scoring a run"},{key:"SB",threshold:1,label:"SB Streak",emoji:"💨",desc:"games w/ a steal"}];
  const tonightNames=new Set(st.tonight.map(p=>p.player_name).filter(Boolean));
  for(const sType of BAT){for(const name of tonightNames){
    const logs=getPlayerLogs(name,false);
    if(logs.length<3)continue;let streak=0;
    for(const g of logs){if(toNum(g[sType.key])>=sType.threshold)streak++;else break}
    if(streak<3)continue;
    const pT=getTonightPlayerRow(name,false)||{};
    const recentVals=logs.slice(0,7).map(g=>toNum(g[sType.key]));
    const avgDuring=(logs.slice(0,streak).reduce((s,g)=>s+toNum(g[sType.key]),0)/streak)||0;
    const seasAvg=toNum(logs[0][`Seas_${sType.key}`]);
    const prop=st.props.find(pr=>normalizePlayerName(pr.PLAYER_NAME)===normalizePlayerName(name)&&normalizePropMetric(pr.METRIC)===normalizePropMetric(sType.key));
    streaks.push({player:name,team:pT.team_abbr||"",opp:pT.opp_abbr_tonight||"",pitcher:pT.opp_pitcher_name||"TBD",hand:pT.opp_pitcher_hand||"?",venue:pT.venue_tonight||"",stat:sType.key,threshold:sType.threshold,streak,label:sType.label,emoji:sType.emoji,propType:"bat",desc:sType.desc,avgDuring:avgDuring.toFixed(2),seasAvg:seasAvg.toFixed(2),recentVals,dkLine:prop?prop.DK_LINE:null,overOdds:prop?parseInt(prop.OVER_ODDS)||null:null});
  }}
  const PITCH=[{key:"SO",threshold:6,label:"K Streak",emoji:"🔥",desc:"starts w/ 6+ K"},{key:"SO",threshold:8,label:"Elite K",emoji:"⚡",desc:"starts w/ 8+ K"},{key:"ER",threshold:2,label:"Lockdown",emoji:"🔒",compare:"lte",desc:"starts w/ ≤2 ER"},{key:"W",threshold:1,label:"Win Streak",emoji:"👑",desc:"consecutive wins"}];
  const pNames=new Set(st.pTonight.map(p=>p.player_name).filter(Boolean));
  for(const sType of PITCH){for(const name of pNames){
    const logs=getPlayerLogs(name,true);
    if(logs.length<2)continue;let streak=0;const isLte=sType.compare==="lte";
    for(const g of logs){const v=toNum(g[sType.key]);if(isLte?v<=sType.threshold:v>=sType.threshold)streak++;else break}
    if(streak<2)continue;
    const pT=getTonightPlayerRow(name,true)||{};
    const recentVals=logs.slice(0,7).map(g=>toNum(g[sType.key]));
    const avgDuring=(logs.slice(0,streak).reduce((s,g)=>s+toNum(g[sType.key]),0)/streak)||0;
    const seasAvg=toNum(logs[0][`Seas_${sType.key}`])||toNum(logs[0][`L7_${sType.key}`]);
    const prop=st.props.find(pr=>normalizePlayerName(pr.PLAYER_NAME)===normalizePlayerName(name)&&normalizePropMetric(pr.METRIC)===normalizePropMetric(sType.key));
    streaks.push({player:name,team:pT.team_abbr||"",opp:pT.opp_abbr_tonight||"",pitcher:"",hand:"",venue:pT.venue_tonight||"",stat:sType.key,threshold:sType.threshold,streak,label:sType.label,emoji:sType.emoji,propType:"pitch",desc:sType.desc,isLte,avgDuring:avgDuring.toFixed(2),seasAvg:seasAvg.toFixed(2),recentVals,dkLine:prop?prop.DK_LINE:null,overOdds:prop?parseInt(prop.OVER_ODDS)||null:null});
  }}
  const best={};for(const s of streaks){const k=`${s.player}|${s.stat}`;if(!best[k]||s.streak>best[k].streak||(s.streak===best[k].streak&&s.threshold>best[k].threshold))best[k]=s}
  const result=Object.values(best);result.sort((a,b)=>b.streak-a.streak);
  return result;
  });
}

function getConvergenceBoard(){
  return getMemo("convergenceBoard",()=>{
  const board=new Map();
  const latestDate=getLatestPickDate();
  const latestRun=getLatestPickRun();
  const allowed=new Set(st.picks.filter(p=>normalizeDate(rowField(p,"DATE"))===latestDate&&toNum(rowField(p,"RUN_NUMBER"))===latestRun).map(p=>normalizePlayerName(p.player)).filter(Boolean));
  const add=(name,source,boost=0,meta={})=>{
    if(!name)return;
    const key=normalizePlayerName(name);
    if(allowed.size && !allowed.has(key))return;
    if(!board.has(key))board.set(key,{name,sources:new Set(),score:0,team:meta.team||"",opp:meta.opp||"",detail:""});
    const row=board.get(key);
    row.sources.add(source);
    row.score+=boost;
    if(!row.team&&meta.team)row.team=meta.team;
    if(!row.opp&&meta.opp)row.opp=meta.opp;
    if(!row.detail&&meta.detail)row.detail=meta.detail;
  };
  const marketEdgeMap=new Map();
  getMarketEdges().filter(b=>b.edge>=0.05).slice(0,20).forEach(b=>{
    marketEdgeMap.set(normalizePlayerName(b.name),b);
    add(b.name,"Market Edge",2+Math.min(b.edge*20,3),{team:b.team,opp:b.opp,detail:`${b.lean} ${b.metric} ${b.dkLine}`});
  });
  st.picks.filter(p=>normalizeDate(rowField(p,"DATE"))===latestDate&&toNum(rowField(p,"RUN_NUMBER"))===latestRun).forEach(pk=>{
    const marketEdge=marketEdgeMap.get(normalizePlayerName(pk.player));
    if(!aiAgreesWithBet(pk,marketEdge))return;
    const conf=normalizeConfidence(pk.confidence);
    add(pk.player,"AI",conf==="SMASH"?4:conf==="STRONG"?3:2,{detail:`${pk.lean||""} ${pk.prop_type||""} ${pk.line||""}`.trim()});
  });
  getStreaks().slice(0,20).forEach(s=>add(s.player,"Streaks",s.streak>=7?3:s.streak>=5?2.5:2,{team:s.team,opp:s.opp,detail:`${s.streak}G ${s.stat}`}));
  getDingerBoard().slice(0,15).forEach(d=>add(d.name,"Dingers",1.5+(d.hrRate||0)*3,{team:d.team,opp:d.opp,detail:`${(d.hrRate*100).toFixed(1)}% HR rate`}));
  return [...board.values()].map(r=>({...r,sourceCount:r.sources.size,sourceList:[...r.sources]})).filter(r=>r.sourceCount>=2).sort((a,b)=>b.sourceCount-a.sourceCount||b.score-a.score).slice(0,5);
  });
}

function renderConvergenceHTML(){
  const board=getConvergenceBoard();
  if(!board.length)return"";
  const top=board[0];
  return `<div class="convergence-shell"><details class="convergence-details"><summary class="convergence-toggle"><div class="convergence-title"><div style="color:var(--accent);font-size:var(--t-sm);font-weight:700">${icon("picks")}Players of the Day</div><div style="color:var(--ink-muted);font-size:var(--t-xs)">Cross-tab convergence from market edge, model picks, Streaks, and TDs.</div></div><div class="convergence-kpis"><span class="convergence-chip"><strong style="color:var(--accent)">${top.sourceCount}</strong> top</span><span class="convergence-chip"><strong>${board.length}</strong> 2+</span><span class="convergence-chip"><strong style="color:var(--over)">${board.filter(p=>p.sourceCount>=3).length}</strong> 3+</span></div></summary><div class="convergence-body"><div class="bet-summary">
    <div class="bs-card"><div class="bs-val" style="color:var(--accent)">${top.sourceCount}</div><div class="bs-lbl">TOP SIGNALS</div></div>
    <div class="bs-card"><div class="bs-val">${board.length}</div><div class="bs-lbl">2+ SURFACES</div></div>
    <div class="bs-card"><div class="bs-val" style="color:var(--over)">${board.filter(p=>p.sourceCount>=3).length}</div><div class="bs-lbl">3+ MATCHES</div></div>
  </div>
  <div class="cards-grid">
    ${board.map((p,i)=>`<div class="bet-card ${i===0?"elite":"mid"}" style="cursor:pointer;border-color:${i===0?"var(--accent)":"var(--border-1)"}" onclick="streakToDash('${esc(p.name)}')"><div class="bet-left"><div class="bet-name">${playerLink(p.name)}</div><div class="bet-meta">${esc(p.team||"")} ${p.opp?`vs ${esc(p.opp)}`:""}</div>${p.detail?`<div class="bet-prop"><span class="prop-metric" style="font-size:var(--t-xs)">Lead</span><span style="color:var(--ink-1);font-size:var(--t-xs)">${esc(p.detail)}</span></div>`:""}<div class="draft-tags" style="margin-top:6px">${p.sourceList.map(s=>`<span class="draft-tag" style="background:var(--surface-2);color:${s==="AI"?"var(--accent)":s==="Market Edge"?"var(--accent-soft)":s==="Streaks"?"#ffaa00":"var(--under)"}">${esc(s==="AI"?"Model":s)}</span>`).join("")}</div></div><div class="bet-right"><div class="bet-edge pos">${p.sourceCount}x</div><div class="bet-sub">signals</div></div></div>`).join("")}
  </div></div></details></div>`;
}

// ═══ DRAFT CHEAT SHEET ═══
// ═══ VS STARTING PITCHER (career) ═══
function getVsSP(playerName){
  if(!playerName||!st.vsSP.length)return null;
  const n=normalizePlayerName(playerName);
  return st.vsSP.find(v=>normalizePlayerName(v.player_name)===n)||null;
}

// ═══ STAT PARLAY ENGINE ═══
function getPropOpponentAdjustment(player,metric){
  const normalized=normalizePropMetric(metric);
  const field=normalized==="H"
    ?"H_OPP_ADJ"
    :["HR","TB"].includes(normalized)
      ?"POWER_OPP_ADJ"
      :normalized==="P_SO"
        ?"P_SO_OPP_ADJ"
        :normalized==="P_ER"
          ?"P_ER_OPP_ADJ"
          :null;
  return field?optionalRowNumber(player,field):null;
}
function getStatParlayBoard(stat){
  return getMemo(`statParlay:${stat}`,()=>{
  const rows=[];
  const isPS=stat.startsWith("P_");
  const logCol=propToLogCol(stat);
  const src=isPS?st.pTonight:st.tonight;

  for(const p of src){
    const name=p.player_name;if(!name)continue;
    const logs=getPlayerLogs(name,isPS);
    if(logs.length<3)continue;
    const most=logs[0]||{};

    // Find DK prop for this stat
    const prop=st.props.find(pr=>normalizePlayerName(pr.PLAYER_NAME)===normalizePlayerName(name)&&normalizePropMetric(pr.METRIC)===normalizePropMetric(stat));
    if(!prop)continue; // need a prop line to parlay

    const dkLine=parseFloat(prop.DK_LINE);if(isNaN(dkLine))continue;
    const overOdds=parseInt(prop.OVER_ODDS);
    const underOdds=parseInt(prop.UNDER_ODDS);

    // Hit rate over the line
    const combo=COMBO_STATS[logCol];
    const hitsOver=combo
      ?logs.filter(g=>combo.reduce((s,k)=>s+toNum(g[k]),0)>dkLine).length
      :logs.filter(g=>toNum(g[logCol])>dkLine).length;
    const hitRate=hitsOver/logs.length;

    // EV edge
    const overIP=impliedProb(overOdds);
    const edge=overIP!==null?hitRate-overIP:0;

    // Season and recent averages
    const seasAvg=getRollingVal(most,"Seas_",logCol);
    const l7Avg=isPS?getRollingVal(most,"L3_",logCol):getRollingVal(most,"L7_",logCol);

    // Matchup score
    let matchupScore=0;
    if(!isPS){
      const vsAvg=toNum(p.vs_OPP_AVG);
      if(vsAvg>=0.280)matchupScore+=2;
      else if(vsAvg>=0.250)matchupScore+=1;
      // Career vs SP
      const vsp=getVsSP(name);
      if(vsp){
        const cAB=toNum(vsp.AB);const cAVG=toNum(vsp.AVG);
        if(cAB>=5&&cAVG>=0.300)matchupScore+=2;
        else if(cAB>=5&&cAVG>=0.250)matchupScore+=1;
      }
    }
    const opponentAdjustment=getPropOpponentAdjustment(p,stat);

    // Composite score: hit rate is king, edge matters, matchup bonus
    const matchupComponent=opponentAdjustment!==null?opponentAdjustment:matchupScore*3;
    const score=hitRate*40+Math.max(edge,0)*30+matchupComponent+(l7Avg>seasAvg?5:0);

    rows.push({
      name,team:p.team_abbr||"",opp:p.opp_abbr_tonight||"",
      pitcher:p.opp_pitcher_name||p.opp_starter||"TBD",
      hand:p.opp_pitcher_hand||"?",
      venue:p.venue_tonight||"",
      stat,dkLine,overOdds,underOdds,
      hitRate,hitsOver,total:logs.length,
      edge,seasAvg,l7Avg,matchupScore,opponentAdjustment,matchupComponent,score
    });
  }
  rows.sort((a,b)=>b.score-a.score);
  return rows;
  });
}

function getRankedPropsBoard(){
  return getMemo("rankedPropsBoard",()=>{
    const metricBoards=new Map();
    [...new Set(st.props.map(p=>p.METRIC).filter(Boolean))].forEach(metric=>{
      const byPlayer=new Map();
      getStatParlayBoard(metric).forEach(row=>byPlayer.set(`${normalizePlayerName(row.name)}|${row.dkLine}`,row));
      metricBoards.set(metric,byPlayer);
    });
    return st.props.map((prop,index)=>{
      const isP=isPitcherProp(prop.METRIC);
      const source=isP?st.pTonight:st.tonight;
      const playerKey=normalizePlayerName(prop.PLAYER_NAME);
      const player=source.find(row=>normalizePlayerName(row.player_name)===playerKey)||{};
      const ranked=metricBoards.get(prop.METRIC)?.get(`${playerKey}|${parseFloat(prop.DK_LINE)}`)||null;
      const logCol=propToLogCol(prop.METRIC);
      const hitRateData=getHitRate(prop.PLAYER_NAME,logCol,parseFloat(prop.DK_LINE),isP);
      const overIP=impliedProb(parseInt(prop.OVER_ODDS));
      const underIP=impliedProb(parseInt(prop.UNDER_ODDS));
      const overEdge=hitRateData&&overIP!==null?hitRateData.overRate-overIP:null;
      const underEdge=hitRateData&&underIP!==null?hitRateData.underRate-underIP:null;
      let side=null,hitRate=null,edge=null,odds=null;
      const sideCandidates=[];
      if(overEdge!==null)sideCandidates.push({side:"OVER",hitRate:hitRateData.overRate,edge:overEdge,odds:parseInt(prop.OVER_ODDS)});
      if(underEdge!==null&&prop.METRIC!=="HR")sideCandidates.push({side:"UNDER",hitRate:hitRateData.underRate,edge:underEdge,odds:parseInt(prop.UNDER_ODDS)});
      sideCandidates.sort((a,b)=>b.edge-a.edge||b.hitRate-a.hitRate);
      if(sideCandidates.length)({side,hitRate,edge,odds}=sideCandidates[0]);
      const hitComponent=hitRate!==null?hitRate*20:0;
      const edgeComponent=edge!==null?Math.max(edge,0)*60:0;
      const formComponent=ranked&&side?(side==="OVER"?ranked.l7Avg>ranked.seasAvg:ranked.l7Avg<ranked.seasAvg)?5:0:0;
      const matchupComponent=ranked&&side
        ?ranked.opponentAdjustment!==null
          ?(side==="OVER"?ranked.opponentAdjustment:-ranked.opponentAdjustment)
          :side==="OVER"
            ?(ranked.matchupScore||0)*3
            :0
        :0;
      const score=hitComponent+edgeComponent+formComponent+matchupComponent;
      const team=String(player.team_abbr||"").toUpperCase();
      return {prop,index,isP,player,team,teamName:teamDisplayName(team),opp:String(player.opp_abbr_tonight||"").toUpperCase(),side,odds,hitRate,edge,score,components:{hit:hitComponent,edge:edgeComponent,form:formComponent,matchup:matchupComponent}};
    });
  });
}

function renderPropsTeamBoard(team,rows){
  if(!team||team==="ALL")return"";
  const teamRows=rows.filter(row=>row.team===team&&row.side);
  const context=teamRows[0]?.player||st.tonight.find(row=>String(row.team_abbr||"").toUpperCase()===team)||{};
  const opp=String(context.opp_abbr_tonight||teamRows[0]?.opp||"").toUpperCase();
  const opponent=getTeamRanking(opp);
  const pitcher=context.opp_pitcher_name||context.opp_starter||"TBD";
  const markets=[{key:"H",label:"Hits"},{key:"HR",label:"Home Runs"},{key:"SB",label:"Stolen Bases"},{key:"TB",label:"Total Bases"},{key:"BB",label:"Walks"}];
  const cards=markets.map(market=>{
    const picks=teamRows.filter(row=>row.prop.METRIC===market.key).sort((a,b)=>b.score-a.score).slice(0,3);
    return `<div class="team-market-card"><div class="team-market-title"><span>${market.label}</span><span>${picks.length}</span></div>${picks.length?picks.map(row=>`<div class="team-market-row" onclick="streakToDash('${esc(row.prop.PLAYER_NAME)}','${propToLogCol(row.prop.METRIC)}','${row.prop.DK_LINE}')"><div class="team-market-player">${esc(row.prop.PLAYER_NAME)}</div><div class="team-market-call"><span class="props-side ${row.side.toLowerCase()}">${row.side} ${esc(row.prop.DK_LINE)}</span><span>${(row.hitRate*100).toFixed(0)}% · ${row.score.toFixed(1)}</span></div></div>`).join(""):`<div style="padding-top:8px;color:var(--ink-muted);font-size:var(--t-xs)">No market</div>`}</div>`;
  }).join("");
  return `<section class="team-props-board"><div class="team-props-head"><div><div class="analysis-eyebrow">Team matchup board</div><div class="team-props-name">${esc(teamDisplayName(team))}</div><div class="team-props-context">${esc(team)} vs ${esc(opp||"TBD")} · opposing starter ${esc(pitcher)}</div></div>${opponent?`<div class="team-props-staff"><span>${teamRankValue(opponent,"PIT_ERA","PIT_ERA_BEST_RANK",{digits:2,direction:"best"})} ERA</span><span>${teamRankValue(opponent,"PIT_WHIP","PIT_WHIP_BEST_RANK",{digits:2,direction:"best"})} WHIP</span><span>${teamRankValue(opponent,"PIT_HR9","PIT_HR9_MOST_RANK",{digits:2,suffix:" HR/9",direction:"most"})}</span></div>`:""}</div><div class="team-market-grid">${cards}</div></section>`;
}

function getStatParlayCombos(board,legs){
  if(board.length<legs)return[];
  const combos=[];
  const pool=board.slice(0,legs<=2?12:15);
  function gen(start,current){
    if(current.length===legs){
      const teams=current.map(d=>d.team);
      const uniqueTeams=new Set(teams);
      // Max 2 from same team
      const teamCounts={};
      for(const t of teams){teamCounts[t]=(teamCounts[t]||0)+1;if(teamCounts[t]>2)return}
      const score=current.reduce((s,d)=>s+d.score,0);
      const avgHitRate=current.reduce((s,d)=>s+d.hitRate,0)/legs;
      const avgEdge=current.reduce((s,d)=>s+d.edge,0)/legs;
      combos.push({players:current.slice(),score,avgHitRate,avgEdge,teams:[...uniqueTeams]});
      return;
    }
    for(let i=start;i<pool.length&&combos.length<300;i++){
      // Unique players
      if(current.some(c=>c.name===pool[i].name))continue;
      current.push(pool[i]);
      gen(i+1,current);
      current.pop();
    }
  }
  gen(0,[]);
  combos.sort((a,b)=>b.score-a.score);
  return combos.slice(0,8);
}

function renderMarketParlays(stat,label){
  const rawBoard=getStatParlayBoard(stat);
  const board=rawBoard.filter(player=>player.edge>=0.05);
  const combos2=getStatParlayCombos(board,2);
  const combos3=getStatParlayCombos(board,3);
  let html=`<section class="combo-section" style="margin-top:12px;border-top:1px solid var(--border-1);padding-top:16px"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px"><div class="combo-title">${label} Parlays</div><div style="color:var(--ink-muted);font-size:var(--t-xs)">${board.length} positive-edge candidates</div></div><div style="color:var(--ink-muted);font-size:var(--t-xs);margin:-2px 0 10px">Combination recommendations from this board. Every leg must clear the +5% edge floor.</div>`;
  if(board.length<2){
    const reason=rawBoard.length?`${rawBoard.length} OVER candidate${rawBoard.length===1?" is":"s are"} available, but fewer than two clear +5% edge. Pass this market.`:"No eligible player props with 3+ games of data.";
    return html+`<div class="empty" style="padding:22px 8px">No positive-edge ${label.toLowerCase()} parlay is available. ${reason}</div></section>`;
  }
  const renderCombos=(combos,legs)=>combos.length?`<div style="margin-top:12px"><div class="combo-title">Best ${legs}-Leg Combinations</div><div class="combo-grid">${combos.map((combo,i)=>`<div class="combo-card ${i===0?"best":""}"><span class="combo-rank">#${i+1}</span><span class="combo-players">${combo.players.map(player=>playerLink(player.name,stat,player.dkLine||"")).join(" + ")}</span><span class="combo-score">${(combo.avgHitRate*100).toFixed(0)}% avg</span><div class="combo-teams">${combo.teams.join(" · ")} · Avg edge: +${(combo.avgEdge*100).toFixed(0)}%</div></div>`).join("")}</div></div>`:"";
  return html+renderCombos(combos2,2)+renderCombos(combos3,3)+`</section>`;
}

function draftGameId(row){
  const gamePk=String(rowField(row,"game_pk","GAME_PK","game_id","GAME_ID")||"").trim();
  if(gamePk)return`pk:${gamePk}`;
  const home=String(rowField(row,"home_abbr","HOME_ABBR")||"").trim().toUpperCase();
  const away=String(rowField(row,"away_abbr","AWAY_ABBR")||"").trim().toUpperCase();
  const pair=entryPairId(home,away);
  return pair?`pair:${pair}`:"";
}

function getDraftSlateGames(){
  return getMemo("draftSlateGames",()=>{
    const games=[];const seen=new Set();
    for(const row of st.schedule||[]){
      const id=draftGameId(row);
      if(!id||seen.has(id))continue;
      seen.add(id);
      const home=String(rowField(row,"home_abbr","HOME_ABBR")||"").trim().toUpperCase();
      const away=String(rowField(row,"away_abbr","AWAY_ABBR")||"").trim().toUpperCase();
      const startMs=parseStartMs(rowField(row,"game_time","commence_time","start_time"));
      games.push({id,home,away,label:`${away} @ ${home}`,startMs,started:!!(startMs&&Date.now()>=startMs)});
    }
    if(!games.length){
      for(const row of [...(st.tonight||[]),...(st.pTonight||[])]){
        const team=String(rowField(row,"team_abbr")||"").trim().toUpperCase();
        const opp=String(rowField(row,"opp_abbr_tonight","tonight_opp","opp_abbr")||"").trim().toUpperCase();
        const pair=entryPairId(team,opp);
        const id=pair?`pair:${pair}`:"";
        if(!id||seen.has(id))continue;
        seen.add(id);
        const startMs=getScheduleStartMs(team,opp);
        games.push({id,home:"",away:"",label:`${team} vs ${opp}`,startMs,started:!!(startMs&&Date.now()>=startMs)});
      }
    }
    return games.sort((a,b)=>(a.startMs||Number.MAX_SAFE_INTEGER)-(b.startMs||Number.MAX_SAFE_INTEGER)||a.label.localeCompare(b.label));
  });
}

function draftSlateSignature(games=getDraftSlateGames()){return games.map(game=>game.id).sort().join("|")}
function persistDraftSlate(){
  localStorage.setItem(DRAFT_SLATE_KEY,JSON.stringify({
    signature:st.draftSlate.signature,
    selectedIds:[...st.draftSlate.selectedIds]
  }));
}
function syncDraftSlateSelection(){
  const games=getDraftSlateGames();
  const signature=draftSlateSignature(games);
  const valid=new Set(games.map(game=>game.id));
  if(st.draftSlate.signature!==signature){
    st.draftSlate.signature=signature;
    st.draftSlate.selectedIds=new Set(valid);
    st.drafted.clear();
  }else{
    st.draftSlate.selectedIds=new Set([...st.draftSlate.selectedIds].filter(id=>valid.has(id)));
  }
  persistDraftSlate();
}
function draftSlateSelection(){
  const games=getDraftSlateGames();
  if(!st.draftSlate.signature)return new Set(games.map(game=>game.id));
  return st.draftSlate.selectedIds;
}
function draftRowGameId(row){
  const direct=draftGameId(row);
  if(direct)return direct;
  const team=String(rowField(row,"team_abbr")||"").trim().toUpperCase();
  const opp=String(rowField(row,"opp_abbr_tonight","tonight_opp","opp_abbr")||"").trim().toUpperCase();
  const pair=entryPairId(team,opp);
  const matches=getDraftSlateGames().filter(game=>entryPairId(game.home,game.away)===pair);
  return matches[0]?.id||(pair?`pair:${pair}`:"");
}
function draftRowInSlate(row){return draftSlateSelection().has(draftRowGameId(row))}
function draftSlateMemoKey(){return [...draftSlateSelection()].sort().join(",")||"none"}
function applyDraftSlateSelection(ids){
  st.draftSlate.signature=draftSlateSignature();
  st.draftSlate.selectedIds=new Set(ids);
  st.drafted.clear();
  persistDraftSlate();
  render();
}
function toggleDraftSlatePanel(){st.draftSlate.panelOpen=!st.draftSlate.panelOpen;render()}
function toggleDraftSlateGame(id){
  const selected=new Set(draftSlateSelection());
  if(selected.has(id))selected.delete(id);else selected.add(id);
  applyDraftSlateSelection(selected);
}
function draftEasternHour(startMs){
  if(!startMs)return null;
  const hour=Number(new Intl.DateTimeFormat("en-US",{timeZone:"America/New_York",hour:"numeric",hour12:false}).format(new Date(startMs)));
  return Number.isFinite(hour)?hour:null;
}
function setDraftSlatePreset(preset){
  const games=getDraftSlateGames();
  let selected=[];
  if(preset==="all")selected=games.map(game=>game.id);
  else if(preset==="open")selected=games.filter(game=>!game.started).map(game=>game.id);
  else if(preset==="after7")selected=games.filter(game=>(draftEasternHour(game.startMs)??-1)>=19).map(game=>game.id);
  else if(preset==="after9")selected=games.filter(game=>(draftEasternHour(game.startMs)??-1)>=21).map(game=>game.id);
  applyDraftSlateSelection(selected);
}
function draftSlatePreset(){
  const games=getDraftSlateGames();
  const selected=draftSlateSelection();
  const same=ids=>ids.length===selected.size&&ids.every(id=>selected.has(id));
  if(same(games.map(game=>game.id)))return"all";
  if(same(games.filter(game=>!game.started).map(game=>game.id)))return"open";
  if(same(games.filter(game=>(draftEasternHour(game.startMs)??-1)>=19).map(game=>game.id)))return"after7";
  if(same(games.filter(game=>(draftEasternHour(game.startMs)??-1)>=21).map(game=>game.id)))return"after9";
  if(!selected.size)return"clear";
  return"custom";
}
function draftDisplayTime(startMs){
  if(!Number.isFinite(startMs))return"";
  return new Date(startMs).toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",timeZone:"America/New_York",timeZoneName:"short"});
}
function renderDraftSlateSelector(){
  const games=getDraftSlateGames();
  const selected=draftSlateSelection();
  const selectedGames=games.filter(game=>selected.has(game.id));
  const starts=selectedGames.map(game=>game.startMs).filter(Boolean).sort((a,b)=>a-b);
  const range=starts.length?starts.length===1?draftDisplayTime(starts[0]):`${draftDisplayTime(starts[0])}–${draftDisplayTime(starts[starts.length-1])}`:"No start window";
  const preset=draftSlatePreset();
  const summary=selectedGames.length?`${selectedGames.length} of ${games.length} games · ${range}`:`0 of ${games.length} games selected`;
  return`<section class="draft-slate"><div class="draft-slate-head"><div><div class="draft-slate-title">Contest slate</div><div class="draft-slate-summary">${summary}</div></div><button class="draft-slate-toggle" onclick="toggleDraftSlatePanel()">${st.draftSlate.panelOpen?"Done":"Choose games"}</button></div>${selectedGames.length?`<div class="draft-slate-games">${selectedGames.map(game=>`<span class="draft-slate-chip">${esc(game.label)} · ${draftDisplayTime(game.startMs)||"Time TBD"}</span>`).join("")}</div>`:""}${st.draftSlate.panelOpen?`<div class="draft-slate-panel"><div class="draft-slate-presets"><button class="draft-slate-preset${preset==="all"?" active":""}" onclick="setDraftSlatePreset('all')">Full slate</button><button class="draft-slate-preset${preset==="open"?" active":""}" onclick="setDraftSlatePreset('open')">Open games</button><button class="draft-slate-preset${preset==="after7"?" active":""}" onclick="setDraftSlatePreset('after7')">7 PM+</button><button class="draft-slate-preset${preset==="after9"?" active":""}" onclick="setDraftSlatePreset('after9')">9 PM+</button><button class="draft-slate-preset${preset==="clear"?" active":""}" onclick="setDraftSlatePreset('clear')">Clear</button></div><div class="draft-game-grid">${games.map(game=>`<button class="draft-game-option${selected.has(game.id)?" selected":""}" onclick="toggleDraftSlateGame('${esc(game.id)}')"><span class="draft-game-check">✓</span><span><span class="draft-game-matchup">${esc(game.label)}</span><span class="draft-game-status">${game.started?"Started / locked":"Available"}</span></span><span class="draft-game-time">${draftDisplayTime(game.startMs)||"TBD"}</span></button>`).join("")}</div><div class="draft-slate-note">Changing games resets drafted marks so the board stays aligned with this contest.</div></div>`:""}</section>`;
}

function getDraftBoard(){
  return getMemo(`draftBoard:${draftSlateMemoKey()}`,()=>{
  const board=[];
  const aiMap=new Map();
  st.picks.forEach(p=>{if(p.player)aiMap.set(normalizePlayerName(p.player),p)});
  for(const p of st.tonight){
    if(!draftRowInSlate(p))continue;
    const name=p.player_name;if(!name)continue;
    const logs=getPlayerLogs(name,false);
    if(!logs.length)continue;const most=logs[0]||{};
    const sH=toNum(most.Seas_H),sHR=toNum(most.Seas_HR),s2B=toNum(most.Seas_2B);
    const sTB=toNum(most.Seas_TB),sRBI=toNum(most.Seas_RBI),sR=toNum(most.Seas_R);
    const sSB=toNum(most.Seas_SB),sBB=toNum(most.Seas_BB),sHBP=toNum(most.Seas_HBP);
    const s3B=Math.max(0,(sTB-sH-s2B-3*sHR)/2)||0;
    const s1B=Math.max(0,sH-s2B-s3B-sHR)||0;
    const projUD=toNum(most.Seas_UD_FP)||(s1B*3+s2B*6+s3B*8+sHR*10+sBB*3+sHBP*3+sRBI*2+sR*2+sSB*4)||0;
    const l7H=toNum(most.L7_H),l7HR=toNum(most.L7_HR),l72B=toNum(most.L7_2B);
    const l7TB=toNum(most.L7_TB),l7RBI=toNum(most.L7_RBI),l7R=toNum(most.L7_R);
    const l7SB=toNum(most.L7_SB),l7BB=toNum(most.L7_BB),l7HBP=toNum(most.L7_HBP);
    const l73B=Math.max(0,(l7TB-l7H-l72B-3*l7HR)/2)||0;
    const l71B=Math.max(0,l7H-l72B-l73B-l7HR)||0;
    const l7UD=toNum(most.L7_UD_FP)||(l71B*3+l72B*6+l73B*8+l7HR*10+l7BB*3+l7HBP*3+l7RBI*2+l7R*2+l7SB*4)||0;
    const ai=aiMap.get(normalizePlayerName(name)),isSmash=ai&&normalizeConfidence(ai.confidence)==="SMASH";
    let pos="FLEX";const posRaw=(p.position||"").toUpperCase();
    if(posRaw.includes("C")||posRaw.includes("1B")||posRaw.includes("2B")||posRaw.includes("3B")||posRaw.includes("SS"))pos="IF";
    else if(posRaw.includes("OF")||posRaw.includes("LF")||posRaw.includes("CF")||posRaw.includes("RF"))pos="OF";
    const flags=getSampleFlags(name,false);
    board.push({name,team:p.team_abbr||"",opp:p.opp_abbr_tonight||"",pitcher:p.opp_pitcher_name||"TBD",hand:p.opp_pitcher_hand||"?",projUD:projUD.toFixed(1),l7UD:l7UD.toFixed(1),sH,sHR,sRBI,sR,sSB,sBB,isSmash,isPitcher:false,pos,returning:flags.returning,limitedSample:flags.limited});
  }
  for(const p of st.pTonight){
    if(!draftRowInSlate(p))continue;
    const name=p.player_name;if(!name)continue;
    const logs=getPlayerLogs(name,true);
    if(!logs.length)continue;const most=logs[0]||{};
    const sSO=toNum(most.Seas_SO),sER=toNum(most.Seas_ER),sW=toNum(most.Seas_W),sIP=toNum(most.Seas_IP);
    const qsRate=logs.length>0?logs.filter(g=>toNum(g.IP)>=6&&toNum(g.ER)<=3).length/logs.length:0;
    const projUD=toNum(most.Seas_UD_FP)||(sW*5+qsRate*5+sSO*3+sIP*3+sER*-3)||0;
    const l3SO=toNum(most.L3_SO),l3ER=toNum(most.L3_ER),l3W=toNum(most.L3_W),l3IP=toNum(most.L3_IP);
    const l3QS=logs.slice(0,3).filter(g=>toNum(g.IP)>=6&&toNum(g.ER)<=3).length/Math.min(3,logs.length);
    const l7UD=toNum(most.L7_UD_FP)||(l3W*5+l3QS*5+l3SO*3+l3IP*3+l3ER*-3)||0;
    const ai=aiMap.get(normalizePlayerName(name)),isSmash=ai&&normalizeConfidence(ai.confidence)==="SMASH";
    const flags=getSampleFlags(name,true);
    board.push({name,team:p.team_abbr||"",opp:p.opp_abbr_tonight||"",pitcher:"",hand:"",projUD:projUD.toFixed(1),l7UD:l7UD.toFixed(1),sSO,sER,sW,sIP,qsRate,isSmash,isPitcher:true,pos:"P",returning:flags.returning,limitedSample:flags.limited});
  }
  board.sort((a,b)=>parseFloat(b.projUD)-parseFloat(a.projUD));
  return board;
  });
}

function getMlbPitcherEra(name){
  const key=normalizePlayerName(name);
  const row=(st.pTonight||[]).find(p=>normalizePlayerName(p.player_name)===key);
  return row?toNum(row.Seas_ERA||row.L7_ERA||row.L3_ERA):0;
}

function getDraftStacks(){
  return getMemo(`draftStacks:${draftSlateMemoKey()}`,()=>{
    const board=getDraftBoard().filter(p=>!p.isPitcher);
    const byName=new Map(board.map(p=>[normalizePlayerName(p.name),p]));
    const byTeam=new Map();
    for(const row of st.tonight||[]){
      const key=normalizePlayerName(row.player_name);
      if(!key||!byName.has(key))continue;
      const team=row.team_abbr||"";
      if(!byTeam.has(team))byTeam.set(team,[]);
      byTeam.get(team).push(row);
    }
    const pairs=[];const seen=new Set();
    for(const [team,rows] of byTeam.entries()){
      for(let i=0;i<rows.length;i++){
        for(let j=i+1;j<rows.length;j++){
          const ra=rows[i],rb=rows[j];
          const a=byName.get(normalizePlayerName(ra.player_name));
          const b=byName.get(normalizePlayerName(rb.player_name));
          if(!a||!b)continue;
          const key=[normalizePlayerName(a.name),normalizePlayerName(b.name)].sort().join("|");
          if(seen.has(key))continue;
          seen.add(key);
          const era=getMlbPitcherEra(ra.opp_pitcher_name||rb.opp_pitcher_name);
          const venue=ra.venue_tonight||rb.venue_tonight||"";
          const coors=/coors/i.test(venue)||["LAD","COL"].includes(team);
          const weakPitcher=era>=4.5;
          const proj=toNum(a.projUD)+toNum(b.projUD);
          const score=proj+(weakPitcher?4:0)+(coors?5:0)+(toNum(a.l7UD)>toNum(a.projUD)?1:0)+(toNum(b.l7UD)>toNum(b.projUD)?1:0);
          const tags=[];
          if(coors)tags.push("⚡ HIGH TOTAL");
          if(weakPitcher)tags.push("STACK TARGET");
          if(team===ra.team_abbr&&team===rb.team_abbr)tags.push("🔗 CORRELATED");
          pairs.push({players:[a,b],score,combinedProj:proj.toFixed(1),tags,team,opp:a.opp,pitcher:ra.opp_pitcher_name||"TBD",era,venue});
        }
      }
    }
    return pairs.sort((a,b)=>b.score-a.score).slice(0,10);
  });
}

function getDraftStackTagMap(){
  return getMemo(`draftStackTags:${draftSlateMemoKey()}`,()=>{
    const map=new Map();
    getDraftStacks().forEach(stack=>{
      stack.players.forEach(p=>{
        const key=normalizePlayerName(p.name);
        if(!map.has(key))map.set(key,new Set());
        stack.tags.forEach(tag=>map.get(key).add(tag));
      });
    });
    return map;
  });
}


const STATS_WINDOWS=[['last_7d','Last 7 days'],['last_30d','Last 30 days'],['last_90d','Last 90 days'],['all_time','All time']];
const STATS_BREAK_EVEN=0.524;

function entryField(row,keys){for(const k of keys){if(row&&row[k]!==undefined&&row[k]!==null&&String(row[k]).trim()!=='')return row[k]}return ''}
function entryMetric(m){return typeof normalizePropMetric==='function'?normalizePropMetric(m):(typeof normalizePropName==='function'?normalizePropName(m):String(m||'').trim().toUpperCase())}
function entryPropLabel(metric){const key=entryMetric(metric);const labels={P_SO:"Passing yards",P_H:"Hits allowed",P_BB:"Walks allowed",P_ER:"Earned runs allowed",P_OUTS:"Pitching outs"};return labels[key]||propTypeLabel(key)}
function entryTeam(row){return String(entryField(row,['team_abbr','TEAM_ABBREVIATION','TEAM','team','teamAbbr','TEAM_ABBR'])||'').trim().toUpperCase()}
function entryOpp(row){return String(entryField(row,['opp_abbr_tonight','TONIGHT_OPP','OPP','opponent','OPPONENT','opp'])||'').trim().toUpperCase()}
function entryPlayer(row){return cleanName(entryField(row,['player_name','PLAYER_NAME','PLAYER','player','Player']))}
function entryPairId(a,b){a=String(a||'').trim().toUpperCase();b=String(b||'').trim().toUpperCase();if(!a||!b)return '';return [a,b].sort().join('|')}
function entryGameFromText(game){const s=String(game||'').trim();const m=s.match(/\b([A-Z]{2,4})\s*(?:@|vs\.?|VS)\s*([A-Z]{2,4})\b/);if(!m)return null;return {id:entryPairId(m[1],m[2]),label:s,teams:[m[1],m[2]]}}
function entryTodayISO(){const parts=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date()).reduce((a,p)=>(a[p.type]=p.value,a),{});return `${parts.year}-${parts.month}-${parts.day}`}
function entryDateISO(v){if(v===undefined||v===null||String(v).trim()==='')return '';const raw=String(v).trim();if(/^\d{4}-\d{2}-\d{2}$/.test(raw))return raw;const md=raw.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);if(md)return `${md[3]}-${md[1].padStart(2,"0")}-${md[2].padStart(2,"0")}`;const n=Number(raw);if(Number.isFinite(n)&&n>20000&&n<90000){const d=new Date(Math.round((n-25569)*86400*1000));return d.toISOString().slice(0,10)}const d=new Date(raw);if(Number.isNaN(d.getTime()))return typeof normalizeDate==='function'?normalizeDate(raw):'';const parts=new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(d).reduce((a,p)=>(a[p.type]=p.value,a),{});return `${parts.year}-${parts.month}-${parts.day}`}
function entryRowDate(row){return entryField(row,['DATE','date','GAME_DATE','game_date','Date','GAME_DAY','game_day','start_date','START_DATE','commence_time','COMMENCE_TIME','game_time','GAME_TIME','start_time','START_TIME'])}
function entryRowIsToday(row){const raw=entryRowDate(row);const iso=entryDateISO(raw);return !iso||iso===entryTodayISO()}
function entryStartValue(row){return entryField(row,['commence_time','COMMENCE_TIME','game_time','GAME_TIME','start_time','START_TIME','GAME_DATE','game_date','DATE','date'])}
function entryStartMeta(v){
  if(v===undefined||v===null||String(v).trim()==='')return{ms:Number.POSITIVE_INFINITY,quality:0};
  const raw=String(v).trim();
  const dateOnly=/^\d{4}-\d{2}-\d{2}$/.test(raw);
  const timeOnly=raw.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)(?:\s*(?:EDT|EST|ET))?$/i);
  let parsed=timeOnly?new Date(`${entryTodayISO()}T${String((Number(timeOnly[1])%12)+(timeOnly[3].toUpperCase()==="PM"?12:0)).padStart(2,"0")}:${timeOnly[2]}:00-04:00`):new Date(raw);
  if(Number.isNaN(parsed.getTime()))return{ms:Number.POSITIVE_INFINITY,quality:0};
  return{ms:parsed.getTime(),quality:dateOnly?1:2};
}
function entryStartMs(v){return entryStartMeta(v).ms}
function entryDisplayTime(v){const ms=entryStartMs(v);if(!Number.isFinite(ms))return '';return new Date(ms).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit',timeZone:'America/New_York',timeZoneName:'short'})}
function entryAllPicks(){return Array.isArray(st.picks)&&st.picks.length?st.picks:(Array.isArray(st.aiPicks)?st.aiPicks:[])}
function entryRosterRows(){const rows=[];const add=(arr,type)=>{(arr||[]).forEach(r=>{const player=entryPlayer(r),team=entryTeam(r),opp=entryOpp(r);if(player&&team&&opp)rows.push({player,team,opp,type,row:r,id:entryPairId(team,opp)})})};add(st.tonight,'player');add(st.pTonight,'player');add(st.gTonight,'player');return rows}
function getEntryGames(){return getMemo('gameEntry:games',()=>{
  const byId=new Map();
  const add=(id,label,teams=[],time='')=>{
    if(!id)return;
    const start=entryStartMeta(time);
    const baseLabel=label||teams.join(' vs ');
    if(!byId.has(id)){
      byId.set(id,{id,baseLabel,teams,time,sortTime:start.ms,timeQuality:start.quality});
      return;
    }
    const g=byId.get(id);
    if((baseLabel||'').includes('@'))g.baseLabel=baseLabel;
    if(start.quality>g.timeQuality||(start.quality===g.timeQuality&&start.ms<g.sortTime)){
      g.time=time;g.sortTime=start.ms;g.timeQuality=start.quality;
    }
  };
  entryLatestPicks().forEach(p=>{const g=entryGameFromText(rowField(p,"game","matchup"));if(g)add(g.id,`${g.teams[0]} @ ${g.teams[1]}`,g.teams,entryStartValue(p))});
  entryRosterRows().forEach(r=>{if(entryRowIsToday(r.row))add(r.id,`${r.team} vs ${r.opp}`,[r.team,r.opp],entryStartValue(r.row))});
  (st.schedule||[]).forEach(r=>{
    if(!entryRowIsToday(r))return;
    const away=String(entryField(r,['away_team','AWAY_TEAM','away','AWAY','away_abbr','away_team_abbr'])||'').toUpperCase();
    const home=String(entryField(r,['home_team','HOME_TEAM','home','HOME','home_abbr','home_team_abbr'])||'').toUpperCase();
    if(away&&home)add(entryPairId(away,home),`${away} @ ${home}`,[away,home],entryStartValue(r));
  });
  const now=Date.now();
  return [...byId.values()].map(g=>({...g,label:g.baseLabel,timeText:entryDisplayTime(g.time),started:Number.isFinite(g.sortTime)&&g.sortTime<=now}))
    .sort((a,b)=>(a.started-b.started)||(a.started?(b.sortTime-a.sortTime):(a.sortTime-b.sortTime))||a.baseLabel.localeCompare(b.baseLabel));
})}
// Display-only start-time lookup. Unlike getEntryGames() (which filters to today
// for the Game Builder), this reads every schedule row regardless of date so the
// passive time labels on Shortlist/Picks/dashboard don't blank out when the
// Schedule tab lags a day behind. Memoized on dataVersion, so it refreshes with data.
function gameTimeLookup(){return getMemo('gameEntry:timeLookup',()=>{
  const byId=new Map();
  const consider=(id,timeVal)=>{
    if(!id)return;
    const meta=entryStartMeta(timeVal);
    if(!Number.isFinite(meta.ms))return;
    const existing=byId.get(id);
    if(!existing||meta.quality>existing.quality||(meta.quality===existing.quality&&meta.ms<existing.ms)){
      byId.set(id,{ms:meta.ms,quality:meta.quality,timeText:entryDisplayTime(timeVal)});
    }
  };
  (st.schedule||[]).forEach(r=>{
    const away=String(entryField(r,['away_team','AWAY_TEAM','away','AWAY','away_abbr','away_team_abbr'])||'').toUpperCase();
    const home=String(entryField(r,['home_team','HOME_TEAM','home','HOME','home_abbr','home_team_abbr'])||'').toUpperCase();
    if(away&&home)consider(entryPairId(away,home),entryStartValue(r));
  });
  entryLatestPicks().forEach(p=>{const g=entryGameFromText(rowField(p,"game","matchup"));if(g)consider(g.id,entryStartValue(p))});
  return byId;
})}
function gameTimeTextById(id){if(!id)return '';const hit=gameTimeLookup().get(id);if(hit&&hit.timeText)return hit.timeText;const game=getEntryGames().find(g=>g.id===id);return game?.timeText||''}
function gameStartTimeForTeams(team,opp){return gameTimeTextById(entryPairId(team,opp))}
function gameStartTimeForText(gameText){const parsed=entryGameFromText(gameText);return parsed?gameTimeTextById(parsed.id):''}
function setGameEntryGame(gameId){st.gameEntry=st.gameEntry||{selectedGame:null,legCount:GAME_ENTRY_DEFAULT_LEGS,entry:null};st.gameEntry.selectedGame=gameId;st.gameEntry.entry=null;st.dataVersion++;render()}
function setGameEntryLegs(n){st.gameEntry=st.gameEntry||{selectedGame:null,legCount:GAME_ENTRY_DEFAULT_LEGS,entry:null};st.gameEntry.legCount=Math.max(GAME_ENTRY_MIN_LEGS,Math.min(GAME_ENTRY_MAX_LEGS,parseInt(n)||GAME_ENTRY_DEFAULT_LEGS));st.gameEntry.entry=null;st.dataVersion++;render()}
function entryLatestPicks(){const rows=entryAllPicks().filter(p=>entryDateISO(rowField(p,"DATE"))===entryTodayISO());const maxRun=Math.max(0,...rows.map(p=>toNum(rowField(p,"RUN_NUMBER"))));return maxRun?rows.filter(p=>toNum(rowField(p,"RUN_NUMBER"))===maxRun):rows}
function entryFindProp(player,metric,line){const pn=normalizePlayerName(player),mn=entryMetric(metric),lt=String(line??'').trim();return (st.props||[]).find(p=>normalizePlayerName(p.PLAYER_NAME)===pn&&entryMetric(p.METRIC)===mn&&(lt===''||String(p.DK_LINE??'').trim()===lt))||(st.props||[]).find(p=>normalizePlayerName(p.PLAYER_NAME)===pn&&entryMetric(p.METRIC)===mn)||null}
function entryBookName(book){const k=String(book||'').toLowerCase();return {draftkings:'DK',fanduel:'FD',betmgm:'BetMGM',espnbet:'ESPN BET',caesars:'Caesars'}[k]||String(book||'')}
function entryBestBook(prop,lean){if(!prop)return null;const side=String(lean||'OVER').toUpperCase()==='UNDER'?'UNDER':'OVER';const book=prop[`BEST_${side}_BOOK`];const odds=prop[`BEST_${side}_ODDS`];if(!book||odds==='')return null;const delta=Number(prop[`BEST_${side}_DELTA_PP`]);return {book:String(book),odds,delta:Number.isFinite(delta)?delta:null,isDK:String(book).toLowerCase()==='draftkings'}}
function renderEntryBestBookLine(prop,lean){const b=entryBestBook(prop,lean);if(!b)return '';const color=b.isDK?'var(--push)':'var(--accent)';const delta=b.delta!==null&&!b.isDK&&Math.abs(b.delta)>0.05?` (${b.delta>0?'+':''}${b.delta.toFixed(1)}pp${b.delta>=3?' ⭐':''})`:'';return `<div style="font-size:var(--t-xs);color:${color};font-weight:800;margin-top:3px">🏪 Best @ ${entryBookName(b.book)} ${entryFmtOdds(b.odds)}${delta}</div>`}
function entryBestBookKey(leg){const b=entryBestBook(leg.prop,leg.lean);return b?entryBookName(b.book):''}
function entryPerfWLB(metric){const mn=entryMetric(metric);const row=(st.pickPerformance||[]).find(r=>String(rowField(r,"DIMENSION_TYPE")).toLowerCase()==='prop_type_norm'&&entryMetric(rowField(r,"DIMENSION_VALUE"))===mn&&String(rowField(r,"TIME_WINDOW"))==='all_time'&&String(rowField(r,"MIN_SAMPLE_FLAG")).toUpperCase()==='TRUE');const v=row?Number(rowField(row,"WILSON_LOWER_95")):NaN;return Number.isFinite(v)?v:GAME_ENTRY_DEFAULT_WLB}
function buildCandidatePool(gameId){const games=getEntryGames();const game=games.find(g=>g.id===gameId);if(!game)return {game:null,candidates:[]};const roster=entryRosterRows().filter(r=>r.id===gameId);const playerNames=new Set(roster.map(r=>normalizePlayerName(r.player)));const candidates=[];const seenAI=new Set();entryLatestPicks().forEach(p=>{const player=rowField(p,"player","PLAYER_NAME"),propType=rowField(p,"prop_type","METRIC"),line=rowField(p,"line","DK_LINE"),conf=rowField(p,"confidence"),g=entryGameFromText(rowField(p,"game","matchup"));let inGame=g&&g.id===gameId;if(!inGame&&playerNames.has(normalizePlayerName(player)))inGame=true;if(!inGame)return;const prop=entryFindProp(player,propType,line);if(!prop)return;const lean=String(rowField(p,"lean")||'OVER').toUpperCase()==='UNDER'?'UNDER':'OVER';const odds=lean==='OVER'?prop.OVER_ODDS:prop.UNDER_ODDS;if(!odds)return;const key=`${normalizePlayerName(player)}|${entryMetric(propType)}|${lean}`;seenAI.add(key);candidates.push({player,prop_type:entryMetric(propType),line:line||prop.DK_LINE,lean,odds,ai_tier:normalizeConfidence(conf),source:'AI',prop})});(st.props||[]).forEach(prop=>{if(!playerNames.has(normalizePlayerName(prop.PLAYER_NAME)))return;['OVER','UNDER'].forEach(lean=>{const odds=lean==='OVER'?prop.OVER_ODDS:prop.UNDER_ODDS;if(!odds)return;const key=`${normalizePlayerName(prop.PLAYER_NAME)}|${entryMetric(prop.METRIC)}|${lean}`;if(seenAI.has(key))return;candidates.push({player:prop.PLAYER_NAME,prop_type:entryMetric(prop.METRIC),line:prop.DK_LINE,lean,odds,ai_tier:'LEAN',source:'DK',prop})})});return {game,candidates}}
function scoreCandidate(c){const tier=normalizeConfidence(c.ai_tier||'LEAN');const tierWeight=GAME_ENTRY_TIER_WEIGHTS[tier]||GAME_ENTRY_TIER_WEIGHTS.LEAN;const wlb=entryPerfWLB(c.prop_type);return {...c,ai_tier:tier,tier_weight:tierWeight,wlb,leg_score:tierWeight*wlb}}
function selectTopN(candidates,n){const sorted=candidates.map(scoreCandidate).sort((a,b)=>b.leg_score-a.leg_score);const used=new Set(),perPlayer=new Map(),out=[];for(const c of sorted){const playerKey=normalizePlayerName(c.player),key=`${playerKey}|${entryMetric(c.prop_type)}`;if(used.has(key))continue;if((perPlayer.get(playerKey)||0)>=GAME_ENTRY_MAX_LEGS_PER_PLAYER)continue;used.add(key);perPlayer.set(playerKey,(perPlayer.get(playerKey)||0)+1);out.push(c);if(out.length>=n)break}return out}
function entryAmericanToDecimal(odds){const o=Number(String(odds).replace(/[^0-9+\-.]/g,''));if(!Number.isFinite(o)||o===0)return 1;return o>0?1+o/100:1+100/Math.abs(o)}
function entryDecimalToAmerican(dec){if(!Number.isFinite(dec)||dec<=1)return 0;return dec>=2?Math.round((dec-1)*100):-Math.round(100/(dec-1))}
function entryFmtOdds(odds){if(typeof fmtOdds==='function')return fmtOdds(odds);const o=Number(odds);return Number.isFinite(o)?(o>0?`+${o}`:`${o}`):String(odds||'—')}
function calculateParlayMath(legs){const decimal=legs.reduce((p,l)=>p*entryAmericanToDecimal(l.odds),1);return {decimal,american:entryDecimalToAmerican(decimal),return10:decimal*10,profit10:(decimal*10)-10}}
function buildGameEntry(){const ge=st.gameEntry||{};if(!ge.selectedGame)return null;const {game,candidates}=buildCandidatePool(ge.selectedGame);if(!game)return null;const requested=ge.legCount||GAME_ENTRY_DEFAULT_LEGS;const legs=selectTopN(candidates,requested);const math=calculateParlayMath(legs);return {game,requested,legs,candidates,math,score:legs.reduce((s,l)=>s+l.leg_score,0)}}
function renderGameSelector(games){
  if(!games.length)return `<section class="entry-shell"><div class="entry-header"><div><div class="analysis-eyebrow">Game builder</div><div class="entry-title">1. Choose a matchup</div><div class="entry-subtitle">No current slate is available from the latest engine snapshot.</div></div></div></section>`;
  const sel=st.gameEntry?.selectedGame;
  const upcoming=games.filter(g=>!g.started);
  const started=games.filter(g=>g.started);
  const renderCard=g=>{
    const candidateCount=buildCandidatePool(g.id).candidates.length;
    const selected=sel===g.id;
    const status=g.started?"Locked":selected?"Selected":"Open";
    return `<button class="entry-game-card ${selected?"selected":""} ${g.started?"started":""}" onclick='setGameEntryGame(${JSON.stringify(g.id)})'>
      <div class="entry-game-top"><span class="entry-game-matchup">${esc(g.baseLabel)}</span><span class="entry-game-time">${esc(g.timeText||"Time TBD")}</span></div>
      <div class="entry-game-meta"><span class="entry-game-status">${status}</span><span class="entry-game-props">${candidateCount?`${candidateCount} options`:"No props"}</span></div>
    </button>`;
  };
  const openBoard=upcoming.length?`<div class="entry-game-grid">${upcoming.map(renderCard).join("")}</div>`:`<div class="entry-open-empty">No games remain open on this slate.</div>`;
  const lockedBoard=started.length?`<details class="entry-locked"><summary>${started.length} started / locked game${started.length===1?"":"s"}</summary><div class="entry-game-grid">${started.map(renderCard).join("")}</div></details>`:"";
  return `<section class="entry-shell"><div class="entry-header"><div><div class="analysis-eyebrow">Game builder</div><div class="entry-title">1. Choose a matchup</div><div class="entry-subtitle">Open games first · ordered by first pitch · select one to build an entry</div></div><div class="entry-count">${upcoming.length} open</div></div>${openBoard}${lockedBoard}</section>`;
}
function renderLegCountSelector(){const cur=st.gameEntry?.legCount||GAME_ENTRY_DEFAULT_LEGS;const counts=Array.from({length:GAME_ENTRY_MAX_LEGS-GAME_ENTRY_MIN_LEGS+1},(_,i)=>i+GAME_ENTRY_MIN_LEGS);return `<div class="section"><div class="card"><div class="card-title">2. CHOOSE LEG COUNT</div><div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0">${counts.map(n=>`<button onclick="setGameEntryLegs(${n})" style="border:1px solid ${cur===n?'var(--accent)':'#334155'};background:${cur===n?'var(--accent)':'transparent'};color:${cur===n?'#07130b':'inherit'};border-radius:999px;padding:7px 12px;font-weight:900;cursor:pointer">${n}</button>`).join('')}</div><div style="font-size:var(--t-xs);color:var(--push)">Build a 2-8 leg entry from available props in this matchup.</div></div></div>`}
function renderEntry(entry){if(!entry)return '';if(!entry.candidates.length)return `<div class="section"><div class="card"><div class="card-title">${icon('entry')}3. RECOMMENDED ENTRY</div><div class="empty" style="padding:24px;text-align:center">No props available for this game yet.</div></div></div>`;if(!entry.legs.length)return `<div class="section"><div class="card"><div class="card-title">${icon('entry')}3. RECOMMENDED ENTRY</div><div class="empty" style="padding:24px;text-align:center">No usable odds for this game yet.</div></div></div>`;const odds=entry.math.american;const oddsText=odds>0?`+${odds}`:`${odds}`;const books=[...new Set(entry.legs.map(entryBestBookKey).filter(Boolean))];const warning=books.length>=2?`<div style="margin-top:12px;background:color-mix(in srgb, var(--warn) 8%, transparent);border:1px solid color-mix(in srgb, var(--warn) 33%, transparent);color:var(--warn);border-radius:8px;padding:8px;font-size:var(--t-xs)">${icon('warn')}Cross-book: legs split across ${books.join(', ')}. Single-book parlay may price differently.</div>`:'';const shortage=entry.legs.length<entry.requested?`<div style="margin-top:8px;color:var(--warn);font-size:var(--t-xs)">Only ${entry.legs.length} legs available (you requested ${entry.requested}).</div>`:'';return `<div class="section"><div class="card"><div class="card-title">${icon('entry')}3. RECOMMENDED ENTRY — ${esc(entry.game.label)} · ${entry.legs.length} legs</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0"><div class="stat-box"><div class="val">${oddsText}</div><div class="lbl">Combined</div></div><div class="stat-box"><div class="val">$${entry.math.return10.toFixed(0)}</div><div class="lbl">$10 return</div></div><div class="stat-box"><div class="val">${entry.score.toFixed(2)}</div><div class="lbl">Score</div></div></div>${shortage}<div style="height:1px;background:#334155;margin:12px 0"></div>${entry.legs.map((l,i)=>`<div style="padding:10px 0;border-bottom:1px solid #263238"><div style="display:flex;justify-content:space-between;gap:8px"><div style="font-weight:900">${i+1}. ${typeof playerLink==='function'?playerLink(l.player,l.prop_type,l.line):esc(l.player)} — ${esc(entryPropLabel(l.prop_type))} ${l.lean} ${l.line}</div><div style="font-weight:900;color:${l.lean==='OVER'?'var(--over)':'var(--under)'}">${entryFmtOdds(l.odds)}</div></div><div style="font-size:var(--t-xs);color:var(--push);margin-top:4px">Why: ${l.ai_tier} × ${esc(entryPropLabel(l.prop_type))} WLB ${l.wlb.toFixed(2)} = ${l.leg_score.toFixed(2)} · ${l.source}</div>${renderEntryBestBookLine(l.prop,l.lean)}</div>`).join('')}${warning}<button onclick="copyEntryToClipboard()" style="margin-top:14px;border:1px solid var(--accent);background:color-mix(in srgb, var(--accent) 13%, transparent);color:var(--accent);border-radius:8px;padding:10px 12px;font-weight:900;cursor:pointer;width:100%">${window.__entryCopied?'✓ Copied':'Copy entry'}</button></div></div>`}
function renderGameEntryView(){st.gameEntry=st.gameEntry||{selectedGame:null,legCount:GAME_ENTRY_DEFAULT_LEGS,entry:null};const games=getEntryGames();let html=renderGameSelector(games);if(st.gameEntry.selectedGame){html+=renderLegCountSelector();html+=renderEntry(buildGameEntry())}return html}
function entryCopyText(entry){const odds=entry.math.american;const oddsText=odds>0?`+${odds}`:`${odds}`;return `${entry.game.label} — ${entry.legs.length}-leg entry\n${entry.legs.map((l,i)=>`${i+1}. ${l.player} - ${entryPropLabel(l.prop_type)} ${l.lean} ${l.line}`).join('\n')}\nCombined ${oddsText} | $10 → $${entry.math.return10.toFixed(0)}\nBuilt: ${new Date().toLocaleString()}`}
function copyEntryToClipboard(){const entry=buildGameEntry();if(!entry)return;const text=entryCopyText(entry);if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(()=>{window.__entryCopied=true;render();setTimeout(()=>{window.__entryCopied=false;render()},1200)}).catch(()=>entryShowCopyFallback(text))}else entryShowCopyFallback(text)}
function entryShowCopyFallback(text){window.__entryCopied=false;const box=document.createElement('textarea');box.value=text;box.style.position='fixed';box.style.left='10px';box.style.bottom='10px';box.style.width='320px';box.style.height='160px';box.style.zIndex='9999';document.body.appendChild(box);box.focus();box.select()}

function setStatsTimeWindow(w){st.statsTimeWindow=w;render()}
function setStatsLeaderMetric(metric){st.statsLeaderMetric=metric;st.leaderDateOffset=0;render()}
function setLeaderMode(mode){st.leaderMode=mode==="live"?"live":"final";st.leaderDateOffset=0;render()}
function shiftLeaderDate(delta){st.leaderDateOffset=Math.max(0,(st.leaderDateOffset||0)+delta);render()}
function getDailyLeaders(metric){
  const pitcher=metric==="P_SO";
  const stat= pitcher?"SO":metric;
  const logs=pitcher?st.pGameLogs:st.gameLogs;
  const today=easternTodayISO();
  const dated=(logs||[]).map(row=>({...row,_leaderDate:entryDateISO(rowField(row,"game_date","GAME_DATE","DATE"))})).filter(row=>row._leaderDate);
  const mode=st.leaderMode==="live"?"live":"final";
  const finalDates=[...new Set(dated.filter(row=>row._leaderDate<today).map(row=>row._leaderDate))].sort().reverse();
  const maxOffset=Math.max(0,finalDates.length-1);
  const offset=Math.min(Math.max(0,st.leaderDateOffset||0),maxOffset);
  if(offset!==st.leaderDateOffset)st.leaderDateOffset=offset;
  const date=mode==="live"?today:(finalDates[offset]||"");
  if(!date)return{date:"",rows:[],mode,hasPrevious:false,hasNext:false};
  const grouped=new Map();
  dated.filter(row=>row._leaderDate===date).forEach(row=>{
    const name=cleanName(rowField(row,"player_name","PLAYER_NAME","player"));
    if(!name)return;
    const key=normalizePlayerName(name);
    const current=grouped.get(key)||{
      name,team:String(rowField(row,"team_abbr","TEAM_ABBR","team")||""),
      opp:String(rowField(row,"opp_abbr","OPP_ABBR","opponent")||""),
      value:0,games:0,pitcher
    };
    current.value+=toNum(rowField(row,stat));
    current.games+=1;
    grouped.set(key,current);
  });
  return{
    date,mode,
    hasPrevious:mode==="final"&&offset<maxOffset,
    hasNext:mode==="final"&&offset>0,
    rows:[...grouped.values()].filter(row=>row.value>0).sort((a,b)=>b.value-a.value||a.name.localeCompare(b.name)).slice(0,10)
  };
}
function renderDailyLeaders(){
  const metric=st.statsLeaderMetric||"H";
  const board=getDailyLeaders(metric);
  const labels={H:"Hits",HR:"Home runs",RBI:"RBI",P_SO:"Passing yards"};
  const metricLabel=labels[metric]||metric;
  const dateLabel=board.date?new Date(`${board.date}T12:00:00`).toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric"}):"Latest completed slate";
  const live=board.mode==="live";
  const modeControls=`<div class="daily-leaders-mode"><button class="${live?"":"active"}" onclick="setLeaderMode('final')">Final</button><button class="${live?"active":""}" onclick="setLeaderMode('live')">Today so far</button></div>`;
  const dateNav=live?"":`<div class="daily-leaders-date-nav"><button onclick="shiftLeaderDate(1)" ${board.hasPrevious?"":"disabled"} aria-label="Previous completed slate">‹</button><button onclick="shiftLeaderDate(-1)" ${board.hasNext?"":"disabled"} aria-label="Next completed slate">›</button></div>`;
  const controls=[["H","Hits"],["HR","Home Runs"],["RBI","RBI"],["P_SO","Pitcher Ks"]]
    .map(([value,label])=>`<button class="daily-leaders-metric ${metric===value?"active":""}" onclick="setStatsLeaderMetric('${value}')">${label}</button>`).join("");
  const rows=board.rows.map((row,index)=>{
    const detail=[row.team,row.opp?`vs ${row.opp}`:"",row.games>1?`${row.games} games`:""].filter(Boolean).join(" · ");
    return`<div class="daily-leader-row" onclick="streakToDash(decodeURIComponent('${encodeURIComponent(row.name)}'),'${metric}','')"><div class="daily-leader-rank">${String(index+1).padStart(2,"0")}</div><div><div class="daily-leader-name">${esc(row.name)}</div><div class="daily-leader-meta">${esc(detail)}</div></div><div class="daily-leader-team">${row.pitcher?"PITCHER":"BATTER"}</div><div class="daily-leader-value">${row.value}</div></div>`;
  }).join("");
  const sourceLabel=live?`<span class="daily-leaders-live">LIVE / INCOMPLETE</span> · games currently available in MLB game logs`:"final box scores from MLB game logs";
  const emptyLabel=live?"No results have reached today's game logs yet.":"No completed-game data available for this metric.";
  return`<section class="daily-leaders"><div class="daily-leaders-head"><div><div class="analysis-eyebrow">Daily results</div><div class="daily-leaders-title">${esc(metricLabel)} Leaders</div><div class="daily-leaders-sub">${esc(dateLabel)} · ${sourceLabel}</div></div><div class="daily-leaders-toolbar">${modeControls}${dateNav}<div class="daily-leaders-metrics">${controls}</div></div></div>${rows?`<div class="daily-leaders-list">${rows}</div>`:`<div class="empty" style="padding:24px;text-align:center">${emptyLabel}</div>`}</section>`;
}
function statField(row,name){return row?.[name]??row?.[name.toLowerCase()]??row?.[name.toUpperCase()]??''}
function statNum(row,name){return toNum(statField(row,name))}
function statBool(row,name){const v=String(statField(row,name)).trim().toUpperCase();return v==='TRUE'||v==='YES'||v==='1'}
function statPct(v){const n=Number(v);return Number.isFinite(n)?(n*100).toFixed(1)+'%':'—'}
function statPct0(v){const n=Number(v);return Number.isFinite(n)?Math.round(n*100)+'%':'—'}
function statSigned(v){const n=Number(v);if(!Number.isFinite(n))return '—';return (n>0?'+':'')+n.toFixed(3)}
function statRoiPct(v){const n=Number(v);if(!Number.isFinite(n))return '—';return `${n>0?'+':''}${(n*100).toFixed(1)}%`}
function statRoiSummary(r){const n=Math.round(statNum(r,'N_PRICED')),actual=statNum(r,'ACTUAL_ROI_PER_PICK');return n>0&&Number.isFinite(actual)?`actual ${statRoiPct(actual)} on ${n} · flat ${statSigned(statNum(r,'ROI_PER_PICK'))}`:`flat ${statSigned(statNum(r,'ROI_PER_PICK'))}`}
function priceDisciplineOddsValue(v){const n=Number(v);return Number.isFinite(n)&&n!==0?n:null}
function priceDisciplineCurrentPrice(pick){
  const captured=priceDisciplineOddsValue(rowField(pick,'PICK_ODDS'));
  if(captured!==null)return{odds:captured,book:String(rowField(pick,'PICK_BOOK')||'captured')};
  const prop=findPropForPick(rowField(pick,'player'),rowField(pick,'prop_type'),rowField(pick,'line'));
  const best=getBestBookForLean(prop,rowField(pick,'lean'));
  if(best&&priceDisciplineOddsValue(best.odds)!==null)return{odds:Number(best.odds),book:formatBookName(best.book)};
  const side=normalizeLeanText(rowField(pick,'lean'))==='UNDER'?'UNDER':'OVER';
  const reference=priceDisciplineOddsValue(mbField(prop,`${side}_ODDS`));
  return reference===null?null:{odds:reference,book:formatBookName(mbField(prop,'REFERENCE_BOOK')||mbField(prop,'BOOK')||'DK')};
}
function priceDisciplineCohorts(pick,rows){
  const method=String(rowField(pick,'SELECTION_METHOD')).trim().toUpperCase();
  const confidence=method==='VALIDATED_MODEL'?'VALIDATED':normalizeConfidence(rowField(pick,'confidence'));
  const prop=normalizePropMetric(rowField(pick,'prop_type'));
  const validated=method==='VALIDATED_MODEL';
  const candidates=(validated?[
    getMetricsForSlice(rows,'selection_method_norm',method,'all_time'),
    getMetricsForSlice(rows,'confidence_norm','VALIDATED','all_time'),
  ]:[
    method&&getMetricsForSlice(rows,'selection_method_norm',method,'all_time'),
    confidence&&getMetricsForSlice(rows,'confidence_norm',confidence,'all_time'),
    prop&&getMetricsForSlice(rows,'prop_type_norm',prop,'all_time'),
  ]).filter(r=>r&&statBool(r,'MIN_SAMPLE_FLAG')&&statNum(r,'WILSON_LOWER_95')>0);
  const unique=[...new Map(candidates.map(r=>[`${statField(r,'DIMENSION_TYPE')}|${statField(r,'DIMENSION_VALUE')}`,r])).values()];
  return unique;
}
function evaluatePriceDiscipline(pick,rows){
  const cohorts=priceDisciplineCohorts(pick,rows),price=priceDisciplineCurrentPrice(pick);
  if(!cohorts.length)return{pick,price,status:'LOW SAMPLE',reason:'No qualifying historical cohort'};
  const conservative=Math.min(...cohorts.map(r=>statNum(r,'WILSON_LOWER_95')));
  const fair=Math.min(...cohorts.map(r=>statNum(r,'HIT_RATE')));
  const thresholdOdds=impliedToAmerican(conservative);
  if(!price)return{pick,price,status:'NO PRICE',fair,conservative,thresholdOdds,reason:'No current sportsbook price'};
  const marketProb=impliedProb(price.odds);
  const edge=marketProb===null?null:conservative-marketProb;
  return{pick,price,fair,conservative,thresholdOdds,edge,status:edge!==null&&edge>=0?'BET':'PASS',cohorts};
}
function renderPriceDiscipline(rows){
  const active=getActivePicks();
  const hasStatuses=active.some(p=>String(rowField(p,'RECOMMENDATION_STATUS')).trim());
  const playable=hasStatuses?active.filter(p=>String(rowField(p,'RECOMMENDATION_STATUS')).trim().toUpperCase()==='PLAYABLE'):active;
  if(!playable.length)return'';
  const evaluated=playable.map(p=>evaluatePriceDiscipline(p,rows)).sort((a,b)=>{
    const order={BET:0,PASS:1,'NO PRICE':2,'LOW SAMPLE':3};
    return(order[a.status]??9)-(order[b.status]??9)||(Number(b.edge)||-99)-(Number(a.edge)||-99);
  });
  const bets=evaluated.filter(r=>r.status==='BET').length,passes=evaluated.filter(r=>r.status==='PASS').length;
  const statusColor=s=>s==='BET'?'var(--over)':s==='PASS'?'var(--under)':'var(--warn)';
  return`<div style="padding:0 16px 10px">
    <div style="display:flex;justify-content:space-between;gap:12px;align-items:end;margin-bottom:6px">
      <div><div style="color:var(--accent);font-size:var(--t-sm);font-weight:800">Price Discipline — Current Slate</div><div style="font-size:var(--t-xs);color:var(--push);margin-top:2px">Advisory only. Current price must beat the most conservative qualified all-time cohort.</div></div>
      <div style="font-size:var(--t-xs);color:var(--ink-1);white-space:nowrap">${bets} BET · ${passes} PASS</div>
    </div>
    <div class="card" style="padding:0;overflow-x:auto">
      <table style="width:100%;min-width:760px;border-collapse:collapse;font-size:var(--t-xs)">
        <thead><tr style="color:var(--push)"><th style="text-align:left;padding:8px">PLAYER</th><th>PROP</th><th>PRICE</th><th>FAIR</th><th>CONSERVATIVE</th><th>MIN PRICE</th><th>EDGE</th><th>CALL</th></tr></thead>
        <tbody>${evaluated.map(r=>{
          const p=r.pick,edge=Number(r.edge),edgeText=Number.isFinite(edge)?`${edge>=0?'+':''}${(edge*100).toFixed(1)}pp`:'—';
          return`<tr style="border-top:1px solid #26313a"><td style="padding:8px;font-weight:800;color:var(--ink-1)">${playerLink(rowField(p,'player'),rowField(p,'prop_type'),rowField(p,'line'))}</td><td style="text-align:center">${esc(propTypeLabel(rowField(p,'prop_type')))} ${esc(normalizeLeanText(rowField(p,'lean')))} ${esc(rowField(p,'line'))}</td><td style="text-align:center">${r.price?`${fmtOdds(r.price.odds)} <span style="color:var(--push)">${esc(r.price.book)}</span>`:'—'}</td><td style="text-align:center">${Number.isFinite(r.fair)?statPct(r.fair):'—'}</td><td style="text-align:center">${Number.isFinite(r.conservative)?statPct(r.conservative):'—'}</td><td style="text-align:center">${r.thresholdOdds!==null&&r.thresholdOdds!==undefined?fmtOdds(r.thresholdOdds):'—'}</td><td style="text-align:center;color:${Number.isFinite(edge)?statusColor(r.status):'var(--push)'};font-weight:800">${edgeText}</td><td style="text-align:center"><span style="color:${statusColor(r.status)};font-weight:900">${r.status}</span></td></tr>`;
        }).join('')}</tbody>
      </table>
    </div>
    <div style="font-size:var(--t-xs);color:var(--push);margin-top:5px">MIN PRICE is the worst price worth accepting under the conservative estimate. PASS does not remove a tracked pick.</div>
  </div>`;
}
function statsRowsForWindow(rows,w){return (rows||[]).filter(r=>String(statField(r,'TIME_WINDOW'))===w)}
function getMetricsForSlice(rows,dimType,dimValue,timeWindow){return (rows||[]).find(r=>String(statField(r,'DIMENSION_TYPE'))===dimType&&String(statField(r,'DIMENSION_VALUE'))===String(dimValue)&&String(statField(r,'TIME_WINDOW'))===timeWindow)||null}
function statsWindowLabel(w){return (STATS_WINDOWS.find(x=>x[0]===w)||[])[1]||w}
function renderTimeWindowSelector(currentWindow){return `<div class="stats-strip" style="position:sticky;top:0;z-index:5;display:flex;gap:6px">${STATS_WINDOWS.map(([w,l])=>`<button class="tab-btn ${currentWindow===w?'active':''}" onclick="setStatsTimeWindow('${w}')" style="white-space:nowrap;${currentWindow===w?'background:var(--accent);color:#07110b;border-color:var(--accent);':''}">${l}</button>`).join('')}</div>`}
function detectDrifts(rows,threshold=0.10){const all=(rows||[]).filter(r=>String(statField(r,'TIME_WINDOW'))==='all_time'&&statBool(r,'MIN_SAMPLE_FLAG'));const recent=(rows||[]).filter(r=>String(statField(r,'TIME_WINDOW'))==='last_30d'&&statBool(r,'MIN_SAMPLE_FLAG'));const map=new Map(all.map(r=>[`${statField(r,'DIMENSION_TYPE')}|${statField(r,'DIMENSION_VALUE')}`,r]));return recent.map(r=>{const key=`${statField(r,'DIMENSION_TYPE')}|${statField(r,'DIMENSION_VALUE')}`;const base=map.get(key);if(!base)return null;const hr30=statNum(r,'HIT_RATE'),hrAll=statNum(base,'HIT_RATE');const delta=hr30-hrAll;if(!Number.isFinite(delta)||Math.abs(delta)<threshold)return null;return{dimension_type:statField(r,'DIMENSION_TYPE'),dimension_value:statField(r,'DIMENSION_VALUE'),hit_rate_last_30d:hr30,hit_rate_all_time:hrAll,delta,n:statNum(r,'N_PICKS_DECISIVE')}}).filter(Boolean).sort((a,b)=>Math.abs(b.delta)-Math.abs(a.delta))}
function renderDriftAlerts(rows){const drifts=detectDrifts(rows);if(!drifts.length)return '';const shown=drifts.slice(0,5);return `<div style="padding:0 16px 8px"><div style="color:var(--warn);font-size:var(--t-sm);font-weight:800;margin-bottom:6px">Drift Alerts</div>${shown.map(d=>`<div class="card" style="border-color:var(--warn-line);margin-bottom:6px"><div style="font-size:var(--t-sm);color:var(--warn);font-weight:800">⚠️ DRIFT — ${esc(String(d.dimension_value||d.dimension_type))}</div><div style="font-size:var(--t-xs);color:var(--ink-1);margin-top:4px">last 30d ${statPct(d.hit_rate_last_30d)} vs all-time ${statPct(d.hit_rate_all_time)} (${d.delta>0?'+':''}${Math.round(d.delta*100)}pp on n=${Math.round(d.n)})</div></div>`).join('')}${drifts.length>5?`<div style="color:var(--push);font-size:var(--t-xs);padding:2px 4px">... and ${drifts.length-5} more</div>`:''}</div>`}
function renderOverallCard(rows,w){const r=getMetricsForSlice(rows,'overall','',w);if(!r)return `<div class="empty">No overall stats for ${statsWindowLabel(w)}.</div>`;const low=!statBool(r,'MIN_SAMPLE_FLAG');const nPriced=Math.round(statNum(r,'N_PRICED'));const actualRoi=statNum(r,'ACTUAL_ROI_PER_PICK');const hasActual=nPriced>0&&Number.isFinite(actualRoi);return `<div class="card" style="margin:0 16px 10px;border-color:color-mix(in srgb, var(--accent) 27%, transparent)"><div class="card-title">OVERALL — ${statsWindowLabel(w)} ${low?'<span style="font-size:var(--t-xs);color:var(--warn)">(low sample)</span>':''}</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;align-items:end"><div><div style="font-size:34px;font-weight:900;color:var(--accent)">${statPct(statNum(r,'HIT_RATE'))}</div><div style="font-size:var(--t-xs);color:var(--push)">Push-adjusted hit rate</div><div style="font-size:var(--t-sm);color:var(--ink-1);margin-top:6px">${Math.round(statNum(r,'N_PICKS_DECISIVE'))} decisive / ${Math.round(statNum(r,'N_PICKS'))} picks</div></div><div style="text-align:right"><div style="font-size:var(--t-lg);font-weight:800;color:${(hasActual?actualRoi:statNum(r,'ROI_PER_PICK'))>=0?'var(--over)':'var(--under)'}">${hasActual?`Actual ROI ${statRoiPct(actualRoi)}`:`Flat ROI/pick ${statSigned(statNum(r,'ROI_PER_PICK'))}`}</div><div style="font-size:var(--t-xs);color:var(--push)">${hasActual?`${nPriced} picks with captured prices · ${statSigned(statNum(r,'ACTUAL_PROFIT_UNITS'))}u`:'No captured prices yet · flat -115 proxy'}</div>${hasActual?`<div style="font-size:var(--t-xs);color:var(--ink-muted);margin-top:2px">Flat -115 comparison ${statSigned(statNum(r,'ROI_PER_PICK'))}</div>`:''}</div></div></div>`}
function auditLabel(dimension,value){
  const labels={
    model_era:{
      legacy_v1:'Legacy v1 · before May 24',
      market_enriched_v2:'Market-enriched v2 · May 24–Jul 16',
      flash_review_v3:'Flash review v3 · Jul 17–22',
      calibrated_hybrid_v4:'Calibrated hybrid v4 · Jul 23+',
      mlb_hybrid_calibrated_v1:'Explicit calibrated v1',
      legacy_unknown:'Legacy · date unknown',
    },
    cohort_norm:{
      'PLAYABLE · VALIDATED_MODEL':'Playable · validated model',
      'PLAYABLE · GEMINI':'Playable · Gemini reviewed',
      'RESEARCH · VALIDATED_MODEL':'Research · validated challenger',
      'RESEARCH · GEMINI':'Research · Gemini reviewed',
      'LEGACY_RESEARCH · VALIDATED_MODEL':'Legacy research · validated model',
      'LEGACY_RESEARCH · GEMINI':'Legacy research · Gemini',
    },
    odds_bucket:{
      plus_money:'Plus money',
      '-101_to_-125':'-101 to -125',
      '-126_to_-150':'-126 to -150',
      '-151_to_-200':'-151 to -200',
      'below_-200':'Below -200',
      unknown:'Price not captured',
    },
  };
  return labels[dimension]?.[value]||String(value||'Unknown').replaceAll('_',' ');
}
function auditRows(rows,dimension,w){
  return statsRowsForWindow(rows,w)
    .filter(r=>String(statField(r,'DIMENSION_TYPE'))===dimension)
    .sort((a,b)=>statNum(b,'N_PICKS_DECISIVE')-statNum(a,'N_PICKS_DECISIVE'));
}
function renderAuditTable(rows,dimension,title,w){
  const data=auditRows(rows,dimension,w);
  if(!data.length)return '';
  return `<div class="card" style="padding:0;overflow-x:auto"><div class="card-title" style="padding:10px 12px 4px">${esc(title)}</div><table style="width:100%;min-width:620px;border-collapse:collapse;font-size:var(--t-xs)"><thead><tr><th style="text-align:left;padding:8px 12px">COHORT</th><th>N</th><th>HIT RATE</th><th>LOWER 95%</th><th>PRICE ROI</th></tr></thead><tbody>${data.map(r=>{
    const n=Math.round(statNum(r,'N_PICKS_DECISIVE')),nPriced=Math.round(statNum(r,'N_PRICED')),roi=statNum(r,'ACTUAL_ROI_PER_PICK'),qualified=statBool(r,'MIN_SAMPLE_FLAG');
    const roiText=nPriced>0&&Number.isFinite(roi)?`${statRoiPct(roi)} · ${nPriced} priced`:'No captured prices';
    return `<tr style="border-top:1px solid var(--border-1)"><td style="padding:8px 12px;color:var(--ink-1);font-weight:750">${esc(auditLabel(dimension,statField(r,'DIMENSION_VALUE')))}${qualified?'':` <span style="color:var(--warn)">(low sample)</span>`}</td><td style="text-align:center">${n}</td><td style="text-align:center;font-weight:800">${statPct(statNum(r,'HIT_RATE'))}</td><td style="text-align:center;color:var(--push)">${statPct(statNum(r,'WILSON_LOWER_95'))}</td><td style="text-align:center;color:${roi>=0?'var(--over)':'var(--under)'}">${roiText}</td></tr>`;
  }).join('')}</tbody></table></div>`;
}
function renderEraCohortAudit(rows,w){
  const era=renderAuditTable(rows,'model_era','Model Era',w);
  const cohort=renderAuditTable(rows,'cohort_norm','Recommendation Cohort',w);
  const odds=renderAuditTable(rows,'odds_bucket','Captured Price Bucket',w);
  if(!era&&!cohort&&!odds)return '';
  return `<section style="padding:0 16px 10px"><div style="margin-bottom:7px"><div style="color:var(--accent);font-size:var(--t-sm);font-weight:800">Era & Cohort Audit</div><div style="color:var(--push);font-size:var(--t-xs);margin-top:2px">Historical systems are separated instead of treating every pick as one model. Lower 95% is the conservative hit-rate bound.</div></div><div style="display:grid;gap:10px">${era}${cohort}${odds}</div></section>`;
}
function hitBar(rate){const r=Math.max(0,Math.min(1,Number(rate)||0));const w=Math.round(r*100);const good=r>=STATS_BREAK_EVEN;return `<div style="height:7px;background:#26313a;border-radius:999px;overflow:hidden;margin-top:5px"><div style="height:100%;width:${w}%;background:${good?'var(--over)':'var(--under)'}"></div></div><div style="font-size:var(--t-xs);color:var(--push);margin-top:2px">break-even 52.4%</div>`}
function renderTierBreakdown(rows,w){const tiers=['VALIDATED','SMASH','STRONG','LEAN'];const found=tiers.map(t=>getMetricsForSlice(rows,'confidence_norm',t,w)).filter(Boolean);if(!found.length)return '';const aiRows=found.filter(r=>statField(r,'DIMENSION_VALUE')!=='VALIDATED');const rates=aiRows.map(r=>statNum(r,'HIT_RATE'));const collapse=aiRows.length>=2&&rates.some((a,i)=>rates.some((b,j)=>j>i&&Math.abs(a-b)<=0.01));return `<div style="padding:0 16px 10px"><div style="color:var(--accent);font-size:var(--t-sm);font-weight:800;margin-bottom:6px">Selection Calibration ${collapse?'<span style="color:var(--warn);font-size:var(--t-xs)">⚠️ AI tier collapse</span>':''}</div><div style="font-size:var(--t-xs);color:var(--push);margin:-1px 0 7px">VALIDATED is the deterministic market model. SMASH / STRONG / LEAN are Gemini confidence labels.</div>${tiers.map(t=>{const r=getMetricsForSlice(rows,'confidence_norm',t,w);if(!r)return '';const rate=statNum(r,'HIT_RATE');const color=t==='VALIDATED'?'var(--over)':t==='SMASH'?'var(--smash)':t==='STRONG'?'var(--warn)':'var(--push)';return `<div class="card" style="margin-bottom:6px"><div style="display:flex;justify-content:space-between;gap:10px"><div><span style="background:${color}22;color:${color};border:1px solid ${color}55;border-radius:999px;padding:2px 7px;font-size:var(--t-xs);font-weight:800">${t}</span><div style="font-size:var(--t-xs);color:var(--push);margin-top:5px">n=${Math.round(statNum(r,'N_PICKS_DECISIVE'))} · ROI ${statRoiSummary(r)}</div></div><div style="font-size:var(--t-lg);font-weight:900;color:${color}">${statPct(rate)}</div></div>${hitBar(rate)}</div>`}).join('')}</div>`}
function renderLeanBreakdown(rows,w){const over=getMetricsForSlice(rows,'lean_norm','OVER',w),under=getMetricsForSlice(rows,'lean_norm','UNDER',w);if(!over&&!under)return '';let call='';if(over&&under&&statBool(over,'MIN_SAMPLE_FLAG')&&statBool(under,'MIN_SAMPLE_FLAG')){const diff=statNum(under,'HIT_RATE')-statNum(over,'HIT_RATE');if(Math.abs(diff)>=0.05)call=`<div class="card" style="border-color:#60a5fa55;margin-bottom:6px;color:#bfdbfe;font-size:var(--t-xs)">💡 ${diff>0?'UNDERs':'OVERs'} outperforming by ${Math.abs(diff*100).toFixed(1)}pp — consider review.</div>`}return `<div style="padding:0 16px 10px"><div style="color:var(--accent);font-size:var(--t-sm);font-weight:800;margin-bottom:6px">Lean Breakdown</div>${call}${['OVER','UNDER'].map(v=>{const r=v==='OVER'?over:under;if(!r)return '';return `<div class="card" style="margin-bottom:6px"><div style="display:flex;justify-content:space-between"><div style="font-weight:800;color:var(--ink-1)">${v}<div style="font-size:var(--t-xs);color:var(--push)">n=${Math.round(statNum(r,'N_PICKS_DECISIVE'))} · ROI ${statRoiSummary(r)}</div></div><div style="font-size:var(--t-lg);font-weight:900;color:${statNum(r,'HIT_RATE')>=STATS_BREAK_EVEN?'var(--over)':'var(--under)'}">${statPct(statNum(r,'HIT_RATE'))}</div></div></div>`}).join('')}</div>`}
function renderCLVSummary(rows,w){const pos=getMetricsForSlice(rows,'clv_bucket','positive',w),neg=getMetricsForSlice(rows,'clv_bucket','negative',w);if(!pos&&!neg)return '';const cell=(label,r)=>`<div class="card"><div style="font-size:var(--t-xs);color:var(--push);text-transform:uppercase">${label}</div><div style="font-size:var(--t-lg);font-weight:900;color:${label.includes('Positive')?'var(--over)':'var(--under)'}">${r?statPct(statNum(r,'HIT_RATE')):'—'}</div><div style="font-size:var(--t-xs);color:var(--ink-1)">n=${r?Math.round(statNum(r,'N_PICKS_DECISIVE')):0}</div></div>`;return `<div style="padding:0 16px 10px"><div style="color:var(--accent);font-size:var(--t-sm);font-weight:800;margin-bottom:6px">CLV Summary</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">${cell('Positive CLV',pos)}${cell('Negative CLV',neg)}</div></div>`}
function renderPropTypeList(rows,w,ranking='best',limit=5){const arr=statsRowsForWindow(rows,w).filter(r=>statField(r,'DIMENSION_TYPE')==='prop_type_norm'&&statBool(r,'MIN_SAMPLE_FLAG')).sort((a,b)=>ranking==='best'?statNum(b,'WILSON_LOWER_95')-statNum(a,'WILSON_LOWER_95'):statNum(a,'WILSON_LOWER_95')-statNum(b,'WILSON_LOWER_95')).slice(0,limit);if(!arr.length)return '';const good=ranking==='best';return `<div style="padding:0 16px 10px"><div style="color:${good?'var(--over)':'var(--under)'};font-size:var(--t-sm);font-weight:800;margin-bottom:6px">${good?'Top':'Worst'} Prop Types</div><div class="card" style="padding:0;overflow:hidden"><table style="width:100%;border-collapse:collapse;font-size:var(--t-xs)"><thead><tr style="color:var(--push)"><th style="text-align:left;padding:8px">PROP</th><th>HIT</th><th>n</th><th>ROI/p</th><th>WLB</th></tr></thead><tbody>${arr.map(r=>`<tr style="border-top:1px solid #26313a"><td style="padding:8px;font-weight:800;color:var(--ink-1)">${esc(statField(r,'DIMENSION_VALUE'))}</td><td style="text-align:center;color:${statNum(r,'HIT_RATE')>=STATS_BREAK_EVEN?'var(--over)':'var(--under)'};font-weight:800">${statPct0(statNum(r,'HIT_RATE'))}</td><td style="text-align:center">${Math.round(statNum(r,'N_PICKS_DECISIVE'))}</td><td style="text-align:center">${statSigned(statNum(r,'ROI_PER_PICK'))}</td><td style="text-align:center">${statNum(r,'WILSON_LOWER_95').toFixed(3)}</td></tr>`).join('')}</tbody></table></div></div>`}

const MULTI_BOOK_ACCENT = "var(--accent)";
function mbField(row,name){if(!row)return "";return row[name]??row[name.toLowerCase()]??row[name.toUpperCase()]??""}
function mbBool(v){const s=String(v??"").trim().toUpperCase();return s==="TRUE"||s==="YES"||s==="1"}
function mbMetric(m){return typeof normalizePropMetric==="function"?normalizePropMetric(m):(typeof normalizePropName==="function"?normalizePropName(m):String(m||"").trim().toUpperCase())}
function formatBookName(bookKey){const k=String(bookKey||"").trim().toLowerCase();return {draftkings:"DK",fanduel:"FD",betmgm:"BetMGM",espnbet:"ESPN BET",caesars:"Caesars"}[k]||String(bookKey||"").trim()}
function findPropForPick(player,metric,line){const pn=normalizePlayerName(player),mn=mbMetric(metric),lineText=String(line??"").trim();const props=st.props||[];return props.find(p=>normalizePlayerName(p.PLAYER_NAME)===pn&&mbMetric(p.METRIC)===mn&&(lineText===""||String(p.DK_LINE??"").trim()===lineText))||props.find(p=>normalizePlayerName(p.PLAYER_NAME)===pn&&mbMetric(p.METRIC)===mn)||null}
function getBestBookForLean(prop,lean){if(!prop)return null;const side=String(lean||"OVER").toUpperCase()==="UNDER"?"UNDER":"OVER";const book=mbField(prop,`BEST_${side}_BOOK`);const odds=mbField(prop,`BEST_${side}_ODDS`);if(!book||odds==="")return null;const deltaRaw=mbField(prop,`BEST_${side}_DELTA_PP`);const delta=Number(deltaRaw);return {side,book:String(book),odds,delta:Number.isFinite(delta)?delta:null,isDK:String(book).toLowerCase()==="draftkings"}}
function renderBestBookPill(prop,lean){const b=getBestBookForLean(prop,lean);if(!b)return "";const book=formatBookName(b.book);const oddsText=typeof fmtOdds==="function"?fmtOdds(b.odds):String(b.odds);const showDelta=b.delta!==null&&Math.abs(b.delta)>0.05&&!b.isDK;const deltaText=showDelta?` <b>${b.delta>0?"+":""}${b.delta.toFixed(1)}pp</b>`:"";const star=showDelta&&b.delta>=3?" ⭐":"";const bg=b.isDK?"rgba(148,163,184,.12)":`${MULTI_BOOK_ACCENT}24`;const border=b.isDK?"rgba(148,163,184,.25)":`${MULTI_BOOK_ACCENT}88`;const color=b.isDK?"var(--push)":MULTI_BOOK_ACCENT;return `<span class="best-book-pill" title="Best ${b.side}: ${book} ${oddsText}${showDelta?` (${b.delta.toFixed(1)}pp cheaper than reference)`:""}" style="display:inline-flex;align-items:center;gap:4px;border:1px solid ${border};background:${bg};color:${color};border-radius:999px;padding:2px 7px;font-size:var(--t-xs);font-weight:800;white-space:nowrap">${b.side[0]} ${book} ${oddsText}${deltaText}${star}</span>`}
function renderAltLineFlag(prop){if(!mbBool(mbField(prop,'ALT_LINE_AVAILABLE')))return "";const books=mbField(prop,'ALT_LINE_BOOKS')||"available";return `<span class="alt-line-flag" title="Alt lines: ${esc(String(books))}" style="display:inline-flex;align-items:center;border:1px solid color-mix(in srgb, var(--warn) 40%, transparent);background:color-mix(in srgb, var(--warn) 10%, transparent);color:var(--warn);border-radius:999px;padding:2px 7px;font-size:var(--t-xs);font-weight:800;white-space:nowrap">🔀 alt</span>`}
function renderReferenceFootnote(prop){const ref=mbField(prop,'REFERENCE_BOOK');if(!ref||String(ref).toLowerCase()==='draftkings')return "";return `<span style="font-size:var(--t-xs);color:var(--warn)">DK n/a — using ${formatBookName(ref)} as reference</span>`}
function softLinePropKey(prop){return `${normalizePlayerName(mbField(prop,'PLAYER_NAME'))}|${mbMetric(mbField(prop,'METRIC'))}|${String(mbField(prop,'DK_LINE')).trim()}`}
function softLineAllBooksByKey(){return getMemo('softLineAllBooks',()=>{const map=new Map();(st.allBooksProps||[]).forEach(r=>{const key=`${normalizePlayerName(mbField(r,'PLAYER_NAME'))}|${mbMetric(mbField(r,'METRIC'))}`;if(!map.has(key))map.set(key,[]);map.get(key).push(r)});return map})}
function detectSoftLine(dkOdds,otherRows,side){const dkImplied=impliedProb(dkOdds);if(dkImplied===null)return null;const rows=(otherRows||[]).map(r=>({book:String(mbField(r,'BOOK')).toLowerCase(),odds:mbField(r,`${side}_ODDS`)})).filter(r=>r.odds!==''&&impliedProb(r.odds)!==null);if(rows.length<SOFT_LINE_MIN_BOOKS)return null;const implieds=rows.map(r=>impliedProb(r.odds));const median=computeMedian(implieds);const consensusOdds=impliedToAmerican(median);if(median===null||consensusOdds===null)return null;const ppSpread=(median-dkImplied)*100;const direction=Math.sign(ppSpread);if(direction<=0)return null;const centsSpread=americanCentsDiff(dkOdds,consensusOdds);const sameDirectionCount=rows.filter(r=>Math.sign(impliedProb(r.odds)-dkImplied)===direction).length;const flagged=Math.abs(centsSpread||0)>=SOFT_LINE_CENTS_THRESHOLD&&ppSpread>=SOFT_LINE_PP_THRESHOLD&&sameDirectionCount>=SOFT_LINE_MIN_AGREEMENT;return {side,flagged,dkOdds,dkImplied,consensusOdds,consensusImplied:median,ppSpread,centsSpread,sameDirectionCount,totalOtherBooks:rows.length,books:rows.map(r=>({...r,implied:impliedProb(r.odds)}))}}
function evaluateSoftLineForProp(prop){if(!prop)return null;const book=String(mbField(prop,'BOOK')||'draftkings').toLowerCase();const ref=String(mbField(prop,'REFERENCE_BOOK')||'draftkings').toLowerCase();if(book&&book!=='draftkings')return null;if(ref&&ref!=='draftkings')return null;const baseKey=`${normalizePlayerName(mbField(prop,'PLAYER_NAME'))}|${mbMetric(mbField(prop,'METRIC'))}`;const line=String(mbField(prop,'DK_LINE')).trim();let rows=(softLineAllBooksByKey().get(baseKey)||[]).filter(r=>SOFT_LINE_BOOKS.includes(String(mbField(r,'BOOK')).toLowerCase())&&impliedProb(mbField(r,'OVER_ODDS'))!==null&&impliedProb(mbField(r,'UNDER_ODDS'))!==null);const sameLine=rows.filter(r=>String(mbField(r,'LINE')).trim()===line);if(sameLine.length>=SOFT_LINE_MIN_BOOKS)rows=sameLine;const over=detectSoftLine(mbField(prop,'OVER_ODDS'),rows,'OVER');const under=detectSoftLine(mbField(prop,'UNDER_ODDS'),rows,'UNDER');if(!over&&!under)return null;return {key:softLinePropKey(prop),over:over&&over.flagged?over:null,under:under&&under.flagged?under:null}}
function renderSoftLineTooltip(result){if(!result)return "";const sides=[result.over,result.under].filter(Boolean);if(!sides.length)return "";return `<div onclick="event.stopPropagation()" style="position:relative;flex-basis:100%;max-width:420px;margin-top:6px;background:var(--ink-0);border:1px solid color-mix(in srgb, var(--warn) 40%, transparent);border-radius:8px;padding:9px;color:var(--ink-1);box-shadow:0 8px 24px #0008;z-index:20">${sides.map(r=>`<div style="margin-bottom:${sides.length>1?'10px':'0'}"><div style="color:var(--warn);font-size:var(--t-xs);font-weight:900;margin-bottom:6px">🚨 Soft DK line — ${r.side}</div><div style="display:grid;grid-template-columns:auto 1fr;gap:3px 10px;font-size:var(--t-xs)"><span style="color:var(--push)">DK:</span><span>${fmtOdds(r.dkOdds)} (${(r.dkImplied*100).toFixed(1)}%)</span><span style="color:var(--push)">Consensus:</span><span>${fmtOdds(r.consensusOdds)} (${(r.consensusImplied*100).toFixed(1)}%)</span><span style="color:var(--push)">Spread:</span><span>+${Math.round(r.centsSpread)} cents | ${r.ppSpread>0?'+':''}${r.ppSpread.toFixed(1)}pp</span></div><div style="font-size:var(--t-xs);color:var(--ink-1);margin-top:6px">${r.sameDirectionCount} of ${r.totalOtherBooks} other books agree DK is too low.</div><div style="font-size:var(--t-xs);color:var(--push);margin-top:6px">${r.books.map(b=>`${formatBookName(b.book)}: ${fmtOdds(b.odds)} (${(b.implied*100).toFixed(1)}%)`).join(' · ')}</div></div>`).join('')}</div>`}
function renderSoftLinePill(prop){const result=evaluateSoftLineForProp(prop);if(!result||(!result.over&&!result.under))return "";const side=result.over&&result.under?'BOTH':result.over?'OVER':'UNDER';const open=window.__softLineOpen===result.key;return `<span onclick="event.stopPropagation();window.__softLineOpen=${open?'null':JSON.stringify(result.key)};render()" class="soft-line-pill" title="Tap for soft DK math" style="display:inline-flex;align-items:center;border:1px solid color-mix(in srgb, var(--warn) 47%, transparent);background:var(--warn-soft);color:var(--warn);border-radius:999px;padding:2px 7px;font-size:var(--t-xs);font-weight:900;white-space:nowrap;cursor:pointer">🚨 Soft DK (${side})</span>${open?renderSoftLineTooltip(result):""}`}
function renderPropBestBookBlock(prop){if(!prop)return "";const over=renderBestBookPill(prop,'OVER'),under=renderBestBookPill(prop,'UNDER'),alt=renderAltLineFlag(prop),soft=renderSoftLinePill(prop),ref=renderReferenceFootnote(prop);const top=[over,under,alt,soft].filter(Boolean).join(" ");if(!top&&!ref)return "";return `<div class="best-book-block" style="display:flex;flex-wrap:wrap;gap:5px;margin-top:6px;align-items:center">${top}${ref?`<div style="flex-basis:100%">${ref}</div>`:""}</div>`}
function renderPropBestBookTableRow(prop,colspan=7,{collapsed=false}={}){
  const block=renderPropBestBookBlock(prop);
  if(!block)return"";
  const content=collapsed?`<details class="props-book-details" onclick="event.stopPropagation()"><summary>Book details</summary>${block}</details>`:block;
  return`<tr class="best-book-row"><td colspan="${colspan}" style="text-align:left;padding:0 8px 8px;border-top:0">${content}</td></tr>`;
}
function renderBestBookLine(prop,lean){const b=getBestBookForLean(prop,lean);if(!b)return "";const book=formatBookName(b.book);const oddsText=typeof fmtOdds==="function"?fmtOdds(b.odds):String(b.odds);const delta=b.delta!==null&&!b.isDK&&Math.abs(b.delta)>0.05?` <span style="font-weight:800">(${b.delta>0?"+":""}${b.delta.toFixed(1)}pp vs DK${b.delta>=3?" · edge":""})</span>`:"";const color=b.isDK?"var(--push)":MULTI_BOOK_ACCENT;return `<div class="best-book-line" style="margin-top:5px;font-size:var(--t-xs);color:${color};font-weight:700">Best: ${book} @ ${oddsText}${delta}</div>`}
function pickLogMetric(metric){return {P_SO:"SO",P_ER:"ER",P_BB:"BB",P_H:"H"}[String(metric||"").toUpperCase()]||String(metric||"").toUpperCase()}
function getPickRecentForm(pk){
  const isP=String(pk.prop_type||"").startsWith("P_");
  const field=pickLogMetric(pk.prop_type),line=Number(pk.line),lean=normalizeLeanText(pk.lean);
  const values=getPlayerLogs(pk.player,isP).slice(0,10).reverse().map(g=>toNum(rowField(g,field)));
  const decisive=values.filter(v=>Number.isFinite(v)&&Number.isFinite(line)&&v!==line);
  const hits=decisive.filter(v=>lean==="UNDER"?v<line:v>line).length;
  const avg=values.length?values.reduce((s,v)=>s+v,0)/values.length:null;
  return{values,line,lean,hits,decisive:decisive.length,avg};
}
function renderPickFormBars(form){
  if(!form.values.length)return `<span class="pick-form-empty">No L10</span>`;
  const max=Math.max(1,form.line||0,...form.values);
  return form.values.map(v=>{const hit=Number.isFinite(form.line)&&(form.lean==="UNDER"?v<form.line:v>form.line);const push=Number.isFinite(form.line)&&v===form.line;const height=Math.max(3,Math.round((v/max)*25));return `<span class="pick-form-bar ${push?"":hit?"hit":"miss"}" style="height:${height}px" title="${v}"></span>`}).join("");
}
function pickEvidenceHTML(model){
  const bits=[];
  if(model.form.decisive)bits.push(`<span><strong>L10 ${model.form.hits}/${model.form.decisive}</strong> hit</span>`);
  if(model.form.avg!==null)bits.push(`<span>avg <strong>${model.form.avg.toFixed(1)}</strong></span>`);
  const book=getBestBookForLean(model.pickProp,model.leanText);
  if(book&&book.delta!==null&&!book.isDK&&Math.abs(book.delta)>0.05)bits.push(`<span><strong>${book.delta>0?"+":""}${book.delta.toFixed(1)}pp</strong> book edge</span>`);
  if(model.flags.returning)bits.push(`<span>returning</span>`);
  if(model.flags.limited)bits.push(`<span>limited sample</span>`);
  return bits.join("");
}
function getPickProvenance(pk){
  const method=String(rowField(pk,"SELECTION_METHOD")||"").trim().toUpperCase();
  const status=String(rowField(pk,"RECOMMENDATION_STATUS")||"").trim().toUpperCase();
  const consensusCount=Math.max(0,toNum(rowField(pk,"CONSENSUS_COUNT")));
  const validated=method.includes("VALIDATED");
  return{
    label:status==="RESEARCH"?"Research only":validated?"Validated model":"AI reviewed",
    className:status==="RESEARCH"?"research":validated?"validated":"ai",
    consensusCount,
    description:status==="RESEARCH"
      ?"Tracked for grading; not promoted as an actionable recommendation."
      :validated
        ?"Selected by the deterministic market and form model."
        :"Selected by Gemini, then checked against real players, markets, and lines."
  };
}
function pickProvenanceHTML(model){
  const source=model.provenance;
  return `<div class="pick-provenance"><span class="pick-source-badge ${source.className}" title="${esc(source.description)}">${esc(source.label)}</span>${source.consensusCount>=2?`<span class="pick-consensus-badge" title="Appeared across repeated engine runs">Run consensus · ${source.consensusCount}</span>`:""}</div>`;
}
function pickWhyHTML(model){
  const reason=String(rowField(model.pk,"rationale","reasoning")||"").trim();
  const score=Number(rowField(model.pk,"CALIBRATION_SCORE"));
  const scoreText=Number.isFinite(score)?` · calibration ${score.toFixed(2)}`:"";
  return `<div class="pick-why"><strong>Why it ranks:</strong> ${esc(reason||model.provenance.description)}${esc(scoreText)}</div>`;
}
function getPickDisplayModel(pk){
  const confidence=normalizeConfidence(pk.confidence),tierClass=confidence==="SMASH"?"smash":confidence==="STRONG"?"strong":"lean";
  const leanText=normalizeLeanText(pk.lean),leanClass=leanText==="UNDER"?"under":"over";
  const isPitch=String(pk.prop_type||"").startsWith("P_");
  const flags=getSampleFlags(pk.player,isPitch),locked=getLockInfo(pk.player,isPitch).started;
  const hit=String(rowField(pk,"HIT")).toUpperCase(),actual=rowField(pk,"ACTUAL_STAT");
  const hasActual=actual!=null&&actual!==""&&!isNaN(actual),pending=!!hit&&!["YES","TRUE","NO","FALSE"].includes(hit)&&!hasActual;
  const result=hit==="YES"||hit==="TRUE"?"HIT":hit==="NO"||hit==="FALSE"?"MISS":hasActual?"PUSH":"";
  const injury=String(pk.injury_context||""),lineupRisk=injury.toUpperCase().startsWith("LINEUP RISK");
  const pickProp=findPropForPick(pk.player,pk.prop_type,pk.line);
  const model={pk,confidence,tierClass,leanText,leanClass,isPitch,flags,locked,actual,hasActual,pending,result,injury,lineupRisk,pickProp,provenance:getPickProvenance(pk)};
  model.form=getPickRecentForm(pk);
  return model;
}
function pickStatusLine(model){
  const states=[];
  if(model.locked)states.push("LOCKED");
  if(model.flags.returning)states.push("RETURNING");
  if(model.flags.limited)states.push("LIMITED SAMPLE");
  if(model.pending)states.push("PENDING");
  if(model.result)states.push(model.result+(model.hasActual?` ${model.actual}`:""));
  if(model.lineupRisk)states.push("LINEUP RISK");
  return states.join(" · ");
}
function pickClick(model){return `streakToDash(${[model.pk.player,model.pk.prop_type||"",model.pk.line||""].map(v=>esc(JSON.stringify(String(v)))).join(",")})`}
function renderFeaturedPick(model){
  const p=model.pk,status=pickStatusLine(model),evidence=pickEvidenceHTML(model),gameTime=gameStartTimeForText(p.game);
  return `<section class="pick-feature ${model.tierClass}${model.locked?" locked-card":""}" onclick="${pickClick(model)}"><div class="pick-feature-kicker"><span>${icon("picks")}Top recommendation</span><span style="color:var(--${model.tierClass==="smash"?"smash":model.tierClass==="strong"?"strong":"push"})">${model.confidence}</span></div><div class="pick-feature-main"><div><div class="pick-feature-name">${playerLink(p.player,p.prop_type||"",p.line||"")}</div><div class="pick-feature-matchup">${esc(p.game||"")}${gameTime?` · ${esc(gameTime)}`:""} · vs ${esc(p.opp_pitcher||"TBD")} · ${esc(p.venue||"")}</div>${pickProvenanceHTML(model)}</div><div class="pick-feature-call"><div class="pick-feature-line ${model.leanClass}">${esc(model.leanText)} ${esc(p.line||"—")}</div><div class="pick-feature-market">${esc(propTypeLabel(p.prop_type))}</div></div></div><div class="pick-feature-evidence"><div><div class="pick-evidence">${evidence||"Model-ranked slate leader"}</div>${renderBestBookLine(model.pickProp,model.leanText)}${pickWhyHTML(model)}</div><div class="pick-board-form" aria-label="Last ten results">${renderPickFormBars(model.form)}</div></div>${status?`<div class="pick-board-status" style="grid-column:auto;margin-top:8px">${esc(status)}</div>`:""}${model.lineupRisk?`<div class="lineup-risk-text">${esc(model.injury)}</div>`:""}</section>`;
}
function renderPickBoardRow(model,index){
  const p=model.pk,status=pickStatusLine(model),evidence=pickEvidenceHTML(model),gameTime=gameStartTimeForText(p.game);
  return `<div class="pick-board-row${model.locked?" locked-card":""}" onclick="${pickClick(model)}"><div class="pick-board-rank">${String(p.rank||index+2).padStart(2,"0")}</div><div class="pick-board-player"><div class="pick-board-name">${playerLink(p.player,p.prop_type||"",p.line||"")}</div><div class="pick-board-meta">${esc(p.game||"")}${gameTime?` · ${esc(gameTime)}`:""} · ${esc(propTypeLabel(p.prop_type))}</div>${pickProvenanceHTML(model)}</div><div class="pick-board-form" aria-label="Last ten results">${renderPickFormBars(model.form)}</div><div class="pick-evidence">${evidence||"No recent sample"}</div><div class="pick-board-decision"><div class="pick-board-call ${model.leanClass}">${esc(model.leanText)} ${esc(p.line||"—")}</div><div class="pick-board-market">${esc(propTypeLabel(p.prop_type))}</div><div class="pick-board-tier ${model.tierClass}">${model.confidence}</div></div><div class="pick-board-rationale">${pickWhyHTML(model)}</div>${status?`<div class="pick-board-status">${esc(status)}</div>`:""}</div>`;
}
function bestBookKeyForLean(prop,lean){const b=getBestBookForLean(prop,lean);return b?formatBookName(b.book):""}
function renderCrossBookWarning(legs){const books=[...new Set((legs||[]).map(l=>bestBookKeyForLean(l.prop,l.lean)).filter(Boolean))];return books.length>=2?`<div class="cross-book-warning" style="margin-top:6px;font-size:var(--t-xs);color:var(--warn);background:color-mix(in srgb, var(--warn) 8%, transparent);border:1px solid var(--warn-line);border-radius:6px;padding:6px">${icon('warn')}Best book differs across legs (${books.join(", ")}). Single-book parlay may not match leg-by-leg EV.</div>`:""}

function renderLeadersView(){
  const live=st.leaderMode==="live";
  const refreshed=st.loadedAt||"this page load";
  const status=live
    ?`Today so far · Engine snapshot refreshed ${refreshed} · Not continuously live`
    :`Finalized MLB game-log snapshot · Dashboard refreshed ${refreshed}`;
  return `${renderDailyLeaders()}<div class="timestamp">${esc(status)} · Click any player to open analysis</div>`;
}
function renderStatsView(){const w=st.statsTimeWindow||'last_30d';const rows=typeof getMemo==='function'?getMemo('statsRows:'+w,()=>st.pickPerformance||[]):(st.pickPerformance||[]);let html=renderTimeWindowSelector(w);if(!rows.length)return html+`<div class="empty" style="padding:40px 20px;text-align:center">Pick Performance unavailable — grading analytics will appear after the next grader run.</div>`;if(!statsRowsForWindow(rows,w).length)return html+`<div class="empty" style="padding:40px 20px;text-align:center">No Pick Performance rows for ${statsWindowLabel(w)}.</div>`;const updated=rows.map(r=>statField(r,'LAST_UPDATED')).filter(Boolean).sort().pop()||'';html+=renderDriftAlerts(rows);html+=renderOverallCard(rows,w);html+=renderEraCohortAudit(rows,w);html+=renderPriceDiscipline(rows);html+=renderTierBreakdown(rows,w);html+=renderLeanBreakdown(rows,w);html+=renderCLVSummary(rows,w);html+=renderPropTypeList(rows,w,'best');html+=renderPropTypeList(rows,w,'worst');html+=`<div class="timestamp">Data through ${esc(updated||'latest grader run')} · Updated daily after grader run</div>`;return html}

function renderShortlistPicksView(){
  return renderTonightShortlist();
}

function renderModelPicksView(convergenceHTML){
  const latestDate=getLatestPickDate();
  const latestRun=getLatestPickRun();
  const allTodayPicks=latestDate
    ?st.picks.filter(p=>normalizeDate(rowField(p,"DATE"))===latestDate&&toNum(rowField(p,"RUN_NUMBER"))===latestRun)
    :st.picks;
  const hasCalibrationStatus=allTodayPicks.some(p=>String(rowField(p,"RECOMMENDATION_STATUS")||"").trim());
  const todayPicks=hasCalibrationStatus
    ?allTodayPicks.filter(p=>String(rowField(p,"RECOMMENDATION_STATUS")).toUpperCase()==="PLAYABLE")
    :allTodayPicks;
  const researchCount=hasCalibrationStatus?allTodayPicks.length-todayPicks.length:0;
  const modelIntro=`<section class="model-picks-intro"><div class="model-picks-title">Model Picks</div><div class="model-picks-sub">Ranked recommendations from the deterministic market model and Gemini review layer. Provenance, evidence, and source freshness stay visible so every call can be audited.</div>${renderModelRunHealth(allTodayPicks)}${renderModelFreshness()}</section>`;
  let html=convergenceHTML+modelIntro+renderPickGuard(st.pickGuard);

  if(!todayPicks.length){
    const emptyMessage=hasCalibrationStatus
      ?`No calibrated play qualifies today. ${researchCount} research pick${researchCount===1?"":"s"} remain tracked for model learning.`
      :"No model picks today. Run the engine to generate.";
    return html+`<div class="empty" style="padding:40px">${emptyMessage}</div>`;
  }

  const hits=todayPicks.filter(p=>{
    const result=String(rowField(p,"HIT")).toUpperCase();
    return result==="YES"||result==="TRUE";
  }).length;
  const misses=todayPicks.filter(p=>{
    const result=String(rowField(p,"HIT")).toUpperCase();
    return result==="NO"||result==="FALSE";
  }).length;
  if(hits+misses){
    html+=`<div style="display:flex;justify-content:flex-end;padding:0 16px 9px"><span class="pick-source-badge ${hits>=misses?"validated":"research"}">Current record ${hits}-${misses}</span></div>`;
  }

  const rankedPicks=[...todayPicks].sort((a,b)=>toNum(a.rank||999)-toNum(b.rank||999));
  const pickModels=rankedPicks.map(getPickDisplayModel);
  const featured=pickModels[0];
  const remaining=pickModels.slice(1);
  const board=remaining.length
    ?`<div class="pick-board"><div class="pick-board-head"><span>#</span><span>Player / matchup</span><span>L10</span><span>Evidence</span><span style="text-align:right">Decision</span></div>${remaining.map((model,index)=>renderPickBoardRow(model,index)).join("")}</div>`
    :"";
  return html+`<div class="pick-editorial">${featured?renderFeaturedPick(featured):""}${board}</div>`;
}

function renderDingerBoardView(convergenceHTML){
  const db=getDingerBoard();
  if(!db.length){
    const missing=[];
    if(!st.tonight.length)missing.push("this week's skill players");
    if(!st.gameLogs.length)missing.push("batter game logs");
    const detail=missing.length
      ?`Google Sheets did not return ${missing.join(" or ")} on this page load.`
      :"No eligible players had usable snaps and game-log history.";
    return convergenceHTML+`<div class="empty" style="padding:40px;text-align:center"><div style="font-weight:800;color:var(--ink-1)">Dinger Board unavailable</div><div style="margin-top:6px">${detail}</div><button class="refresh-btn" style="margin-top:12px" onclick="loadAllData()">${icon("refresh")}Retry data load</button></div>`;
  }
  let html=convergenceHTML+`<div class="dinger-header"><div class="dinger-title">This Week's TD Board</div></div>
  <div class="dinger-desc">Ranked by red-zone usage, recent form, opposing-starter quality, and sportsbook price. Top 3 are 🔥.</div>`;
  html+=`<div class="cards-grid">`;
  html+=db.map((d,i)=>{
    const isTop=i<3;
    const odds=d.overOdds?fmtOdds(d.overOdds):"—";
    const ratePct=(d.hrRate*100).toFixed(1);
    const abPerHR=d.seasHR>0?Math.round(d.totalAB/d.seasHR):"—";
    const matchupAdjustment=d.modelOpponentAdjustment;
    const matchupGrade=matchupAdjustment===null
      ?null
      :matchupAdjustment>=2
        ?{label:"Favorable defensive matchup",color:"var(--over)"}
        :matchupAdjustment<=-2
          ?{label:"Tough defensive matchup",color:"var(--under)"}
          :{label:"Neutral defensive matchup",color:"var(--ink-muted)"};
    const opponentRanking=getTeamRanking(d.opp);
    const teamContext=opponentRanking?`${esc(d.opp)} staff · ${teamRankValue(opponentRanking,"PIT_HR9","PIT_HR9_MOST_RANK",{digits:2,suffix:" HR/9",direction:"most"})}`:"";
    const locked=getLockInfo(d.name,false).started;
    return`<div class="dinger-card ${isTop?"top3":""}${locked?" locked-card":""}" style="cursor:pointer" onclick="streakToDash('${esc(d.name)}','HR','${d.dkLine||""}')">
      <div class="dinger-left">
        <div><span class="dinger-rank">${i+1}</span><span class="dinger-name">${playerLink(d.name,"HR",d.dkLine||"")}${lockBadge(d.name,false)}</span></div>
        <div class="dinger-meta">${esc(d.team)} vs ${esc(d.pitcher)} (${d.hand}HP) · ${esc(d.venue)}</div>
        <div class="dinger-meta">${d.seasHR} HR in ${d.gamesPlayed} G · L7 avg: ${d.l7HR.toFixed(2)} · L14: ${d.l14HR.toFixed(2)}</div>
        ${teamContext?`<div class="dinger-meta" style="color:var(--accent)">${teamContext}</div>`:""}
        ${matchupGrade?`<div class="dinger-meta" style="color:${matchupGrade.color}">${matchupGrade.label} · opponent adjustment ${matchupAdjustment>0?"+":""}${matchupAdjustment.toFixed(1)}</div>`:""}
      </div>
      <div class="dinger-right">
        <div class="dinger-rate">${ratePct}%</div>
        <div class="dinger-sub">${locked?"started":"HR/AB · 1 per "+abPerHR+" AB"}</div>
        ${d.dkLine!==null?`<div class="dinger-odds">DK ${d.dkLine} O:${odds}</div>`:""}
      </div>
    </div>`;
  }).join("");
  html+=`</div>`;
  html+=renderMarketParlays("HR","Dinger");
  return html;
}

function renderKsBoardView(convergenceHTML){
  const kb=getKsBoard();
  if(!kb.length){
    return convergenceHTML+`<div class="empty" style="padding:40px">No Ks data available. Run the engine first.</div>`;
  }
  let html=convergenceHTML+`<div class="dinger-header"><div class="dinger-title">This Week's Passing Board</div></div>
  <div class="dinger-desc">Projected Ks blend season, L7, and L3 form, then adjust for the opponent's pass defense. Sportsbook price breaks close calls.</div>`;
  html+=`<div class="cards-grid">`;
  html+=kb.map((d,i)=>{
    const isTop=i<3;
    const odds=d.overOdds?fmtOdds(d.overOdds):"—";
    const k9Str=d.k9.toFixed(1);
    const projectionStr=d.adjustedProjection.toFixed(1);
    const adjustmentText=`${d.projectionAdjustment>0?"+":""}${d.projectionAdjustment.toFixed(1)} K`;
    const matchupGrade=d.projectionAdjustment<=-0.35
      ?{label:"Tough matchup",color:"var(--under)"}
      :d.projectionAdjustment>=0.35
        ?{label:"Favorable matchup",color:"var(--over)"}
        :{label:"Neutral matchup",color:"var(--ink-muted)"};
    const opponentRanking=getTeamRanking(d.opp);
    const teamContext=opponentRanking?`${esc(d.opp)} offense · ${teamRankValue(opponentRanking,"OFF_K_PCT","OFF_K_PCT_MOST_RANK",{digits:1,suffix:"% K",direction:"most"})}`:"";
    const locked=getLockInfo(d.name,true).started;
    return`<div class="dinger-card ${isTop?"top3":""}${locked?" locked-card":""}" style="cursor:pointer" onclick="streakToDash('${esc(d.name)}','P_SO','${d.dkLine||""}')">
      <div class="dinger-left">
        <div><span class="dinger-rank">${i+1}</span><span class="dinger-name">${playerLink(d.name,"P_SO",d.dkLine||"")}${lockBadge(d.name,true)}</span></div>
        <div class="dinger-meta">${esc(d.team)} vs ${esc(d.opp)} · ${esc(d.venue)}</div>
        <div class="dinger-meta">${d.seasSO} K in ${d.gamesStarted} GS · L7 avg: ${d.l7SO.toFixed(1)} · L3: ${d.l3SO.toFixed(1)}</div>
        ${teamContext?`<div class="dinger-meta" style="color:var(--accent)">${teamContext}</div>`:""}
        <div class="dinger-meta" style="color:${matchupGrade.color}">${matchupGrade.label} · raw ${d.projectedSO.toFixed(1)} → adjusted ${projectionStr} (${adjustmentText})</div>
      </div>
      <div class="dinger-right">
        <div class="dinger-rate">${projectionStr}</div>
        <div class="dinger-sub">Matchup projection · ${k9Str} K/9</div>
        ${d.dkLine!==null?`<div class="dinger-odds">DK ${d.dkLine} O:${odds}</div>`:""}
      </div>
    </div>`;
  }).join("");
  html+=`</div>`;
  html+=renderMarketParlays("P_SO","K");
  return html;
}

function renderStreaksBoardView(convergenceHTML){
  const allStreaks=getStreaks();
  const fil=st.streakFilter==="all"?allStreaks:st.streakFilter==="bat"?allStreaks.filter(s=>s.propType==="bat"):allStreaks.filter(s=>s.propType==="pitch");
  if(!fil.length){
    return convergenceHTML+`<div class="empty" style="padding:40px">${allStreaks.length?`No ${st.streakFilter} streaks found.`:"No active streaks yet. Need 3+ games of data."}</div>`;
  }
  let html=convergenceHTML+`<div style="padding:12px 16px 4px;display:flex;justify-content:space-between;align-items:center"><div style="color:#ffaa00;font-size:var(--t-sm);font-weight:700">🔥 Active Streaks</div><div style="color:var(--ink-muted);font-size:var(--t-xs)">${fil.length} streaks found</div></div>
  <div class="streak-filters"><div class="pf-btn ${st.streakFilter==="all"?"active":""}" onclick="setStreakFilter('all')">All</div><div class="pf-btn ${st.streakFilter==="bat"?"active":""}" onclick="setStreakFilter('bat')">${icon('bat')} Skill</div><div class="pf-btn ${st.streakFilter==="pitch"?"active":""}" onclick="setStreakFilter('pitch')">${icon('ball')} QB</div></div>`;
  html+=`<div class="cards-grid">`;
  html+=fil.map(s=>{
    const heat=getStreakHeat(s.streak);
    const odds=s.overOdds?fmtOdds(s.overOdds):"";
    const locked=getLockInfo(s.player,s.propType==="pitch").started;
    return`<div class="streak-card ${heat.cls}${locked?" locked-card":""}" onclick="streakToDash('${esc(s.player)}')">
      <div class="streak-left">
        <div><span class="streak-emoji">${s.emoji}</span><span class="streak-name">${playerLink(s.player,s.stat,s.dkLine||"")}${lockBadge(s.player,s.propType==="pitch")}</span><span class="streak-label">${s.label}</span></div>
        <div class="streak-meta">${esc(s.team)} vs ${s.propType==="pitch"?esc(s.opp):esc(s.pitcher)+" ("+s.hand+"HP)"} · ${s.desc}</div>
        <div class="streak-chart">${miniChart(s.recentVals,s.threshold)}</div>
        ${s.dkLine?`<div class="streak-prop">DK ${s.stat} ${s.dkLine} ${odds?" O:"+odds:""} · Avg during: ${s.avgDuring}</div>`:`<div class="streak-prop">Avg during streak: ${s.avgDuring} · Season: ${s.seasAvg}</div>`}
      </div>
      <div class="streak-right">
        <div class="streak-count">${s.streak}</div>
        <div class="streak-sub">${locked?"started":"games"}</div>
      </div>
    </div>`;
  }).join("");
  html+=`</div>`;
  return html;
}

function renderDraftBoardView(convergenceHTML){
  let html="";
      const board=getDraftBoard();
      const slateGames=getDraftSlateGames();
      const selectedGames=draftSlateSelection();
      const available=board.filter(p=>!st.drafted.has(p.name));
      const stacks=getDraftStacks().slice(0,5);
      const stackTags=getDraftStackTagMap();
      const draftedCount=st.drafted.size;
      function getTier(proj,isP){const v=parseFloat(proj);if(isP){if(v>=8)return{label:"TIER 1 — Ace",cls:"tier1",color:"var(--accent)"};if(v>=5)return{label:"TIER 2 — Solid SP",cls:"tier2",color:"var(--strong)"};return{label:"TIER 3 — Spot Start",cls:"tier3",color:"#8b5cf6"}}if(v>=12)return{label:"TIER 1 — Elite",cls:"tier1",color:"var(--accent)"};if(v>=9)return{label:"TIER 2 — Strong",cls:"tier2",color:"var(--strong)"};if(v>=6)return{label:"TIER 3 — Solid",cls:"tier3",color:"#8b5cf6"};if(v>=4)return{label:"TIER 4 — Role Player",cls:"",color:"var(--accent-soft)"};return{label:"TIER 5 — Dart Throw",cls:"",color:"var(--ink-muted)"}}
      function getPosClass(pos){if(pos==="P")return"draft-pos-p";if(pos==="IF")return"draft-pos-if";if(pos==="OF")return"draft-pos-of";return"draft-pos-flex"}
      const draftHeader=convergenceHTML+`<div style="padding:12px 16px 4px;color:var(--accent);font-size:var(--t-sm);font-weight:700">Draft Cheat Sheet</div>
        <div style="padding:0 16px 4px;color:var(--ink-muted);font-size:var(--t-xs)">Underdog scoring: 1B×3 2B×6 3B×8 HR×10 BB×3 HBP×3 RBI×2 R×2 SB×4 | P: W×5 QS×5 K×3 IP×3 ER×-3</div>
        <div style="padding:0 16px 4px;color:var(--ink-muted);font-size:var(--t-xs)">Roster: P×1 · IF×2 · OF×2 · FLEX×1 — Tap to mark as drafted.</div>
        ${renderDraftSlateSelector()}`;
      if(!board.length){
        const emptyMessage=slateGames.length&&!selectedGames.size
          ?"No contest games selected. Choose the games included in this UD contest."
          :"No draftable players loaded for the selected games.";
        html=draftHeader+`<div class="empty" style="padding:40px">${emptyMessage}</div>`;
      }
      else{
        html=draftHeader+`<div class="draft-controls"><button class="draft-reset" onclick="resetDrafted()">Reset Board</button><div class="draft-count">${draftedCount} drafted · ${available.length} available</div></div>`;
        html+=`<div class="cards-grid draft-board">`;
        let lastTier="";
        board.forEach((p,i)=>{
          const tier=getTier(p.projUD,p.isPitcher);const isDrafted=st.drafted.has(p.name);
          const tierChanged=tier.label!==lastTier;lastTier=tier.label;
          let tags=[];
          if(p.isSmash)tags.push(`<span class="draft-tag" style="background:var(--smash-soft);color:var(--smash)">SMASH</span>`);
          if(p.isPitcher){if(p.qsRate>=0.6)tags.push(`<span class="draft-tag" style="background:color-mix(in srgb, var(--strong) 13%, transparent);color:var(--strong)">QS ${(p.qsRate*100).toFixed(0)}%</span>`);if(p.sSO>=6)tags.push(`<span class="draft-tag" style="background:var(--under-soft);color:var(--under)">🔥 ${p.sSO.toFixed(1)} K/GS</span>`)}
          else{if(p.sHR>=0.3)tags.push(`<span class="draft-tag" style="background:var(--under-soft);color:var(--under)">💣 POWER</span>`);if(p.sSB>=0.3)tags.push(`<span class="draft-tag" style="background:var(--over-soft);color:var(--over)">💨 SPEED</span>`);if(p.sBB>=0.5)tags.push(`<span class="draft-tag" style="background:color-mix(in srgb, var(--strong) 13%, transparent);color:var(--strong)">👁️ PATIENT</span>`)}
          if(p.returning)tags.push(`<span class="draft-tag" style="background:var(--warn-soft);color:var(--warn)">${icon('warn')}RETURNING</span>`);
          if(p.limitedSample)tags.push(`<span class="draft-tag" style="background:var(--ink-quiet);color:var(--ink-1)">${icon('warn')}LIMITED SAMPLE</span>`);
          const l7v=parseFloat(p.l7UD),projv=parseFloat(p.projUD);
          if(l7v>projv*1.15)tags.push(`<span class="draft-tag" style="background:var(--over-soft);color:var(--over)">📈 HOT</span>`);
          if(l7v<projv*0.8&&l7v>0)tags.push(`<span class="draft-tag" style="background:var(--under-soft);color:var(--under)">📉 COLD</span>`);
          (stackTags.get(normalizePlayerName(p.name))||new Set()).forEach(tag=>{const clr=tag.includes("CORRELATED")?"#60a5fa":tag.includes("HIGH TOTAL")?"var(--warn)":"#34d399";tags.push(`<span class="draft-tag" style="background:${clr}22;color:${clr}">${tag}</span>`);});
          const metaLine=p.isPitcher?`${esc(p.team)} vs ${esc(p.opp)} · ${p.sSO.toFixed(1)}K · ${p.sIP.toFixed(1)}IP · ${p.sER.toFixed(1)}ER`:`${esc(p.team)} vs ${esc(p.pitcher)} (${p.hand}HP) · ${p.sH.toFixed(0)}h/${p.sHR.toFixed(1)}hr/${p.sRBI.toFixed(1)}rbi/${p.sR.toFixed(1)}r`;
          const locked=getLockInfo(p.name,p.isPitcher).started;
          const cardCls=`draft-card${isDrafted?" drafted":""}${p.isSmash&&!isDrafted?" smash":!isDrafted?" "+tier.cls:""}${p.isPitcher&&!isDrafted?" pitcher":""}${locked?" locked-card":""}`;
          html+=`${tierChanged?`<div class="draft-tier-label" style="color:${tier.color}">${tier.label}</div>`:""}
          <div class="${cardCls}" onclick="toggleDrafted('${esc(p.name)}')">
            <div class="draft-rank" style="color:${isDrafted?"var(--border-1)":tier.color}">${i+1}</div>
            <div class="draft-main"><div class="draft-name">${playerLink(p.name)}${lockBadge(p.name,p.isPitcher)}<span class="draft-pos ${getPosClass(p.pos)}">${p.pos}</span><span style="margin-left:6px;cursor:pointer;opacity:.6" onclick="event.stopPropagation();streakToDash('${esc(p.name)}')">${icon('stats')}</span></div><div class="draft-meta">${metaLine}</div>${p.returning?`<div class="risk-subnote">Returning from absence — season averages may not reflect current form.</div>`:""}${tags.length?`<div class="draft-tags">${tags.join("")}</div>`:""}</div>
            <div class="draft-fp"><div class="draft-fp-val" style="color:${isDrafted?"var(--border-1)":tier.color}">${p.projUD}</div><div class="draft-fp-lbl">${locked?"STARTED":"UD FP"}</div>${l7v!==projv?`<div style="font-size:var(--t-xs);color:${l7v>projv?"var(--over)":"var(--under)"};margin-top:1px">L7: ${p.l7UD}</div>`:""}</div>
          </div>`;
        });
        html+=`</div>`;
        if(stacks.length){
          html+=`<div style="padding:14px 16px 4px;color:var(--accent);font-size:var(--t-sm);font-weight:700">⚡ Stacks</div><div style="padding:0 16px 6px;color:var(--ink-muted);font-size:var(--t-xs)">Top 2-player stacks ranked by combined UD projection, weak-pitcher targets, and Coors boosts.</div><div class="cards-grid">`;
          html+=stacks.map((s,i)=>`<div class="bet-card ${i===0?"elite":"mid"}" style="cursor:default"><div class="bet-left"><div class="bet-name">${playerLink(s.players[0].name)} + ${playerLink(s.players[1].name)}</div><div class="bet-meta">${esc(s.team)} vs ${esc(s.pitcher)}${s.era?` · ERA ${s.era.toFixed(2)}`:""}${s.venue?` · ${esc(s.venue)}`:""}</div><div class="draft-tags" style="margin-top:6px">${s.tags.map(tag=>`<span class="draft-tag" style="background:${tag.includes("CORRELATED")?"#60a5fa22":tag.includes("HIGH TOTAL")?"var(--warn-soft)":"#34d39922"};color:${tag.includes("CORRELATED")?"#60a5fa":tag.includes("HIGH TOTAL")?"var(--warn)":"#34d399"}">${tag}</span>`).join("")}</div></div><div class="bet-right"><div class="bet-edge pos">${s.combinedProj}</div><div class="bet-sub">UD FP</div></div></div>`).join("");
          html+=`</div>`;
        }
      }
  return html;
}

function renderBetsBoardView(convergenceHTML){
  let html="";
      const allBets=getMarketEdges();
      const posEV=allBets.filter(b=>b.edge>=0.05);
      const elite=posEV.filter(b=>b.edge>=0.15);
      const strong=posEV.filter(b=>b.edge>=0.08&&b.edge<0.15);
      if(!allBets.length){html=convergenceHTML+`<div class="empty" style="padding:40px">No props available for +EV analysis. Run the engine with DK props first.</div>`}
      else if(!posEV.length){html=convergenceHTML+`<div class="props-pass"><div class="props-pass-title">No actionable market edges this week</div><div class="props-pass-copy">No eligible side clears both the +5% edge floor and the ${MARKET_EDGE_MIN_ODDS} price floor. Passing is better than promoting a heavily juiced near-certainty.</div></div>`}
      else{
        html=convergenceHTML+`<div class="bet-summary"><div class="bs-card"><div class="bs-val">${posEV.length}</div><div class="bs-lbl">+EV PROPS</div></div><div class="bs-card"><div class="bs-val" style="color:var(--under)">${elite.length}</div><div class="bs-lbl">ELITE (15%+)</div></div><div class="bs-card"><div class="bs-val" style="color:var(--accent)">${strong.length}</div><div class="bs-lbl">STRONG (8%+)</div></div><div class="bs-card"><div class="bs-val" style="color:var(--ink-muted)">${allBets.length}</div><div class="bs-lbl">ANALYZED</div></div></div>`;
        html+=`<div style="padding:0 16px 4px;color:var(--ink-muted);font-size:var(--t-xs)">Edge = Your hit rate − DK implied probability. Higher = more value. Min 3 games of data.</div>`;
        html+=`<div class="cards-grid">`;
        html+=posEV.slice(0,40).map((b,i)=>{
          const edgePct=(b.edge*100).toFixed(1);
          const hrPct=(b.hitRate*100).toFixed(0);
          const ipPct=(b.impliedProb*100).toFixed(0);
          const cls=b.edge>=0.15?"elite":b.edge>=0.08?"strong":"mid";
          const leanCls=b.lean==="OVER"?"prop-over":"prop-under";
          const badges=riskBadges(b.name,b.isP,{showLimited:false});
          const locked=getLockInfo(b.name,b.isP).started;
          return`<div class="bet-card ${cls}${locked?" locked-card":""}" style="cursor:pointer" onclick="streakToDash('${esc(b.name)}')">
            <div class="bet-left">
              <div class="bet-name">${b.isP?icon('ball'):""}${playerLink(b.name,b.metric,b.dkLine)}${badges}${lockBadge(b.name,b.isP)}</div>
              <div class="bet-meta">${esc(b.team)} vs ${b.isP?esc(b.opp):esc(b.pitcher)+(b.hand?" ("+b.hand+"HP)":"")} · ${b.hits}/${b.total} games</div>
              <div class="bet-prop">
                <span class="prop-metric" style="font-size:var(--t-xs)">${b.metric}</span>
                <span class="${leanCls}" style="font-weight:700;font-size:var(--t-sm)">${b.lean} ${b.dkLine}</span>
                <span style="color:var(--accent-soft);font-size:var(--t-xs)">${fmtOdds(b.odds)}</span>
                <span class="ev-badge ev-pos ev-big ${b.returning||locked?"muted-risk":""}">+${edgePct}% EV</span>
              </div>
              ${renderBestBookLine(b.prop,b.lean)}
              <div class="bet-bar ${b.returning||locked?"muted-risk":""}"><div class="bet-bar-fill" style="width:${hrPct}%;background:${b.edge>=0.15?"var(--under)":b.edge>=0.08?"var(--over)":"var(--warn)"}"></div></div>
              <div style="display:flex;justify-content:space-between;margin-top:3px;font-size:var(--t-xs);color:var(--ink-muted)"><span>You: ${hrPct}%</span><span>DK: ${ipPct}%</span></div>
            </div>
            <div class="bet-right">
              <div class="bet-edge pos ${b.returning||locked?"muted-risk":""}">+${edgePct}%</div>
              <div class="bet-sub">${locked?"started":b.returning?"reduced":"edge"}</div>
            </div>
          </div>`;
        }).join("");
        html+=`</div>`;
      }
  return html;
}

function renderSlipsBoardView(convergenceHTML){
  let html="";
      const result=getSmartSlips();
      const {legs}=result;
      if(!legs.length){html=convergenceHTML+`<div class="empty" style="padding:40px">No +EV props available to build slips. Run the engine with DK props first.</div>`}
      else{
        const slips=st.slipLegs==="3"?result.slips3:st.slipLegs==="4"?result.slips4:result.slips5;
        const payouts={"3":"6x","4":"10x","5":"20x"};
        const topLeg=legs[0];
        const aiCount=legs.filter(l=>l.hasAI).length;
        const conflictCount=legs.filter(l=>l.hasAIConflict).length;
        const streakCount=legs.filter(l=>l.hasStreak).length;
  
        html=convergenceHTML+`<div class="bet-summary"><div class="bs-card"><div class="bs-val">${legs.length}</div><div class="bs-lbl">ELIGIBLE LEGS</div></div><div class="bs-card"><div class="bs-val" style="color:var(--accent)">${aiCount}</div><div class="bs-lbl">AI-BACKED</div></div><div class="bs-card"><div class="bs-val" style="color:#ffaa00">${streakCount}</div><div class="bs-lbl">ON STREAKS</div></div><div class="bs-card"><div class="bs-val" style="color:#fca5a5">${conflictCount}</div><div class="bs-lbl">AI CONFLICTS</div></div><div class="bs-card"><div class="bs-val" style="color:var(--accent-soft)">${payouts[st.slipLegs]}</div><div class="bs-lbl">PAYOUT</div></div></div>`;
        html+=`<div class="slip-controls"><span style="color:var(--ink-muted);font-size:var(--t-xs)">Legs:</span><div class="pf-btn ${st.slipLegs==="3"?"active":""}" onclick="setSlipLegs('3')">3-Leg (6x)</div><div class="pf-btn ${st.slipLegs==="4"?"active":""}" onclick="setSlipLegs('4')">4-Leg (10x)</div><div class="pf-btn ${st.slipLegs==="5"?"active":""}" onclick="setSlipLegs('5')">5-Leg (20x)</div></div>`;
        html+=`<div style="padding:0 16px 4px;color:var(--ink-muted);font-size:var(--t-xs)">Conviction = EV edge + AI confidence + streak heat + hit rate. Unique players, max 2 per team. AI disagreements show inline on the leg.</div>`;
  
        if(!slips.length){html+=`<div class="empty">Not enough eligible legs for ${st.slipLegs}-leg slips. Try fewer legs.</div>`}
        else{
          html+=slips.map((slip,si)=>{
            const isBest=si===0;
            const isAgg=parseInt(st.slipLegs)>=5;
            const avgEdgePct=(slip.avgEdge*100).toFixed(1);
            const avgHRPct=(slip.avgHitRate*100).toFixed(0);
            const allSignals=slip.legs.reduce((a,l)=>a.concat(l.signals),[]);
            const uniqueSignals=[...new Set(allSignals)].slice(0,4);
  
            return`<div class="slip-card ${isBest?"best":""}${isAgg?" aggressive":""}">
              <div class="slip-header">
                <span class="slip-rank">${isBest?"⭐ BEST":"#"+(si+1)} · ${st.slipLegs}-LEG</span>
                <span class="slip-score">${slip.score.toFixed(1)} pts</span>
              </div>
              <div class="slip-legs">${slip.legs.map(l=>{
                const leanCls=l.lean==="OVER"?"over":"under";
                const locked=getLockInfo(l.name,l.isP).started;
                return`<div class="slip-leg${locked?" locked-card":""}">
                  <span class="slip-leg-team">${esc(l.team)}</span>
                  <div style="flex:1;min-width:0">
                    <span class="slip-leg-name" style="cursor:pointer;text-decoration:underline dotted color-mix(in srgb, var(--accent) 53%, transparent)" onclick="event.stopPropagation();streakToDash('${esc(l.name)}','${l.metric}','${l.dkLine}')">${l.isP?icon('ball'):""}${playerLink(l.name,l.metric,l.dkLine)}</span>${lockBadge(l.name,l.isP)}
                    ${l.aiDisagreementText?`<div style="font-size:var(--t-xs);color:${l.aiConflictLevel==="strong"?"#fca5a5":"#fde68a"};margin-top:2px">${esc(l.aiDisagreementText)}</div>`:""}
                  </div>
                  <div class="slip-leg-prop">
                    <span class="slip-leg-metric">${l.metric}</span>
                    <span class="slip-leg-lean ${leanCls}">${l.lean} ${l.dkLine}</span>
                    <span class="slip-leg-edge">+${(l.edge*100).toFixed(0)}%</span>
                  </div>
                </div>`;
              }).join("")}</div>
              ${(uniqueSignals.length||slip.slipTags?.length)?`<div class="slip-tags">${[...new Set([...(slip.slipTags||[]),...uniqueSignals])].map(s=>`<span class="slip-tag" style="background:var(--surface-2);color:var(--accent-soft);border:1px solid var(--border-1)">${s}</span>`).join("")}</div>`:""}
              ${renderCrossBookWarning(slip.legs)}<div class="slip-meta"><span>Avg edge: +${avgEdgePct}%</span><span>Avg hit: ${avgHRPct}%</span><span>${slip.teams.length} teams</span></div>
            </div>`;
          }).join("");
        }
      }
  return html;
}

function renderPropExplorerView(){
  let html="";
      const allM=[...new Set(st.props.map(p=>p.METRIC).filter(Boolean))].sort();
      const allTeams=[...new Set([...st.tonight,...st.pTonight].map(p=>String(p.team_abbr||"").toUpperCase()).filter(Boolean))].sort((a,b)=>teamDisplayName(a).localeCompare(teamDisplayName(b)));
      const query=normalizePlayerName(st.propsSearch);
      const minHit=parseFloat(st.propsMinHit)/100;
      const minEdge=parseFloat(st.propsMinEdge)/100;
      const rankedProps=getRankedPropsBoard();
      let filtered=rankedProps.filter(row=>{
        const p=row.prop;
        if(st.propsMetric!=="ALL"&&p.METRIC!==st.propsMetric)return false;
        if(st.propsTeam!=="ALL"&&row.team!==st.propsTeam)return false;
        if(query&&!normalizePlayerName(`${p.PLAYER_NAME} ${row.team} ${row.teamName}`).includes(query))return false;
        if(minHit>0&&(row.hitRate===null||row.hitRate<minHit))return false;
        if(minEdge>-1&&(row.edge===null||row.edge<minEdge))return false;
        return true;
      });
      const sortValue=(row,key)=>key==="HIT"?(row.hitRate??-Infinity):key==="EDGE"?(row.edge??-Infinity):key==="PLAYER"?0:(row.score??-Infinity);
      filtered.sort((a,b)=>st.propsSort==="PLAYER"?(a.prop.PLAYER_NAME||"").localeCompare(b.prop.PLAYER_NAME||""):sortValue(b,st.propsSort)-sortValue(a,st.propsSort)||(b.hitRate??-Infinity)-(a.hitRate??-Infinity)||(a.prop.PLAYER_NAME||"").localeCompare(b.prop.PLAYER_NAME||""));
      const sorted=filtered.slice(0,200);
      const playerCount=new Set(filtered.map(row=>normalizePlayerName(row.prop.PLAYER_NAME))).size;
      const teamBoardHTML=renderPropsTeamBoard(st.propsTeam,rankedProps);
      html=`<div style="padding:14px 16px 0"><div class="analysis-eyebrow">Market research</div><div style="font-family:'Barlow Condensed',system-ui,sans-serif;font-size:var(--t-xl);font-weight:800;color:var(--ink-0)">Prop Explorer</div><div style="color:var(--ink-muted);font-size:var(--t-xs);margin-top:2px">Explore this week's available markets. Default view shows only props with at least +5% modeled edge.</div></div><div class="props-toolbar">
        <div class="props-control props-control-search"><label for="propsSearchInput">Player or team</label><input type="text" id="propsSearchInput" placeholder="Search Harper, TOR, Blue Jays..." value="${esc(st.propsSearch)}"/></div>
        <div class="props-control"><label for="propsTeamSelect">Team</label><select id="propsTeamSelect"><option value="ALL">All teams</option>${allTeams.map(team=>`<option value="${esc(team)}" ${st.propsTeam===team?"selected":""}>${esc(teamDisplayName(team))} (${esc(team)})</option>`).join("")}</select></div>
        <div class="props-control"><label for="propsSortSelect">Rank by</label><select id="propsSortSelect"><option value="EDGE" ${st.propsSort==="EDGE"?"selected":""}>Edge %</option><option value="HIT" ${st.propsSort==="HIT"?"selected":""}>Hit %</option><option value="SCORE" ${st.propsSort==="SCORE"?"selected":""}>Research score</option><option value="PLAYER" ${st.propsSort==="PLAYER"?"selected":""}>Player name</option></select></div>
        <div class="props-control"><label for="propsMinHitSelect">Minimum Hit%</label><select id="propsMinHitSelect">${[[0,"Any"],[50,"50%+"],[60,"60%+"],[70,"70%+"]].map(([v,l])=>`<option value="${v}" ${String(st.propsMinHit)===String(v)?"selected":""}>${l}</option>`).join("")}</select></div>
        <div class="props-control"><label for="propsMinEdgeSelect">Minimum Edge%</label><select id="propsMinEdgeSelect">${[[-100,"Any"],[0,"Positive"],[5,"+5%"],[10,"+10%"],[15,"+15%"]].map(([v,l])=>`<option value="${v}" ${String(st.propsMinEdge)===String(v)?"selected":""}>${l}</option>`).join("")}</select></div>
      </div>
      ${teamBoardHTML}
      <div class="props-filter"><div class="pf-btn ${st.propsMetric==="ALL"?"active":""}" onclick="setPropsMetric('ALL')">All</div>${allM.map(m=>`<div class="pf-btn ${st.propsMetric===m?"active":""}" onclick="setPropsMetric('${m}')">${m}</div>`).join("")}</div>
      <div style="padding:0 16px;color:var(--ink-muted);font-size:var(--t-xs);margin-bottom:4px">${filtered.length} props across ${playerCount} players${filtered.length>200?" · showing top 200":""} · ranked by ${st.propsSort==="SCORE"?"research score":st.propsSort==="HIT"?"Hit%":st.propsSort==="EDGE"?"Edge%, then Hit%":"player"}</div>
      ${sorted.length?`<div class="props-tbl-wrap"><table><thead><tr><th>#</th><th>Player</th><th>Team</th><th>Prop</th><th>Best Side</th><th>Over</th><th>Under</th><th>Hit%</th><th>Edge</th><th>Research Score</th></tr></thead><tbody>${sorted.map((row,i)=>{
        const p=row.prop;
        const flags=getSampleFlags(p.PLAYER_NAME,row.isP);
        const locked=getLockInfo(p.PLAYER_NAME,row.isP).started;
        const hrPct=row.hitRate!==null?`${(row.hitRate*100).toFixed(0)}%`:"—";
        const edgeStr=row.edge!==null?`<span class="ev-badge ${row.edge>0.08?"ev-pos":row.edge>0?"ev-neutral":"ev-neg"}">${row.edge>0?"+":""}${(row.edge*100).toFixed(0)}%</span>`:"—";
        const matchupDisplay=Math.abs(row.components.matchup)<0.5?0:row.components.matchup;
        const breakdown=`Hit ${row.components.hit.toFixed(1)} · Edge ${row.components.edge.toFixed(1)} · Form ${row.components.form.toFixed(0)} · Matchup ${matchupDisplay.toFixed(0)}`;
        const weak=row.edge===null||row.edge<0.05;
        return`<tr class="${flags.returning?"props-returning":""}${locked?" props-locked":""}${weak?" props-weak":""}" style="cursor:pointer" onclick="streakToDash('${esc(p.PLAYER_NAME)}','${propToLogCol(p.METRIC)}','${p.DK_LINE}')"><td style="color:var(--ink-muted);font-weight:700">${i+1}</td><td style="text-align:left;font-weight:600">${playerLink(p.PLAYER_NAME,propToLogCol(p.METRIC),p.DK_LINE)}${flags.returning?` <span class="risk-badge risk-returning">⚠️</span>`:flags.limited?` <span class="risk-badge risk-limited">⚠️</span>`:""}${locked?` <span class="locked-badge">🔒</span>`:""}</td><td title="${esc(row.teamName)}"><strong>${esc(row.team||"—")}</strong>${row.opp?` <span style="color:var(--ink-muted)">vs ${esc(row.opp)}</span>`:""}</td><td><span style="color:var(--accent);font-weight:600">${p.METRIC}</span><div style="color:var(--ink-muted);font-size:9px">line ${esc(p.DK_LINE)}</div></td><td>${row.side?`<span class="props-side ${row.side.toLowerCase()}">${row.side} ${fmtOdds(row.odds)}</span>`:"—"}</td><td class="${parseInt(p.OVER_ODDS)<=-130?"odds-over":parseInt(p.OVER_ODDS)>=130?"odds-under":"odds-even"}">${fmtOdds(p.OVER_ODDS)}</td><td class="${parseInt(p.UNDER_ODDS)<=-130?"odds-over":parseInt(p.UNDER_ODDS)>=130?"odds-under":"odds-even"}">${fmtOdds(p.UNDER_ODDS)}</td><td style="font-weight:700">${hrPct}</td><td>${edgeStr}</td><td title="${esc(breakdown)}"><span class="props-score">${row.score.toFixed(1)}</span><div class="props-score-detail">H ${row.components.hit.toFixed(1)} · E ${row.components.edge.toFixed(1)} · F ${row.components.form.toFixed(0)} · M ${matchupDisplay.toFixed(0)}</div></td></tr>${renderPropBestBookTableRow(p,10,{collapsed:true})}`}).join("")}</tbody></table></div>`:`<div class="props-pass"><div class="props-pass-title">No props clear these filters</div><div class="props-pass-copy">That is a valid result, not a broken board. Lower the minimum edge or change the team/market filter to explore the wider slate.</div></div>`}`;
  return html;
}

// ============================================================================
// BEST BALL DRAFT BOARD
// ============================================================================
// Model projection and consensus are shown SIDE BY SIDE with the gap explicit,
// never collapsed into one ranking. The model is unvalidated (no backtest), so
// a disagreement is a prompt to look closer, not a signal to trust. Collapsing
// them would hide exactly the information needed to judge that.

// Underdog rosters are 18 deep with a 1 QB / 2 RB / 3 WR / 1 TE / 1 FLEX
// lineup, so these are build targets for an 18-man draft, not lineup slots.
const BB_ROSTER_TARGETS={QB:2,RB:5,WR:9,TE:2};
const BB_ROSTER_SIZE=18;
const BB_DRAFTABLE_ECR=BB_ROSTER_SIZE*12;  // 216 total picks in a 12-team draft
function bbIsDraftable(r){
  return (r.ecr&&r.ecr<=BB_DRAFTABLE_ECR)||(r.modelRank&&r.modelRank<=BB_DRAFTABLE_ECR);
}

function bbSourceScoring(){
  const raw=String(rowField((st.projections||[])[0]||{},"scoring_format")||"").toLowerCase();
  return raw==="ppr"?"full":"half";
}

function bbProjectedPoints(row,scoring=st.bbScoring){
  const base=toNum(row.projPpr);
  const rec=toNum(row.projReceptions);
  const source=bbSourceScoring();
  if(source===scoring)return base;
  if(source==="half"&&scoring==="full")return base+(0.5*rec);
  if(source==="full"&&scoring==="half")return base-(0.5*rec);
  return base;
}

function bbWithDisplayStats(rows,scoring=st.bbScoring){
  const enriched=(rows||[]).map(r=>({...r,displayProj:bbProjectedPoints(r,scoring)}));
  const replacementByPos={};
  Object.entries(BB_ROSTER_TARGETS).forEach(([pos,targetPerRoster])=>{
    const startersNeeded=targetPerRoster*12;
    const pool=enriched
      .filter(r=>r.pos===pos&&Number.isFinite(r.displayProj))
      .sort((a,b)=>(b.displayProj||0)-(a.displayProj||0));
    const replacement=pool[startersNeeded-1]?.displayProj ?? pool[pool.length-1]?.displayProj ?? 0;
    replacementByPos[pos]=replacement;
  });
  return enriched.map(r=>({
    ...r,
    displayVorp:Math.max(0,(r.displayProj||0)-(replacementByPos[r.pos]||0)),
    replacementProj:replacementByPos[r.pos]||0
  }));
}

function bbScarcityRows(rows){
  const basePool=(rows||[]).filter(r=>r&&r.pos&&Number.isFinite(r.displayProj||r.projPpr));
  return Object.entries(BB_ROSTER_TARGETS).map(([pos,targetPerRoster])=>{
    const startersNeeded=targetPerRoster*12;
    const sorted=basePool
      .filter(r=>r.pos===pos)
      .sort((a,b)=>((b.displayProj||b.projPpr||0)-(a.displayProj||a.projPpr||0)));
    const cutoff=sorted[startersNeeded-1]||null;
    const nextUp=sorted[startersNeeded]||null;
    const cutoffProj=cutoff?(cutoff.displayProj??cutoff.projPpr):0;
    const nextProj=nextUp?(nextUp.displayProj??nextUp.projPpr):0;
    const cliff=cutoff&&nextUp?(cutoffProj-nextProj):0;
    return {
      pos,
      startersNeeded,
      available:sorted.length,
      cutoff,
      nextUp,
      cliff
    };
  });
}

function bbRows(){
  return (st.projections||[]).map(r=>({
    id:String(rowField(r,"player_id")||rowField(r,"player_display_name")||""),
    name:cleanName(rowField(r,"player_display_name","player_name")),
    pos:String(rowField(r,"position","pos")||"").toUpperCase(),
    team:rowField(r,"team_now","team_abbr")||"",
    bye:rowField(r,"bye"),
    ecr:toNum(rowField(r,"ecr")),
    ecrSd:toNum(rowField(r,"ecr_sd")),
    projPpr:toNum(rowField(r,"proj_ppr")),
    projReceptions:toNum(rowField(r,"proj_receptions")),
    projGames:toNum(rowField(r,"proj_games")),
    vorp:toNum(rowField(r,"vorp")),
    modelRank:toNum(rowField(r,"model_rank")),
    posRank:toNum(rowField(r,"model_pos_rank")),
    delta:toNum(rowField(r,"ecr_vs_model")),
    confidence:String(rowField(r,"confidence")||""),
    source:String(rowField(r,"proj_source")||"")
  })).filter(r=>r.name&&r.pos);
}

function bbToggleDrafted(id){
  if(st.bbDrafted.has(id))st.bbDrafted.delete(id);
  else{
    st.bbDrafted.add(id);
    if(st.bbTaken.has(id)){
      st.bbTaken.delete(id);
      saveBestBallTaken();
    }
    if(st.bbQueue.has(id)){
      st.bbQueue.delete(id);
      saveBestBallQueue();
    }
  }
  saveBestBallDrafted();render();
}
function bbToggleTaken(id){
  if(st.bbTaken.has(id))st.bbTaken.delete(id);
  else{
    st.bbTaken.add(id);
    if(st.bbDrafted.has(id)){
      st.bbDrafted.delete(id);
      saveBestBallDrafted();
    }
    if(st.bbQueue.has(id)){
      st.bbQueue.delete(id);
      saveBestBallQueue();
    }
  }
  saveBestBallTaken();render();
}
function bbResetDraft(){
  st.bbDrafted=new Set();
  st.bbTaken=new Set();
  saveBestBallDrafted();
  saveBestBallTaken();
  render();
}
function bbToggleQueue(id){
  if(st.bbQueue.has(id))st.bbQueue.delete(id);
  else if(!st.bbDrafted.has(id)&&!st.bbTaken.has(id))st.bbQueue.add(id);
  saveBestBallQueue();render();
}
function bbClearQueue(){st.bbQueue=new Set();saveBestBallQueue();render()}
function bbSetPos(p){st.bbPos=p;render()}
function bbSetSort(k){st.bbSort=k;render()}
function bbToggleHide(){st.bbHideDrafted=!st.bbHideDrafted;render()}
function bbSetSearch(v){st.bbSearch=String(v||"");render()}
function bbSetTeam(v){st.bbTeam=String(v||"ALL");render()}
function bbToggleDraftable(){st.bbDraftableOnly=!st.bbDraftableOnly;render()}
function bbSetScoring(v){st.bbScoring=v==="full"?"full":"half";render()}

function bbRosterPressure(rows){
  const mine=(rows||[]).filter(r=>st.bbDrafted.has(r.id));
  const byeCounts={};
  const teamCounts={};
  mine.forEach(r=>{
    if(r.bye)byeCounts[r.bye]=(byeCounts[r.bye]||0)+1;
    if(r.team)teamCounts[r.team]=(teamCounts[r.team]||0)+1;
  });
  const byeStacks=Object.entries(byeCounts)
    .sort((a,b)=>b[1]-a[1]||String(a[0]).localeCompare(String(b[0])))
    .map(([week,count])=>({week,count,warning:count>=3}));
  const teamStacks=Object.entries(teamCounts)
    .sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))
    .map(([team,count])=>({team,count,warning:count>=3}));
  const qbStacks=mine.filter(r=>r.pos==="QB").map(qb=>{
    const mates=mine.filter(r=>r.id!==qb.id&&r.team===qb.team&&["WR","TE","RB"].includes(r.pos));
    return {qb:qb.name,team:qb.team,count:mates.length,mates:mates.map(r=>r.name),warning:mates.length===0};
  });
  return {mine,byeStacks,teamStacks,qbStacks};
}

function bbNextTargets(rows){
  const all=rows||[];
  const mine=all.filter(r=>st.bbDrafted.has(r.id));
  const available=all.filter(r=>!st.bbDrafted.has(r.id)&&!st.bbTaken.has(r.id));
  const counts={};
  mine.forEach(r=>{counts[r.pos]=(counts[r.pos]||0)+1});
  const scarcityByPos=Object.fromEntries(bbScarcityRows(all).map(item=>[item.pos,item]));
  const posPriority=Object.entries(BB_ROSTER_TARGETS)
    .map(([pos,target])=>({
      pos,
      have:counts[pos]||0,
      need:Math.max(0,target-(counts[pos]||0)),
      cliff:toNum(scarcityByPos[pos]?.cliff)
    }))
    .sort((a,b)=>b.need-a.need||b.cliff-a.cliff||a.pos.localeCompare(b.pos));

  const picks=[];
  const seen=new Set();
  posPriority.forEach(item=>{
    if(item.need<=0)return;
    available
      .filter(r=>r.pos===item.pos)
      .sort((a,b)=>(b.displayVorp||0)-(a.displayVorp||0))
      .slice(0,2)
      .forEach(r=>{
        if(seen.has(r.id))return;
        seen.add(r.id);
        picks.push({...r,needPos:item.pos,needCount:item.need,needCliff:item.cliff});
      });
  });
  return picks.slice(0,6);
}

function bbStackTargets(rows){
  const all=rows||[];
  const mine=all.filter(r=>st.bbDrafted.has(r.id));
  const available=all.filter(r=>!st.bbDrafted.has(r.id)&&!st.bbTaken.has(r.id));
  const qbs=mine.filter(r=>r.pos==="QB");
  if(qbs.length){
    return available
      .filter(r=>["WR","TE","RB"].includes(r.pos)&&qbs.some(qb=>qb.team===r.team))
      .sort((a,b)=>(b.displayVorp||0)-(a.displayVorp||0))
      .slice(0,6)
      .map(r=>{
        const qb=qbs.find(item=>item.team===r.team);
        return {...r,stackType:"qb_mate",stackLabel:qb?`${qb.name} stack`:"QB stack"};
      });
  }
  const passCatcherTeams=[...new Set(mine.filter(r=>["WR","TE","RB"].includes(r.pos)).map(r=>r.team).filter(Boolean))];
  if(passCatcherTeams.length){
    return available
      .filter(r=>r.pos==="QB"&&passCatcherTeams.includes(r.team))
      .sort((a,b)=>(b.displayVorp||0)-(a.displayVorp||0))
      .slice(0,6)
      .map(r=>({...r,stackType:"qb_attach",stackLabel:`Attach to ${r.team} pass-catchers`}));
  }
  return [];
}

function renderBestBallRoster(rows){
  const mine=rows.filter(r=>st.bbDrafted.has(r.id));
  const queue=rows.filter(r=>st.bbQueue.has(r.id));
  const taken=rows.filter(r=>st.bbTaken.has(r.id));
  const nextTargets=bbNextTargets(rows);
  const stackTargets=bbStackTargets(rows);
  const byPos={};
  mine.forEach(r=>{byPos[r.pos]=(byPos[r.pos]||0)+1});
  const pressure=bbRosterPressure(rows);
  const stacked=pressure.byeStacks.filter(item=>item.warning).map(item=>`Wk ${esc(item.week)} (${item.count})`);
  const topBye=pressure.byeStacks[0]||null;
  const topTeam=pressure.teamStacks[0]||null;
  const unstackedQBs=pressure.qbStacks.filter(item=>item.warning);
  const bestStackedQB=[...pressure.qbStacks].sort((a,b)=>b.count-a.count)[0]||null;
  const byeAction=topBye
    ? (topBye.warning
      ? `Ease off Week ${esc(topBye.week)} unless the value is obvious.`
      : `Current heaviest cluster is Week ${esc(topBye.week)} with only ${topBye.count}.`)
    : "No bye clusters yet.";
  const teamAction=topTeam
    ? (topTeam.warning
      ? `You are leaning hard into ${esc(topTeam.team)}. Diversify unless you're making a deliberate bet.`
      : `${esc(topTeam.team)} is your biggest mini-stack, but it's still under control.`)
    : "No team concentration yet.";
  const qbPriority=unstackedQBs[0]||null;
  const qbAction=qbPriority
    ? `Add a ${esc(qbPriority.team)} pass-catcher for ${esc(qbPriority.qb)} next if the room lets you.`
    : (bestStackedQB
      ? `${esc(bestStackedQB.qb)} already has ${bestStackedQB.count} teammate${bestStackedQB.count===1?"":"s"} attached.`
      : "Draft a QB and we'll start tracking stack pressure.");

  const slots=Object.entries(BB_ROSTER_TARGETS).map(([pos,target])=>{
    const have=byPos[pos]||0;
    return `<div class="bb-slot ${have<target?"bb-slot-need":""}">${pos} <strong>${have}</strong>/${target}</div>`;
  }).join("");

  const summary=`<div class="bb-summary-bar">
    <div class="bb-summary-pill ${mine.length>BB_ROSTER_SIZE?"bb-slot-need":""}">
      <span class="bb-summary-label">Drafted</span>
      <strong>${mine.length}</strong>/<span>${BB_ROSTER_SIZE}</span>
    </div>
    <div class="bb-summary-pill ${queue.length?"bb-slot-need":""}">
      <span class="bb-summary-label">Targets</span>
      <strong>${queue.length}</strong>
    </div>
    ${slots.replaceAll('bb-slot','bb-summary-pill')}
    ${taken.length?`<div class="bb-summary-pill"><span class="bb-summary-label">Room</span><strong>${taken.length}</strong></div>`:""}
    ${stacked.length?`<div class="bb-summary-pill bb-summary-pill-wide bb-slot-need"><span class="bb-summary-label">Bye cluster</span><strong>${stacked.join(" · ")}</strong></div>`:""}
  </div>`;

  const rail=`<div class="bb-rail-stack">
    <div class="bb-pressure-card ${topBye&&topBye.warning?"warn":""}">
      <div class="bb-pressure-label">Bye-week pressure</div>
      <div class="bb-pressure-value">${topBye?`Wk ${esc(topBye.week)} · ${topBye.count}`:"Balanced"}</div>
      <div class="bb-pressure-copy">${pressure.byeStacks.length?pressure.byeStacks.slice(0,3).map(item=>`Wk ${item.week} (${item.count})`).join(" · "):"No bye clusters yet."}</div>
      <div class="bb-pressure-copy">${byeAction}</div>
    </div>
    <div class="bb-pressure-card ${topTeam&&topTeam.warning?"warn":""}">
      <div class="bb-pressure-label">Team concentration</div>
      <div class="bb-pressure-value">${topTeam?`${esc(topTeam.team)} · ${topTeam.count}`:"Open board"}</div>
      <div class="bb-pressure-copy">${pressure.teamStacks.length?pressure.teamStacks.slice(0,3).map(item=>`${item.team} (${item.count})`).join(" · "):"No team stacks yet."}</div>
      <div class="bb-pressure-copy">${teamAction}</div>
    </div>
    <div class="bb-pressure-card ${unstackedQBs.length?"warn":""}">
      <div class="bb-pressure-label">QB stack pressure</div>
      <div class="bb-pressure-value">${bestStackedQB?`${esc(bestStackedQB.qb)} +${bestStackedQB.count}`:"No QB yet"}</div>
      <div class="bb-pressure-copy">${pressure.qbStacks.length?pressure.qbStacks.map(item=>item.count?`${item.qb.split(" ").slice(-1)[0]} +${item.count}`:`${item.qb.split(" ").slice(-1)[0]} unstacked`).join(" · "):"Draft a QB and we’ll track teammates here."}</div>
      <div class="bb-pressure-copy">${qbAction}</div>
    </div>
    <div class="card bb-note-card">
      <div class="card-title">Queue Coach</div>
      <div class="bb-note-copy">${queue.length?`Keep it to players you would actually click in the next two rounds.`:"Star names in the board to build a real next-up list."}</div>
      <div class="bb-note-row"><span class="bb-note-name">Current mix</span><span class="bb-note-meta">${queue.length?[...new Set(queue.map(r=>r.pos))].join(" · "):"No queue yet"}</span></div>
      <div class="bb-note-row"><span class="bb-note-name">Stack angle</span><span class="bb-note-meta">${stackTargets.length?"Correlation path live":"No active QB pair yet"}</span></div>
      <div class="bb-note-row"><span class="bb-note-name">Board status</span><span class="bb-note-meta">${taken.length?taken.length+" gone / "+rows.length+" visible":rows.length+" visible"}</span></div>
    </div>
    <div class="card bb-note-card">
      <div class="card-title">On Deck</div>
      <div class="bb-note-copy">${nextTargets.length?"Best available names weighted toward your current roster gaps and the live positional cliff.":"No urgent roster gaps yet. Sort by value and keep drafting the board."}</div>
      ${nextTargets.length?nextTargets.map(r=>`<div class="bb-note-row"><span class="bb-note-name">${esc(r.name)}</span><span class="bb-note-meta">${esc(r.team)} · ${esc(r.pos)} · ${Number.isFinite(r.displayProj)?r.displayProj.toFixed(1):"—"} pts</span></div>`).join(""):`<div class="bb-note-empty">Board looks balanced right now.</div>`}
    </div>
    <div class="card bb-note-card">
      <div class="card-title">Stack Targets</div>
      <div class="bb-note-copy">${stackTargets.length?"These are the cleanest correlation adds based on what you've already drafted.":"Draft a QB or a few pass-catchers first and the stack board will wake up."}</div>
      ${stackTargets.length?stackTargets.slice(0,6).map(r=>`<div class="bb-note-row"><span class="bb-note-name">${esc(r.name)}</span><span class="bb-note-meta">${esc(r.stackLabel)} · ${esc(r.team)} · ${esc(r.pos)}</span></div>`).join(""):`<div class="bb-note-empty">No active stack path yet.</div>`}
    </div>
  </div>`;

  return {summary,rail};
}

function renderBestBallView(){
  const sourceScoring=bbSourceScoring();
  const scoringLabel=st.bbScoring==="full"?"full PPR":".5 PPR";
  const all=bbWithDisplayStats(bbRows(),st.bbScoring);
  const rosterUI=renderBestBallRoster(all);
  const queue=all.filter(r=>st.bbQueue.has(r.id));
  if(!all.length){
    return `<section><div class="card" style="margin:16px">
      <div class="card-title">No projections yet</div>
      <p style="color:var(--ink-1);line-height:1.5">The engine hasn't written a <code>Projections</code> tab yet.
      Run the NFL Engine workflow, then reload.</p></div></section>`;
  }

  const positions=["ALL","QB","RB","WR","TE"];
  const posChips=positions.map(p=>
    `<div class="sub-tab ${st.bbPos===p?"active":""}" onclick="bbSetPos('${p}')">${p}</div>`).join("");
  const sorts=[["VORP","Value"],["ECR","Consensus"],["DELTA","Disagreement"]];
  const sortChips=sorts.map(([k,l])=>
    `<div class="sub-tab ${st.bbSort===k?"active":""}" onclick="bbSetSort('${k}')">${l}</div>`).join("");
  const teams=[...new Set(all.map(r=>r.team).filter(Boolean))].sort();
  const searchNeedle=normalizePlayerName(st.bbSearch);
  const scarcityPool=(st.bbDraftableOnly?all.filter(bbIsDraftable):all).filter(r=>!st.bbDrafted.has(r.id)&&!st.bbTaken.has(r.id));
  const scarcityRows=bbScarcityRows(scarcityPool);

  let rows=st.bbPos==="ALL"?all:all.filter(r=>r.pos===st.bbPos);
  if(searchNeedle)rows=rows.filter(r=>
    normalizePlayerName(r.name).includes(searchNeedle)||
    normalizePlayerName(r.team).includes(searchNeedle)
  );
  if(st.bbTeam!=="ALL")rows=rows.filter(r=>r.team===st.bbTeam);
  if(st.bbDraftableOnly)rows=rows.filter(bbIsDraftable);
  if(st.bbHideDrafted)rows=rows.filter(r=>!st.bbDrafted.has(r.id)&&!st.bbTaken.has(r.id));

  const filteredRows=[...rows];
  const filteredDrafted=filteredRows.filter(r=>st.bbDrafted.has(r.id)).length;
  const filteredTaken=filteredRows.filter(r=>st.bbTaken.has(r.id)).length;
  const topDisagreement=[...filteredRows]
    .filter(r=>r.ecr&&r.modelRank)
    .sort((a,b)=>Math.abs(b.delta)-Math.abs(a.delta))[0]||null;
  const modelTargets=[...filteredRows]
    .filter(r=>r.ecr&&r.modelRank&&r.delta>=8)
    .sort((a,b)=>b.delta-a.delta)
    .slice(0,3);
  const consensusTargets=[...filteredRows]
    .filter(r=>r.ecr&&r.modelRank&&r.delta<=-8)
    .sort((a,b)=>a.delta-b.delta)
    .slice(0,3);
  const riskRows=[...filteredRows]
    .filter(r=>r.source==="ecr_imputed"||r.confidence==="changed teams"||r.confidence==="partial season"||r.confidence==="small sample")
    .sort((a,b)=>{
      const order=v=>v==="changed teams"?0:v==="partial season"?1:v==="small sample"?2:3;
      return order(a.confidence)-order(b.confidence);
    })
    .slice(0,4);
  const topVorp=[...filteredRows].sort((a,b)=>(b.displayVorp||0)-(a.displayVorp||0))[0]||null;
  const avgProj=filteredRows.length
    ? filteredRows.reduce((sum,r)=>sum+(r.displayProj||0),0)/filteredRows.length
    : 0;

  rows=[...rows].sort((a,b)=>{
    if(st.bbSort==="ECR"){
      // Unranked players sort last rather than first, which is what a raw
      // ascending sort on 0 would do.
      const av=a.ecr||9999,bv=b.ecr||9999;return av-bv;
    }
    if(st.bbSort==="DELTA"){
      // Rank disagreement only among players who will actually be drafted.
      // Beyond the draftable pool both rankings are meaningless and their gap
      // is an artifact of the model ranking more players than consensus does.
      const ad=a.ecr&&a.ecr<=BB_DRAFTABLE_ECR?Math.abs(a.delta):-1;
      const bd=b.ecr&&b.ecr<=BB_DRAFTABLE_ECR?Math.abs(b.delta):-1;
      return bd-ad;
    }
    return (b.displayVorp||0)-(a.displayVorp||0);
  });

  const body=rows.slice(0,300).map(r=>{
    const drafted=st.bbDrafted.has(r.id);
    const taken=st.bbTaken.has(r.id);
    const queued=st.bbQueue.has(r.id);
    const deltaCls=r.delta>0?"bb-delta-up":r.delta<0?"bb-delta-dn":"";
    const deltaRounded=Math.round(r.delta);
    const deltaTxt=r.ecr?`${deltaRounded>0?"+":""}${deltaRounded}`:"—";
    const flag=r.source==="ecr_imputed"?`<span class="bb-flag" title="No prior-season usage at all (rookie, or a veteran who did not play); placed from consensus rank">no data</span>`
      :r.confidence==="changed teams"?`<span class="bb-flag" title="Changed teams — prior usage is less predictive">new tm</span>`
      :r.confidence==="partial season"||r.confidence==="small sample"?`<span class="bb-flag" title="${esc(r.confidence)}">${esc(r.confidence==="small sample"?"sm samp":"part szn")}</span>`:"";
    return `<tr class="${drafted?"bb-row-drafted":""}${taken?" bb-row-taken":""}">
      <td><span class="bb-take ${drafted?"active":""}" title="${drafted?"Remove from my roster":"I drafted this player"}" onclick="bbToggleDrafted('${esc(r.id)}')">${drafted?"↺":"+"}</span></td>
      <td><span class="bb-pass ${taken?"active":""}" title="${taken?"Return to available board":"Taken by another team"}" onclick="bbToggleTaken('${esc(r.id)}')">${taken?"↺":"×"}</span></td>
      <td><span class="bb-target ${queued?"active":""}" title="${queued?"Remove from target queue":"Add to target queue"}" onclick="bbToggleQueue('${esc(r.id)}')">${queued?"★":"☆"}</span></td>
      <td><span class="bb-name">${esc(r.name)}</span><span class="draft-pos draft-pos-${esc(r.pos.toLowerCase())}">${esc(r.pos)}</span>${flag}</td>
      <td>${esc(r.team)}</td>
      <td>${r.bye?esc(r.bye):"—"}</td>
      <td>${Number.isFinite(r.displayProj)?r.displayProj.toFixed(0):"—"}</td>
      <td>${r.projGames?r.projGames.toFixed(1):"—"}</td>
      <td>${Number.isFinite(r.displayVorp)?r.displayVorp.toFixed(0):"—"}</td>
      <td>${r.modelRank?r.modelRank.toFixed(0):"—"}</td>
      <td>${r.ecr?r.ecr.toFixed(1):"—"}</td>
      <td class="${deltaCls}">${deltaTxt}</td>
    </tr>`;
  }).join("");

  return `<section>
    <div style="padding:12px 16px 4px">
      <div style="color:var(--accent);font-size:var(--t-sm);font-weight:700">Best Ball Draft Board</div>
      <div style="color:var(--ink-muted);font-size:var(--t-xs);line-height:1.5;margin-top:2px">
${sourceScoring?`<span class="bb-flag">${esc(scoringLabel)}</span> `:""}
        Model projection and FantasyPros best-ball consensus side by side.
        <strong>Disagreement is a question, not an edge.</strong> Backtested over 7 seasons on a
        model-independent sample, this board beats simple carry-forward on both error and ranking,
        but only by a modest margin. That means the signal is useful, not magical: use it to
        pressure-test consensus, especially when role, availability, and age adjustments disagree
        with the market. Depth-chart role does most of the heavy lifting.${sourceScoring!==st.bbScoring?` Display converted from ${esc(sourceScoring)} scoring using projected receptions.`:""}
      </div>
    </div>
    <div class="bb-toolbar">
      <div class="props-control props-control-search">
        <label for="bbSearchInput">Player or team</label>
        <input type="text" id="bbSearchInput" placeholder="Search Barkley, PHI, QB..." value="${esc(st.bbSearch)}" oninput="bbSetSearch(this.value)"/>
      </div>
      <div class="props-control">
        <label for="bbTeamSelect">Team</label>
        <select id="bbTeamSelect" onchange="bbSetTeam(this.value)"><option value="ALL">All teams</option>${teams.map(team=>`<option value="${esc(team)}" ${st.bbTeam===team?"selected":""}>${esc(team)}</option>`).join("")}</select>
      </div>
    </div>
    <div class="draft-controls" style="padding:0 16px 8px;display:flex;gap:6px;flex-wrap:wrap;align-items:center">
      ${posChips}<span style="width:10px"></span>${sortChips}
      <span style="width:10px"></span>
      <div class="sub-tab ${st.bbScoring==="half"?"active":""}" onclick="bbSetScoring('half')">.5 PPR</div>
      <div class="sub-tab ${st.bbScoring==="full"?"active":""}" onclick="bbSetScoring('full')">Full PPR</div>
      <div class="sub-tab ${st.bbDraftableOnly?"active":""}" onclick="bbToggleDraftable()">Draftable only</div>
      <div class="sub-tab ${st.bbHideDrafted?"active":""}" onclick="bbToggleHide()">Hide unavailable</div>
      <div class="draft-reset" onclick="bbResetDraft()" style="cursor:pointer;color:var(--ink-muted);font-size:var(--t-xs);margin-left:auto">Reset</div>
    </div>
    <div class="bb-layout">
      <div class="bb-main">
        ${rosterUI.summary}
        <div class="bb-queue-strip">
          <div class="bb-queue-head">
            <div>
              <div class="bb-queue-title">Target Queue</div>
              <div class="bb-queue-copy">${queue.length?`${queue.length} queued target${queue.length===1?"":"s"} for your next turns.`:"Star names in the board to build a real next-up list."}</div>
            </div>
            ${queue.length?`<button type="button" class="bb-mini-btn" onclick="bbClearQueue()">Clear queue</button>`:""}
          </div>
          <div class="bb-queue-list">
            ${queue.length?queue.slice(0,10).map(r=>`<div class="bb-queue-chip">
              <span class="bb-queue-chip-name">${esc(r.name)}</span>
              <span class="bb-queue-chip-meta">${esc(r.team)} · ${esc(r.pos)} · bye ${r.bye||"—"}</span>
              <span class="bb-note-action" onclick="bbToggleQueue('${esc(r.id)}')">remove</span>
            </div>`).join(""):`<div class="bb-note-empty">No queued targets yet.</div>`}
          </div>
        </div>
        <div class="bb-wrap"><table>
          <thead><tr>
            <th title="Add to my roster">Mine</th><th title="Mark as taken by another team">Gone</th><th title="Save as a target">Queue</th><th>Player</th><th>Tm</th><th>Bye</th>
            <th title="Projected season points in the selected scoring view">Proj</th>
            <th title="Projected games played">G</th>
            <th title="Points above the last startable player at this position in the selected scoring view">VORP</th>
            <th title="Model rank by VORP">Mdl</th>
            <th title="FantasyPros best-ball expert consensus rank">ECR</th>
            <th title="ECR minus model rank. Positive = model higher on the player than consensus.">Δ</th>
          </tr></thead>
          <tbody>${body}</tbody>
        </table></div>
      </div>
      <aside class="bb-rail">${rosterUI.rail}</aside>
    </div>
    <div class="stat-grid">
      <div class="stat-box">
        <div class="val">${filteredRows.length}</div>
        <div class="lbl">${st.bbDraftableOnly?"Draftable pool":"Players in view"}</div>
      </div>
      <div class="stat-box">
        <div class="val">${filteredDrafted}</div>
        <div class="lbl">My picks in view</div>
      </div>
      <div class="stat-box">
        <div class="val">${filteredTaken}</div>
        <div class="lbl">Taken in current view</div>
      </div>
      <div class="stat-box">
        <div class="val">${topVorp?topVorp.displayVorp.toFixed(0):"—"}</div>
        <div class="lbl">${topVorp?`${topVorp.name} VORP`:"Top VORP"}</div>
      </div>
      <div class="stat-box">
        <div class="val">${topDisagreement?`${Math.round(topDisagreement.delta)>0?"+":""}${Math.round(topDisagreement.delta)}`:"—"}</div>
        <div class="lbl">${topDisagreement?`${topDisagreement.name} disagreement`:"Biggest disagreement"}</div>
      </div>
    </div>
    <div class="stat-grid" style="padding-top:0">
      <div class="stat-box">
        <div class="val">${avgProj?avgProj.toFixed(0):"—"}</div>
        <div class="lbl">Avg projected points</div>
      </div>
      <div class="stat-box">
        <div class="val">${filteredRows.filter(r=>r.pos==="QB").length}</div>
        <div class="lbl">QB in view</div>
      </div>
      <div class="stat-box">
        <div class="val">${filteredRows.filter(r=>r.pos==="RB").length}</div>
        <div class="lbl">RB in view</div>
      </div>
      <div class="stat-box">
        <div class="val">${filteredRows.filter(r=>r.pos==="WR"||r.pos==="TE").length}</div>
        <div class="lbl">WR/TE in view</div>
      </div>
    </div>
    <div class="bb-insights bb-insights-scarcity">
      ${scarcityRows.map(r=>{
        const cutoffLabel=r.cutoff?`${r.cutoff.name} · ${(r.cutoff.displayProj??r.cutoff.projPpr).toFixed(0)} pts`:"No cutoff yet";
        const nextLabel=r.nextUp?`${r.nextUp.name} · ${(r.nextUp.displayProj??r.nextUp.projPpr).toFixed(0)} pts`:"Pool exhausted";
        return `<div class="card bb-note-card">
          <div class="card-title">${esc(r.pos)} Scarcity</div>
          <div class="bb-note-copy">Starter line at ${r.startersNeeded} drafted. This is the replacement cliff for a 12-team build.</div>
          <div class="bb-note-row"><span class="bb-note-name">Starter cutoff</span><span class="bb-note-meta">${esc(cutoffLabel)}</span></div>
          <div class="bb-note-row"><span class="bb-note-name">Next up</span><span class="bb-note-meta">${esc(nextLabel)}</span></div>
          <div class="bb-note-row"><span class="bb-note-name">Cliff</span><span class="bb-note-meta">${r.cliff>0?`${r.cliff.toFixed(1)} pts drop`:"Flat tier"}</span></div>
        </div>`;
      }).join("")}
    </div>
    <div class="bb-insights">
      <div class="card bb-note-card">
        <div class="card-title">Model Likes More Than Consensus</div>
        <div class="bb-note-copy">Useful when we want upside names the room may let slide.</div>
        ${modelTargets.length?modelTargets.map(r=>`<div class="bb-note-row"><span class="bb-note-name">${esc(r.name)}</span><span class="bb-note-meta">${esc(r.team)} · ${esc(r.pos)} · ${r.delta>0?"+":""}${Math.round(r.delta)}</span></div>`).join(""):`<div class="bb-note-empty">No big model-over-consensus gaps in this view.</div>`}
      </div>
      <div class="card bb-note-card">
        <div class="card-title">Consensus Likes More Than Model</div>
        <div class="bb-note-copy">Good pressure-test list when the market is stronger than our projection.</div>
        ${consensusTargets.length?consensusTargets.map(r=>`<div class="bb-note-row"><span class="bb-note-name">${esc(r.name)}</span><span class="bb-note-meta">${esc(r.team)} · ${esc(r.pos)} · ${Math.round(r.delta)}</span></div>`).join(""):`<div class="bb-note-empty">No big consensus-over-model gaps in this view.</div>`}
      </div>
      <div class="card bb-note-card">
        <div class="card-title">Watchlist</div>
        <div class="bb-note-copy">Names where context matters most before we trust the ranking.</div>
        ${riskRows.length?riskRows.map(r=>`<div class="bb-note-row"><span class="bb-note-name">${esc(r.name)}</span><span class="bb-note-meta">${esc(r.team)} · ${esc(r.pos)} · ${esc(r.source==="ecr_imputed"?"no data":r.confidence||"watch")}</span></div>`).join(""):`<div class="bb-note-empty">No active watchlist flags in this view.</div>`}
      </div>
    </div>
    <div style="padding:0 16px 20px;color:var(--ink-quiet);font-size:var(--t-xs)">
      Showing ${Math.min(rows.length,300)} of ${rows.length}. Draftable pool defaults to the first ${BB_DRAFTABLE_ECR} picks by model rank or consensus rank. Consensus scraped by nflverse from FantasyPros.
    </div>
  </section>`;
}

function renderAppHeader({activeTab,showCtrl,player,metricOpts,curTonight}){
  const navItems=[
    ["dashboard","dash","Dash"],
    ["picks","picks","Picks"],
    ["leaders","leaders","Leaders"],
    ["entry","entry","Game Builder"],
    ["bestball","dash","Best Ball"],
    ["lookup","lookup","Lookup"],
    ["stats","stats","Model Performance"],
    ["method","info","Info"],
  ];
  const navigation=navItems.map(([tab,iconName,label])=>`
    <button class="tab-btn ${activeTab===tab?"active":""}" onclick="switchTab('${tab}')">
      ${icon(iconName)}<span>${label}</span>
    </button>`).join("");
  const controls=showCtrl?`
    <div class="header-controls">
      <div class="mode-toggle">
        <div class="mode-btn" onclick="switchMode('skill')" style="${st.mode==='skill'?'background:var(--over);color:var(--surface-0);border-color:var(--over)':'background:var(--surface-2);color:var(--ink-muted)'}">${icon('bat')} Skill</div>
        <div class="mode-btn" onclick="switchMode('qb')" style="${st.mode==='qb'?'background:var(--over);color:var(--surface-0);border-color:var(--over)':'background:var(--surface-2);color:var(--ink-muted)'}">${icon('ball')} QB</div>
      </div>
      <div class="search-wrap">
        <input type="text" id="dashPlayerSearch" list="playerList" placeholder="Search ${st.mode==='qb'?'quarterback':'skill player'}..." value="${esc(player)}" autocomplete="off"
          onfocus="this.select()"
          onchange="if(this.value)pickDashPlayer(this.value)"
        />
        <datalist id="playerList">${curTonight.filter(p=>p.player_name).map(p=>`<option value="${esc(p.player_name)}">${esc(p.team_abbr||"")}</option>`).join("")}</datalist>
      </div>
      <div class="ctrl-row">
        <select id="metricSel">${metricOpts}</select>
        <input type="number" id="lineInput" value="${st.line}" placeholder="Line" step="0.5"/>
      </div>
    </div>`:"";
  return`
    <div class="header">
      <div class="header-top"><div class="header-title">NFL DFS Dashboard</div><div style="display:flex;gap:8px"><button class="theme-btn" id="themeBtn">${st.theme==="light"?icon('moon')+" Dark":icon('sun')+" Light"}</button><button class="refresh-btn" id="refreshBtn">${icon('refresh')} Refresh</button></div></div>
      <div class="top-nav">${navigation}</div>
      ${controls}
    </div>`;
}

function renderPicksPage(activeTab,picksHTML){
  const views=[
    ["shortlist","This Week's Shortlist"],
    ["slips","Slips"],
    ["picks","Model Picks"],
    ["draft","Draft"],
    ["streaks","Streaks"],
    ["dingers","TDs"],
    ["ks","Passing"],
    ["props","Prop Explorer"],
  ];
  const tabs=views.map(([view,label])=>`<div class="sub-tab ${st.picksView===view?"active":""}" onclick="switchPicksView('${view}')">${label}</div>`).join("");
  return`
    <div id="pg-picks" class="page ${activeTab==="picks"?"active":""}">
      <div class="sub-tabs" style="padding-top:12px">${tabs}</div>
      <div class="cards-wrap">${picksHTML}</div>
      <div class="timestamp">Data from nflverse · multi-book pricing via The Odds API</div>
    </div>`;
}

function renderLookupPage(activeTab){
  if(!LOOKUP_PORTED){
    // Must be a #pg-lookup page div like every other page — render() emits the
    // header once at the top, so rendering it again here duplicated the nav.
    return`<div id="pg-lookup" class="page ${activeTab==="lookup"?"active":""}">
      <div class="card" style="margin:16px">
        <div class="card-title">Lookup is being rebuilt</div>
        <p style="color:var(--ink-1);line-height:1.5">This page was powered by the MLB Stats API — career splits,
        year-by-year, and head-to-head — which has no football equivalent, so it needs a rebuild rather than a rename.</p>
        <p style="color:var(--ink-muted);line-height:1.5">It will be rebuilt on nflverse, which carries roughly 25,000 players
        with a full ID crosswalk. In the meantime, <strong>Dash</strong> and <strong>Player Form</strong> cover
        per-player usage and game logs.</p>
      </div></div>`;
  }
  const lk=st.lkPlayer;
  const lkC=st.lkPlayerType==="qb"?[{k:"gamesPlayed",l:"G"},{k:"gamesStarted",l:"GS"},{k:"wins",l:"W"},{k:"losses",l:"L"},{k:"era",l:"ERA"},{k:"inningsPitched",l:"IP"},{k:"strikeOuts",l:"SO"},{k:"baseOnBalls",l:"BB"},{k:"whip",l:"WHIP"},{k:"avg",l:"BAA"}]:[{k:"gamesPlayed",l:"G"},{k:"atBats",l:"AB"},{k:"hits",l:"H"},{k:"homeRuns",l:"HR"},{k:"rbi",l:"RBI"},{k:"runs",l:"R"},{k:"stolenBases",l:"SB"},{k:"baseOnBalls",l:"BB"},{k:"strikeOuts",l:"SO"},{k:"avg",l:"AVG"},{k:"obp",l:"OBP"},{k:"slg",l:"SLG"},{k:"ops",l:"OPS"}];
  const fv=(s,k)=>{if(!s)return"—";const v=s[k];return v===undefined||v===null?"—":v};
  const mkT=(h,r)=>{if(!r||!r.length)return`<div class="empty">No data</div>`;return`<div class="lk-tbl-wrap"><table><thead><tr>${r[0].label?`<th></th>`:""}${h.map(x=>`<th>${x.l}</th>`).join("")}</tr></thead><tbody>${r.map(x=>`<tr>${x.label?`<td class="hl">${x.label}</td>`:""}${h.map(c=>`<td>${fv(x.stat||x,c.k)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`};

  let lkSum="",lkBody="";
  if(lk&&st.lkCareer){
    const cs=st.lkCareer;
    const bx=st.lkPlayerType==="qb"?[{v:cs.era||"—",l:"ERA"},{v:cs.wins||"—",l:"W"},{v:cs.strikeOuts||"—",l:"K"},{v:cs.whip||"—",l:"WHIP"}]:[{v:cs.avg||"—",l:"AVG"},{v:cs.homeRuns||"—",l:"HR"},{v:cs.hits||"—",l:"H"},{v:cs.ops||"—",l:"OPS"}];
    lkSum=`<div class="stat-grid">${bx.map(b=>`<div class="stat-box"><div class="val">${b.v}</div><div class="lbl">${b.l}</div></div>`).join("")}</div>`;
  }
  if(st.lkSubTab==="career"){
    if(st.lkYby){const rows=st.lkYby.map(y=>({label:`${y.season} ${y.team}`,stat:y.stat}));if(st.lkCareer)rows.push({label:"CAREER",stat:st.lkCareer});lkBody=mkT(lkC,rows)}
    else if(st.lkLoading.career)lkBody=`<div class="loading-sm">Loading...</div>`;
  }
  if(st.lkSubTab==="vsTeam"){
    const tO=st.lkTeamList.map(t=>`<option value="${t.id}" ${t.id===st.lkVsTeamId?"selected":""}>${t.abbr} — ${t.name}</option>`).join("");
    let tbl=`<div class="empty">Select a team</div>`;
    if(st.lkLoading.vsTeam)tbl=`<div class="loading-sm">Loading...</div>`;
    else if(st.lkVsTeamStats){const rows=st.lkVsTeamStats.map(t=>({label:st.lkTeamList.find(x=>x.id===t.teamId)?.abbr||t.team,stat:t.stat}));tbl=rows.length?mkT(lkC,rows):`<div class="empty">No data</div>`}
    lkBody=`<div class="lk-section"><select id="vsTeamSel"><option value="">All Teams</option>${tO}</select></div><div style="margin-top:8px">${tbl}</div>`;
  }
  if(st.lkSubTab==="vsPlayer"){
    const sugs=st.lkVsPlayerResults.length?`<div class="suggestions" style="display:block;position:relative;margin:8px 16px">${st.lkVsPlayerResults.map(r=>`<div class="sug-item" onclick="pickVsP(${r.id},'${r.name.replace(/'/g,"\\'")}')"><span class="sug-name">${r.name}</span> <span class="sug-meta">${r.team} · ${r.pos}</span></div>`).join("")}</div>`:"";
    let res=`<div class="empty">Search for a ${st.lkPlayerType==="qb"?"skill player":"quarterback"}</div>`;
    if(st.lkLoading.vsPlayer)res=`<div class="loading-sm">Loading...</div>`;
    else if(st.lkVsPlayerStats){const s=st.lkVsPlayerStats;const bx=st.lkPlayerType==="qb"?[{v:s.era||"—",l:"ERA"},{v:s.inningsPitched||"—",l:"IP"},{v:s.strikeOuts||"—",l:"K"},{v:s.avg||"—",l:"BAA"}]:[{v:s.avg||"—",l:"AVG"},{v:s.homeRuns||"—",l:"HR"},{v:s.atBats||"—",l:"AB"},{v:s.ops||"—",l:"OPS"}];res=`<div style="padding:0 16px"><div class="card"><div class="card-title">${lk.name} vs ${st.lkVsPlayerName}</div><div class="stat-grid" style="margin:0">${bx.map(b=>`<div class="stat-box"><div class="val">${b.v}</div><div class="lbl">${b.l}</div></div>`).join("")}</div></div></div>${mkT(lkC,[{stat:s}])}`}
    else if(st.lkVsPlayerId)res=`<div class="empty">No head-to-head data</div>`;
    lkBody=`<div class="lk-section"><input type="text" id="vsPlayerInput" placeholder="Search ${st.lkPlayerType==="qb"?"skill player":"quarterback"}..."/></div>${sugs}${res}`;
  }
  const lkSugs=st.lkResults.length?`<div class="suggestions" style="display:block">${st.lkResults.map((r,i)=>`<div class="sug-item" onclick="pickLkPlayer(${i})"><div class="sug-name">${r.name}</div><div class="sug-meta">${r.team} · ${r.pos} · #${r.number}</div></div>`).join("")}</div>`:"";
  const profile=lk?`
    <div class="profile"><div class="profile-img"><img src="${lk.img}" onerror="this.style.display='none'"/></div><div class="profile-info"><h2>${lk.name}</h2><p>${lk.team} · ${lk.pos} · #${lk.number} · B:${lk.bats} T:${lk.throws}</p></div></div>
    ${lkSum}
    <div class="sub-tabs">
      <div class="sub-tab ${st.lkSubTab==="career"?"active":""}" onclick="switchLkSub('career')">Career</div>
      <div class="sub-tab ${st.lkSubTab==="vsTeam"?"active":""}" onclick="switchLkSub('vsTeam')">vs Team</div>
      <div class="sub-tab ${st.lkSubTab==="vsPlayer"?"active":""}" onclick="switchLkSub('vsPlayer')">vs Player</div>
    </div>
    ${lkBody}`:`<div class="lookup-empty">Search by player name to begin.</div>`;
  return`
    <div id="pg-lookup" class="page ${activeTab==="lookup"?"active":""}">
      <section class="lookup-search-shell"><div class="lookup-search-inner"><div class="lookup-search-kicker">MLB player database</div><div class="lookup-search-title">Player lookup</div><div class="search-wrap lookup-search-wrap"><input type="search" id="lkSearch" placeholder="Search any active MLB player" value="${esc(st.lkQuery)}" autocomplete="off"/>${lkSugs}</div></div></section>
      ${st.lookupError?`<div class="lookup-warning" role="status">${esc(st.lookupError)}</div>`:""}
      ${profile}
      <div class="timestamp">Data from nflverse · Live</div>
    </div>`;
}

function renderMethodPage(activeTab){
  return `<div id="pg-method" class="page ${activeTab==="method"?"active":""}">
    <div style="padding:16px"><div style="text-align:center;margin-bottom:16px"><div style="font-size:28px;margin-bottom:4px">⚾</div><div style="color:var(--accent);font-weight:800;font-size:var(--t-md)">How This Dashboard Works</div><div style="color:var(--accent-soft);font-size:var(--t-xs);margin-top:4px">Under the hood of the MLB DFS Engine</div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">📡 Data Sources</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6"><div style="margin-bottom:6px"><span style="color:var(--accent);font-weight:700">MLB Stats API</span> — Batter/QB game logs, splits, matchup history, this week's schedule.</div><div style="margin-bottom:6px"><span style="color:var(--accent);font-weight:700">The Odds API</span> — Live spreads, totals, and player props across 13 markets.</div><div style="margin-bottom:6px"><span style="color:var(--accent);font-weight:700">OpenWeather</span> — Venue weather (temp, wind, conditions) for outdoor parks.</div><div><span style="color:var(--accent);font-weight:700">Google Sheets</span> — Central warehouse. Engine writes 14+ tabs; app reads live.</div></div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">⚙️ Calculations</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6"><span style="color:var(--accent);font-weight:700">Rolling Averages</span> L7/L14/L30/Season · <span style="color:var(--accent);font-weight:700">LHP/RHP Splits</span> · <span style="color:var(--accent);font-weight:700">Home/Away Splits</span> · <span style="color:var(--accent);font-weight:700">Season vs Defense</span> · <span style="color:var(--accent);font-weight:700">EV%</span> hit rate vs implied odds · <span style="color:var(--accent);font-weight:700">Line Movement</span> snapshot diffs</div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">Model Picks</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6">A deterministic market-and-form model and Gemini review layer produce a tracked recommendation cohort. Every pick is anchored to a real player, market, and sportsbook line; provenance badges distinguish validated-model selections from AI-reviewed candidates.</div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">Market Edge & Slips</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6">The market-edge signal compares historical hit rates to implied odds as one input. Slips combine that signal with model review and recent form.</div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">Dingers</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6">TD probability board ranked by TD rate, recent usage, and best-book odds. Includes 3-leg TD parlay combos.</div></div>
      <div class="card" style="margin-bottom:10px"><div class="card-title">📖 Abbreviations</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.7">H — Hits · HR — Home Runs · RBI — Runs Batted In · R — Runs · SB — Stolen Bases<br>TB — Total Bases · BB — Walks · SO — Strikeouts · AB — At Bats · AVG — Batting Average<br>1B — Singles · 2B — Doubles · 3B — Triples · HBP — Hit By Pitch<br>OPS — On-Base Plus Slugging · OBP — On-Base Percentage · SLG — Slugging Percentage<br>H+R+RBI — Hits + Runs + RBIs combo<br>IP — Innings Pitched · ER — Earned Runs · ERA — Earned Run Average<br>WHIP — Walks + Hits per Inning Pitched · K/9 — Strikeouts per 9 innings<br>QS — Quality Start (6+ IP, 3 or fewer ER) · W — Win · PC — Pitch Count<br>P_SO — Passing Yards · P_H — Hits Allowed · P_BB — Walks Allowed · P_ER — Earned Runs<br>DK_FP — DraftKings Fantasy Points · UD_FP — Underdog Fantasy Points<br>EV% — Expected Value (hit rate minus implied odds)<br>LHP/RHP — Left/Right-Handed Pitcher<br>vs SP — Season stats against this week's defense<br>SMASH/STRONG/LEAN — AI confidence tiers<br>L7/L14/L30 — Last 7/14/30 game averages · Seas — Season average</div></div>
      <div class="card" style="margin-bottom:10px;border:1px solid var(--border-1)"><div class="card-title">🙏 Credits</div><div style="font-size:var(--t-sm);color:var(--ink-1);line-height:1.6"><div>Built by <span style="color:var(--accent);font-weight:700">Stephen Krolikowski</span></div><div>AI: <span style="color:var(--accent);font-weight:700">Gemini 3.6 Flash</span> · App: <span style="color:var(--accent);font-weight:700">Claude</span> by Anthropic</div><div>Engine + dashboard fixes with <span style="color:var(--accent);font-weight:700">Codex</span> by OpenAI</div><div>Props: <span style="color:var(--accent);font-weight:700">The Odds API</span> · Data: <span style="color:var(--accent);font-weight:700">MLB Stats API</span> · Weather: <span style="color:var(--accent);font-weight:700">OpenWeather</span></div></div></div>
      <div style="text-align:center;color:var(--ink-quiet);font-size:var(--t-xs);padding:8px 0 20px">For entertainment & research purposes only.</div>
    </div>
  </div>`;
}

function renderMobileNavigation(activeTab){
  const items=[
    ["dashboard","dash","Dash"],
    ["picks","picks","Picks"],
    ["leaders","leaders","Leaders"],
    ["entry","entry","Builder"],
    ["lookup","lookup","Lookup"],
    ["stats","stats","Performance"],
    ["method","info","Info"],
  ];
  return`<div class="tab-bar">${items.map(([tab,iconName,label])=>`
    <button class="tab-btn ${activeTab===tab?"active":""}" onclick="switchTab('${tab}')">${icon(iconName)}<span>${label}</span></button>`).join("")}</div>`;
}

function bindRenderedControls(){
  const bindChange=(id,handler)=>{
    const element=document.getElementById(id);
    if(element)element.addEventListener("change",handler);
  };
  bindChange("metricSel",event=>{st.metric=event.target.value;render()});
  bindChange("lineInput",event=>{st.line=event.target.value;render()});
  bindChange("oppFilter",event=>{st.oppFilter=event.target.value;render()});
  bindChange("vsTeamSel",event=>{st.lkVsTeamId=event.target.value?parseInt(event.target.value):null;fetchLkVsTeam(st.lkPlayer.id,st.lkVsTeamId)});
  bindChange("propsTeamSelect",event=>setPropsTeam(event.target.value));
  bindChange("propsSortSelect",event=>setPropsSort(event.target.value));
  bindChange("propsMinHitSelect",event=>setPropsMinHit(event.target.value));
  bindChange("propsMinEdgeSelect",event=>setPropsMinEdge(event.target.value));

  document.getElementById("themeBtn")?.addEventListener("click",toggleTheme);
  document.getElementById("refreshBtn")?.addEventListener("click",loadAllData);

  const lookupSearch=document.getElementById("lkSearch");
  if(lookupSearch)lookupSearch.addEventListener("input",event=>{
    st.lkQuery=event.target.value;
    clearTimeout(window._lkT);
    window._lkT=setTimeout(()=>searchLkPlayers(event.target.value),300);
  });
  const versusPlayer=document.getElementById("vsPlayerInput");
  if(versusPlayer)versusPlayer.addEventListener("input",event=>{
    clearTimeout(window._vpT);
    window._vpT=setTimeout(()=>searchVsP(event.target.value),300);
  });
  const propsSearch=document.getElementById("propsSearchInput");
  if(propsSearch)propsSearch.addEventListener("input",event=>{st.propsSearch=event.target.value;render()});
}

function renderDashboardPage(){
  const isP=st.mode==="qb";
  const curMetrics=isP?P_METRICS:METRICS;
  const {player,metric,line,activeTab,oppFilter}=st;
  const curTonight=isP?st.pTonight:st.tonight;
  const curLogs=isP?st.pGameLogs:st.gameLogs;
  const curSplits=isP?st.pSplits:st.splits;
  const lineNum=parseFloat(line)||0;

  const pT=getTonightPlayerRow(player,isP)||{};
  const pHasLogs=hasLogs(player,isP);
  const allLogs=getPlayerLogs(player,isP);
  const last10=[...allLogs].reverse().slice(-10);
  const most=allLogs[0]||{};
  const pPick=getPick(player);
  const pickMatchesMetric=pPick&&propToLogCol(pPick.prop_type)===metric;
  const analysisLean=pickMatchesMetric?normalizeLeanText(pPick.lean):(isP&&(metric==="ER"||metric==="BB")?"UNDER":"OVER");

  const seasAvg=getRollingVal(most,"Seas_",metric);
  const midAvg=isP?getRollingVal(most,"L7_",metric):getRollingVal(most,"L30_",metric);
  const shortAvg=isP?getRollingVal(most,"L3_",metric):getRollingVal(most,"L7_",metric);
  const lastGame=getMetricVal(most,metric);
  const midLbl=isP?"L7":"L30",shortLbl=isP?"L3":"L7";

  const hL5=lineNum?allLogs.slice(0,5).filter(g=>clearsPropLine(getMetricVal(g,metric),lineNum,analysisLean)).length:null;
  const hL10=lineNum?allLogs.slice(0,10).filter(g=>clearsPropLine(getMetricVal(g,metric),lineNum,analysisLean)).length:null;
  const hSeas=lineNum?allLogs.filter(g=>clearsPropLine(getMetricVal(g,metric),lineNum,analysisLean)).length:null;
  const sRate=hSeas!==null&&allLogs.length>0?hSeas/allLogs.length:null;
  const maxLog=Math.max(...last10.map(g=>getMetricVal(g,metric)),lineNum||0,1);

  const metricOpts=curMetrics.map(m=>`<option value="${m}" ${m===metric?"selected":""}>${m}</option>`).join("");
  const bars=last10.map(g=>{const v=getMetricVal(g,metric);const h=Math.max(4,(v/maxLog)*80);return`<div class="bar-wrap"><div class="bar-val">${v}</div><div class="bar" style="height:${h}px;background:${barColor(v,lineNum,analysisLean)}"></div><div class="bar-date">${(g.game_date||"").slice(5)}</div><div class="bar-date" style="color:var(--ink-muted);margin-top:0">${g.opp_abbr?(g.home_away==="Home"?"vs":"@")+g.opp_abbr:""}</div></div>`}).join("");
  const avgs=[{l:"Season",v:seasAvg},{l:midLbl,v:midAvg},{l:shortLbl,v:shortAvg},{l:"Last",v:lastGame}].map(a=>`<div class="avg-card" style="border:1px solid ${lineNum&&clearsPropLine(a.v,lineNum,analysisLean)?"var(--over-line)":lineNum?"color-mix(in srgb, var(--under) 20%, transparent)":"var(--border-1)"}"><div class="avg-label">${a.l}</div><div class="avg-val" style="color:${avgColor(a.v,lineNum,analysisLean)}">${a.v.toFixed(2)}</div></div>`).join("");

  const sT={};let statStrip="";
  if(isP){
    ["IP","SO","ER","H","HR","BB","W","L","PC","R"].forEach(s=>{sT[s]=allLogs.reduce((a,g)=>a+toNum(g[s]),0)});
    sT.UD_FP=allLogs.reduce((a,g)=>a+toNum(g.UD_FP),0).toFixed(1);
    const outs=allLogs.reduce((a,g)=>a+Math.round(toNum(g.IP)*3),0);
    const rIP=outs/3;sT.IP=outsToIPStr(outs);
    sT.ERA=rIP>0?((sT.ER*9)/rIP).toFixed(2):"0.00";
    sT.WHIP=rIP>0?(((sT.H||0)+(sT.BB||0))/rIP).toFixed(2):"0.00";
    sT.K9=rIP>0?((sT.SO*9)/rIP).toFixed(1):"0.0";
    statStrip=["W","L","ERA","WHIP","SO","K9","IP","UD_FP"].map(s=>`<div class="stat-item"><div class="stat-label">${s}</div><div class="stat-val">${sT[s]}</div></div>`).join("");
  }else{
    ["H","HR","RBI","R","SB","BB","TB","SO","AB"].forEach(s=>{sT[s]=allLogs.reduce((a,g)=>a+toNum(g[s]),0)});
    sT.AVG=sT.AB>0?(sT.H/sT.AB).toFixed(3):".000";
    sT.UD_FP=allLogs.reduce((a,g)=>a+toNum(g.UD_FP),0).toFixed(1);
    statStrip=["H","HR","RBI","R","SB","BB","TB","UD_FP","AVG"].map(s=>`<div class="stat-item"><div class="stat-label">${s}</div><div class="stat-val">${s==="AVG"?sT.AVG:s==="UD_FP"?sT.UD_FP:sT[s]}</div></div>`).join("");
  }

  const oppP=pT.opp_pitcher_name||"TBD",oppH=pT.opp_pitcher_hand||"?";
  const vsAvg=toNum(pT.vs_OPP_AVG),vsOps=toNum(pT.vs_OPP_OPS),vsHr=toNum(pT.vs_OPP_HR),vsSo=toNum(pT.vs_OPP_SO);
  const venue=pT.venue_tonight||"";
  const wx=st.weather.find(w=>w.venue_name===venue)||{};

  const sp=curSplits.find(s=>s.player_name===player)||{};
  const hV=COMBO_STATS[metric]?COMBO_STATS[metric].reduce((s,k)=>s+toNum(sp[`${k}_Home`]),0):toNum(sp[`${metric}_Home`]);
  const aV=COMBO_STATS[metric]?COMBO_STATS[metric].reduce((s,k)=>s+toNum(sp[`${k}_Away`]),0):toNum(sp[`${metric}_Away`]);
  const hGames=toNum(sp.Home_GAMES)||toNum(sp['Home_GAMES']);
  const aGames=toNum(sp.Away_GAMES)||toNum(sp['Away_GAMES']);
  const hTotal=hGames>0?Math.round(hV*hGames):0;
  const aTotal=aGames>0?Math.round(aV*aGames):0;
  let haBars=`<div class="no-data">No data</div>`;
  if(hV>0||aV>0){const mx=Math.max(hV,aV,.1);haBars=[{l:"Home",v:hV,t:hTotal,g:hGames,c:"#8b5cf6"},{l:"Away",v:aV,t:aTotal,g:aGames,c:"#06b6d4"}].map(b=>`<div class="mini-bar-wrap"><div class="mini-bar" style="height:${Math.max(4,(b.v/mx)*60)}px;background:${b.c}"></div><div class="mini-bar-label">${b.l}</div><div class="mini-bar-val">${b.v.toFixed(2)}/g</div>${b.g?`<div class="mini-bar-val" style="color:var(--accent);font-size:var(--t-xs)">${b.t} in ${b.g}G</div>`:""}</div>`).join("")}

  const lastUp=most.LAST_UPDATED||pT.LAST_UPDATED||"—";
  const earlyBanner=!pHasLogs&&player?`<div class="early-banner"><div class="msg">Early Season — No Game Logs Yet</div><div class="sub">${esc(player)} is on the active roster. Matchup info, props, and Lookup are available.</div></div>`:"";

  const pProps=getProps(player);
  let propsHTML="";
  if(pProps.length>0){propsHTML=`<div class="analysis-market-list">${pProps.map(p=>`<div class="analysis-market-row"><div class="analysis-market-name">${esc(propTypeLabel(p.METRIC))}</div><div class="analysis-market-line">${esc(p.DK_LINE)}</div><div class="analysis-market-odds"><span class="prop-over">O ${fmtOdds(p.OVER_ODDS)}</span><br><span class="prop-under">U ${fmtOdds(p.UNDER_ODDS)}</span></div><div class="analysis-market-best">${renderPropBestBookBlock(p)}</div></div>`).join("")}</div>`}
  let pickBanner="";
  if(pPick){
    const c=pPick.confidence||"",cls=c==="SMASH"?"smash":c==="STRONG"?"strong":"lean";
    const pInjCtx=(pPick.injury_context||"").toString();
    const pHasRisk=pInjCtx.toUpperCase().startsWith("LINEUP RISK");
    const pRiskHTML=pHasRisk?`<div class="lineup-risk-badge">${icon('warn')}LINEUP RISK</div><div class="lineup-risk-text">${esc(pInjCtx)}</div>`:"";
    const decisionLean=normalizeLeanText(pPick.lean),decisionClass=decisionLean==="UNDER"?"under":"over";
    pickBanner=`<div class="analysis-decision ${cls}${pHasRisk?" analysis-decision-risk":""}"><div class="analysis-decision-top"><div><div class="analysis-eyebrow">Model recommendation</div><div class="analysis-decision-call ${decisionClass}">${esc(decisionLean)} ${esc(pPick.line||"—")}</div><div class="analysis-decision-market">${esc(propTypeLabel(pPick.prop_type))}</div></div><div class="analysis-decision-tier ${cls}">${esc(c||"LEAN")}</div></div>${pPick.rationale?`<div class="analysis-decision-reason">${esc(pPick.rationale)}</div>`:""}${pRiskHTML}</div>`;
  }
  const modelScoreValue=(row,key)=>{
    const raw=rowField(row,key);
    if(raw===null||raw===undefined||raw==="")return null;
    const value=Number(raw);
    return Number.isFinite(value)?value:null;
  };
  let modelContext=null;
  if(isP&&metric==="SO"){
    modelContext={
      base:modelScoreValue(pT,"P_SO_PLAYER_SCORE"),
      adjustment:modelScoreValue(pT,"P_SO_OPP_ADJ"),
      final:modelScoreValue(pT,"P_SO_EDGE_SCORE"),
      detail:`Opponent offense adjustment for ${pT.opp_abbr_tonight||"this week's matchup"}`
    };
  }else if(isP&&metric==="ER"){
    modelContext={
      base:modelScoreValue(pT,"P_ER_PLAYER_RISK_SCORE"),
      adjustment:modelScoreValue(pT,"P_ER_OPP_ADJ"),
      final:modelScoreValue(pT,"P_ER_RISK_SCORE"),
      detail:`Opponent scoring-risk adjustment for ${pT.opp_abbr_tonight||"this week's matchup"}`
    };
  }else if(!isP&&metric==="H"){
    modelContext={
      base:modelScoreValue(pT,"H_PLAYER_SCORE"),
      adjustment:modelScoreValue(pT,"H_OPP_ADJ"),
      final:modelScoreValue(pT,"H_EDGE_SCORE"),
      detail:`Opposing starter adjustment for ${oppP}`
    };
  }else if(!isP&&["HR","TB"].includes(metric)){
    modelContext={
      base:modelScoreValue(pT,"POWER_PLAYER_SCORE"),
      adjustment:modelScoreValue(pT,"POWER_OPP_ADJ"),
      final:modelScoreValue(pT,"POWER_EDGE_SCORE"),
      detail:`Opposing starter power adjustment for ${oppP}`
    };
  }
  if(modelContext&&[modelContext.base,modelContext.adjustment,modelContext.final].some(value=>value===null)){
    modelContext=null;
  }
  const modelContextHTML=modelContext?(()=>{
    const adjustment=modelContext.adjustment;
    const grade=adjustment>=2
      ?{label:"Favorable",className:"favorable"}
      :adjustment<=-2
        ?{label:"Tough",className:"tough"}
        :{label:"Neutral",className:"neutral"};
    const adjustmentText=`${adjustment>0?"+":""}${adjustment.toFixed(1)}`;
    const adjustmentClass=adjustment>0?"pos":adjustment<0?"neg":"";
    return `<section class="analysis-rail-section"><div class="analysis-rail-title">Model context</div><div class="model-context-head"><span class="matchup-grade ${grade.className}">${grade.label} matchup</span><span class="model-context-final">${modelContext.final.toFixed(1)}</span></div><div class="analysis-data-row"><span>Player baseline</span><strong>${modelContext.base.toFixed(1)}</strong></div><div class="analysis-data-row"><span>Opponent adjustment</span><strong class="model-context-adj ${adjustmentClass}">${adjustmentText}</strong></div><div class="analysis-data-row"><span>Final score</span><strong>${modelContext.final.toFixed(1)}</strong></div><div class="model-context-note">${esc(modelContext.detail)}</div></section>`;
  })():"";
  const vsp=getVsSP(player);
  const matchupAnalysisHTML=isP
    ?`<div class="analysis-rail-heading">${esc(pT.team_abbr||"")} vs ${esc(pT.opp_abbr_tonight||"—")}</div><div class="analysis-rail-sub">${esc(pT.home_away_tonight||"—")} · ${esc(pT.venue_tonight||"—")}</div>`
    :`<div class="analysis-rail-heading">${esc(pT.team_abbr||"")} vs ${esc(oppP)}</div><div class="analysis-rail-sub">${esc(pT.opp_abbr_tonight||"—")} · ${esc(oppH)}HP · ${esc(venue||"Venue TBD")}</div>${vsp&&toNum(vsp.AB)?`<div style="margin-top:9px"><div class="analysis-data-row"><span>Career matchup</span><strong>${vsp.H||0}-for-${vsp.AB||0}</strong></div><div class="analysis-data-row"><span>Average</span><strong>${vsp.AVG||"—"}</strong></div><div class="analysis-data-row"><span>Home runs</span><strong>${vsp.HR||0}</strong></div></div>`:""}`;
  const opponentRanking=getTeamRanking(pT.opp_abbr_tonight);
  const opponentProfileHTML=opponentRanking?(isP
    ?`<div class="analysis-rail-heading">${esc(rowField(opponentRanking,"TEAM","TEAM_ABBR")||pT.opp_abbr_tonight)} offense</div><div class="analysis-rail-sub">Season-to-date MLB team rates</div><div style="margin-top:8px"><div class="analysis-data-row"><span>Strikeout rate</span><strong>${teamRankValue(opponentRanking,"OFF_K_PCT","OFF_K_PCT_MOST_RANK",{digits:1,suffix:"%",direction:"most"})}</strong></div><div class="analysis-data-row"><span>OPS</span><strong>${teamRankValue(opponentRanking,"OFF_OPS","OFF_OPS_BEST_RANK",{digits:3,direction:"highest"})}</strong></div><div class="analysis-data-row"><span>Runs</span><strong>${teamRankValue(opponentRanking,"OFF_RUNS_PER_GAME","OFF_RUNS_MOST_RANK",{digits:2,suffix:"/game",direction:"most"})}</strong></div><div class="analysis-data-row"><span>Home runs</span><strong>${teamRankValue(opponentRanking,"OFF_HR_PER_GAME","OFF_HR_MOST_RANK",{digits:2,suffix:"/game",direction:"most"})}</strong></div></div>`
    :`<div class="analysis-rail-heading">${esc(rowField(opponentRanking,"TEAM","TEAM_ABBR")||pT.opp_abbr_tonight)} pitching</div><div class="analysis-rail-sub">Season-to-date MLB staff rates</div><div style="margin-top:8px"><div class="analysis-data-row"><span>Home runs allowed</span><strong>${teamRankValue(opponentRanking,"PIT_HR9","PIT_HR9_MOST_RANK",{digits:2,suffix:" HR/9",direction:"most"})}</strong></div><div class="analysis-data-row"><span>Runs allowed</span><strong>${teamRankValue(opponentRanking,"PIT_RUNS_ALLOWED_PER_GAME","PIT_RUNS_ALLOWED_MOST_RANK",{digits:2,suffix:"/game",direction:"most"})}</strong></div><div class="analysis-data-row"><span>ERA</span><strong>${teamRankValue(opponentRanking,"PIT_ERA","PIT_ERA_BEST_RANK",{digits:2,direction:"best"})}</strong></div><div class="analysis-data-row"><span>WHIP</span><strong>${teamRankValue(opponentRanking,"PIT_WHIP","PIT_WHIP_BEST_RANK",{digits:2,direction:"best"})}</strong></div></div>`):"";
  const hitRateAnalysisHTML=lineNum&&pHasLogs?`<div class="analysis-data-row"><span>L5</span><strong>${hL5}/5</strong></div><div class="analysis-data-row"><span>L10</span><strong>${hL10}/10</strong></div><div class="analysis-data-row"><span>Season</span><strong>${hSeas}/${allLogs.length} · ${sRate!==null?(sRate*100).toFixed(0):"—"}%</strong></div>`:"";
  const splitAnalysisHTML=isP
    ?`<div class="analysis-data-row"><span>ERA</span><strong>${sT.ERA||"—"}</strong></div><div class="analysis-data-row"><span>WHIP</span><strong>${sT.WHIP||"—"}</strong></div><div class="analysis-data-row"><span>K/9</span><strong>${sT.K9||"—"}</strong></div>`
    :`<div class="analysis-data-row"><span>vs ${esc(oppH)}HP AVG</span><strong>${vsAvg?vsAvg.toFixed(3):"—"}</strong></div><div class="analysis-data-row"><span>vs ${esc(oppH)}HP OPS</span><strong>${vsOps?vsOps.toFixed(3):"—"}</strong></div><div class="analysis-data-row"><span>HR / SO</span><strong>${vsHr||0} / ${vsSo||0}</strong></div>`;
  const weatherAnalysisHTML=wx.temp_f?`<div class="analysis-data-row"><span>Temperature</span><strong>${wx.temp_f}°F</strong></div><div class="analysis-data-row"><span>Wind</span><strong>${wx.wind_mph} mph ${esc(wx.wind_dir||"")}</strong></div><div class="analysis-data-row"><span>Conditions</span><strong>${esc(wx.description||"—")}</strong></div>${wx.is_dome===true||wx.is_dome==="TRUE"||wx.is_dome==="True"?`<div class="analysis-data-row"><span>Venue</span><strong>Dome</strong></div>`:""}`:"";

  const opps=[...new Set(allLogs.map(g=>g.opp_abbr).filter(Boolean))].sort();
  const oppOpts=`<option value="">All Opponents</option>`+opps.map(o=>`<option value="${o}" ${oppFilter===o?"selected":""}>${o}</option>`).join("");
  const fLogs=oppFilter?allLogs.filter(g=>g.opp_abbr===oppFilter):allLogs;
  const visibleLogs=st.showFullLog?fLogs:fLogs.slice(0,10);
  const logCols=isP?["IP","H","ER","HR","SO","BB","PC","W","L","UD_FP"]:["AB","H","HR","RBI","R","SB","BB","SO","TB","UD_FP"];
  const tHeaders=logCols.map(c=>`<th class="${c===metric?"hl":""}">${c}</th>`).join("");
  const tRows=visibleLogs.map(g=>{const cells=logCols.map(c=>{const v=toNum(g[c]);let cls=c===metric?"hl":"";if(c===metric&&lineNum){cls=v>lineNum?"hit":v===lineNum?"push":"miss"}return`<td class="${cls}">${c==="UD_FP"?v.toFixed(1):v}</td>`}).join("");return`<tr><td>${(g.game_date||"").slice(5)}</td><td>${g.opp_abbr||"—"}</td><td>${g.home_away||"—"}</td>${cells}</tr>`}).join("");

  return `<div id="pg-dash" class="page ${activeTab==="dashboard"?"active":""}">
    ${player?`<div class="analysis-shell">
      ${earlyBanner}
      <header class="analysis-hero">
        <div class="analysis-hero-top"><div><div class="analysis-eyebrow">${isP?"Pitcher analysis":"Batter analysis"}</div><div class="analysis-player">${esc(player)}</div><div class="analysis-context">${esc(pT.team_abbr||"Team TBD")} · ${esc(pT.home_away_tonight||"—")} vs ${esc(pT.opp_abbr_tonight||"—")} · ${esc(venue||pT.venue_tonight||"Venue TBD")}${gameStartTimeForTeams(pT.team_abbr,pT.opp_abbr_tonight)?` · ${esc(gameStartTimeForTeams(pT.team_abbr,pT.opp_abbr_tonight))}`:""}</div></div><div class="analysis-focus"><div class="analysis-focus-value">${esc(metric)}</div><div class="analysis-focus-label">${lineNum?`Prop line ${lineNum}`:"Selected metric"}</div></div></div>
        ${pHasLogs?`<div class="analysis-kpis"><div class="analysis-kpi"><div class="analysis-kpi-value" style="color:${avgColor(seasAvg,lineNum,analysisLean)}">${seasAvg.toFixed(2)}</div><div class="analysis-kpi-label">Season</div></div><div class="analysis-kpi"><div class="analysis-kpi-value" style="color:${avgColor(midAvg,lineNum,analysisLean)}">${midAvg.toFixed(2)}</div><div class="analysis-kpi-label">${midLbl}</div></div><div class="analysis-kpi"><div class="analysis-kpi-value" style="color:${avgColor(shortAvg,lineNum,analysisLean)}">${shortAvg.toFixed(2)}</div><div class="analysis-kpi-label">${shortLbl}</div></div><div class="analysis-kpi"><div class="analysis-kpi-value" style="color:${avgColor(lastGame,lineNum,analysisLean)}">${lastGame.toFixed(2)}</div><div class="analysis-kpi-label">Last game</div></div></div><div class="analysis-season-strip">${statStrip}</div>`:""}
      </header>
      <div class="analysis-layout">
        <main class="analysis-primary">
          ${pHasLogs?`<section class="analysis-section"><div class="analysis-section-head"><div class="analysis-section-title">Last 10 · ${esc(propTypeLabel(metric))}</div><div class="analysis-section-meta">${last10.length} games · green marks ${analysisLean.toLowerCase()} wins</div></div><div class="analysis-chart"><div class="bar-chart">${bars}</div>${lineNum?`<div class="line-indicator">Reference line ${lineNum}</div>`:""}</div></section>`:""}
          ${pickBanner?`<section class="analysis-section"><div class="analysis-section-head"><div class="analysis-section-title">Decision</div><div class="analysis-section-meta">Model-ranked recommendation</div></div>${pickBanner}</section>`:""}
          ${propsHTML?`<section class="analysis-section"><div class="analysis-section-head"><div class="analysis-section-title">Sportsbook markets</div><div class="analysis-section-meta">Live comparison by book</div></div>${propsHTML}</section>`:""}
        </main>
        <aside class="analysis-rail">
          <section class="analysis-rail-section"><div class="analysis-rail-title">This week's matchup</div>${matchupAnalysisHTML}</section>
          ${modelContextHTML}
          ${opponentProfileHTML?`<section class="analysis-rail-section"><div class="analysis-rail-title">Opponent profile</div>${opponentProfileHTML}</section>`:""}
          ${hitRateAnalysisHTML?`<section class="analysis-rail-section"><div class="analysis-rail-title">Hit rates · ${esc(metric)} ${lineNum?`${analysisLean.toLowerCase()} ${lineNum}`:""}</div>${hitRateAnalysisHTML}</section>`:""}
          ${pHasLogs?`<section class="analysis-rail-section"><div class="analysis-rail-title">${isP?"Season rates":`Handedness split · ${esc(oppH)}HP`}</div>${splitAnalysisHTML}</section><section class="analysis-rail-section"><div class="analysis-rail-title">Home / away</div><div class="mini-bars-container">${haBars}</div></section>`:""}
          ${weatherAnalysisHTML?`<section class="analysis-rail-section"><div class="analysis-rail-title">Weather</div>${weatherAnalysisHTML}</section>`:""}
        </aside>
      </div>
      ${pHasLogs?`<section class="analysis-game-log"><div class="analysis-section-head"><div><div class="analysis-section-title">Game log · ${st.showFullLog?"Full history":"Recent 10"}</div><div class="analysis-section-meta">${esc(metric)} results · ${fLogs.length} matching game${fLogs.length===1?"":"s"} loaded</div></div></div><div class="log-controls"><label for="oppFilter">Opponent</label><select id="oppFilter">${oppOpts}</select>${fLogs.length>10?`<button class="log-expand-btn" onclick="toggleFullLog()">${st.showFullLog?"Show recent 10":`Show full history (${fLogs.length})`}</button>`:""}</div><div class="log-table-wrap"><table><thead><tr><th>DATE</th><th>OPP</th><th>H/A</th>${tHeaders}</tr></thead><tbody>${tRows}</tbody></table></div></section>`:""}
    </div>`:`<div class="empty" style="padding:70px 20px">Select a player above to open the analysis workspace.</div>`}
    <div class="timestamp">As of: ${fmtNowEastern()} · Last Refreshed: ${lastUp}</div>
    <div class="timestamp" style="color:var(--border-1);font-size:var(--t-xs);padding-top:0">Made by S. Krolikowski w/ Claude · 2026</div>
  </div>`;
}

function render(){
  var picksHTML="";
  const focus=saveFocus();
  const app=document.getElementById("app");
  if(st.loading){app.innerHTML=`<div class="diamond-loader" role="status" aria-live="polite"><div class="diamond-loader-mark" aria-hidden="true"><div class="diamond-loader-field"></div><span class="diamond-loader-base home"></span><span class="diamond-loader-base first"></span><span class="diamond-loader-base second"></span><span class="diamond-loader-base third"></span><span class="diamond-loader-ball"></span></div><div class="diamond-loader-title">Loading the slate</div><div class="diamond-loader-copy">Scheming up the next Philly Special…</div></div>`;return}
  if(st.error){app.innerHTML=`<div class="error">⚠️ ${st.error}<br><br><span style="color:var(--ink-muted);font-size:var(--t-sm)">Make sure your Google Sheet is set to "Anyone with the link can view"</span></div>`;return}

  const isP=st.mode==="qb";
  const curMetrics=isP?P_METRICS:METRICS;
  const {player,metric,activeTab}=st;
  const curTonight=isP?st.pTonight:st.tonight;
  const metricOpts=curMetrics.map(m=>`<option value="${m}" ${m===metric?"selected":""}>${m}</option>`).join("");

  // === PICKS TAB ===
  const convergenceHTML=renderConvergenceHTML();
  picksHTML="";
  if(st.picksView==="shortlist"){
    picksHTML=renderShortlistPicksView();
  }else if(st.picksView==="bets"){
    picksHTML=renderBetsBoardView(convergenceHTML);
  }else if(st.picksView==="slips"){
    picksHTML=renderSlipsBoardView(convergenceHTML);
  }else if(st.picksView==="picks"){
    picksHTML=renderModelPicksView(convergenceHTML);
  }else if(st.picksView==="dingers"){
    picksHTML=renderDingerBoardView(convergenceHTML);
  }else if(st.picksView==="ks"){
    picksHTML=renderKsBoardView(convergenceHTML);
  }else if(st.picksView==="streaks"){
    picksHTML=renderStreaksBoardView(convergenceHTML);
  }else if(st.picksView==="draft"){
    picksHTML=renderDraftBoardView(convergenceHTML);
  }else{
    picksHTML=renderPropExplorerView();
  }

  const showCtrl=activeTab==="dashboard";
  app.innerHTML=`
  ${renderAppHeader({activeTab,showCtrl,player,metricOpts,curTonight})}
  ${renderDataWarnings()}

  ${renderDashboardPage()}

  ${renderPicksPage(activeTab,picksHTML)}

  <div id="pg-stats" class="page ${activeTab==="stats"?"active":""}">${renderStatsView()}</div>
  <div id="pg-leaders" class="page ${activeTab==="leaders"?"active":""}">${renderLeadersView()}</div>
  <div id="pg-entry" class="page ${activeTab==="entry"?"active":""}">${renderGameEntryView()}</div>
  <div id="pg-bestball" class="page ${activeTab==="bestball"?"active":""}">${renderBestBallView()}</div>

  ${renderLookupPage(activeTab)}

  ${renderMethodPage(activeTab)}

  ${renderMobileNavigation(activeTab)}`;

  bindRenderedControls();
  applyTheme();
  restoreFocus(focus);
}

async function searchLkPlayers(q){
  st.lkQuery=q;st.lookupError="";
  if(q.length<2){st.lkResults=[];render();return}
  try{const d=await mlbFetch(`${MLB_API}/people/search?names=${encodeURIComponent(q)}&sportId=1&hydrate=currentTeam&limit=10`);st.lkResults=(d.people||[]).filter(p=>p.active).map(p=>({id:p.id,name:p.fullName,team:p.currentTeam?.abbreviation||"",pos:p.primaryPosition?.abbreviation||"",number:p.primaryNumber||"",bats:p.batSide?.code||"",throws:p.pitchHand?.code||"",img:`https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_120,q_auto:best/v1/people/${p.id}/headshot/67/current`}));render()}catch(e){st.lkResults=[];st.lookupError="Player search is temporarily unavailable.";reportNonFatal("Lookup player search failed.",e);render()}
}
function pickLkPlayer(i){
  const p=st.lkResults[i];st.lkPlayer=p;st.lkQuery=p.name;st.lkResults=[];st.lkSubTab="career";
  st.lkCareer=null;st.lkYby=null;st.lkVsTeamStats=null;st.lkVsPlayerStats=null;st.lkVsPlayerId=null;st.lkVsPlayerName="";st.lkVsTeamId=null;
  st.lkPlayerType=p.pos==="QB"?"qb":"skill";
  const isP=["P","TWP"].includes(p.pos);
  const src=isP?st.pTonight:st.tonight;
  const match=src.find(t=>normalizePlayerName(t.player_name)===normalizePlayerName(p.name));
  if(match){st.player=match.player_name;if(isP&&st.mode!=="qb"){st.mode="qb";st.metric="PASS_YDS"}if(!isP&&st.mode!=="skill"){st.mode="skill";st.metric="H"}}
  render();fetchLkCareer(p.id);
}
async function fetchLkCareer(id){
  st.lkLoading.career=true;st.lookupError="";render();
  try{const g=st.lkPlayerType==="qb"?"pitching":"hitting";const[cr,yby]=await Promise.all([mlbFetch(`${MLB_API}/people/${id}/stats?stats=career&group=${g}`),mlbFetch(`${MLB_API}/people/${id}/stats?stats=yearByYear&group=${g}&sportId=1`)]);st.lkCareer=(cr.stats||[])[0]?.splits?.[0]?.stat||null;st.lkYby=((yby.stats||[])[0]?.splits||[]).filter(s=>s.sport?.id===1).map(s=>({season:s.season,team:s.team?.abbreviation||"",stat:s.stat}))}catch(e){st.lkCareer=null;st.lkYby=null;st.lookupError="Career stats are temporarily unavailable.";reportNonFatal("Lookup career request failed.",e)}
  st.lkLoading.career=false;render();
}
async function fetchLkVsTeam(id,teamId){
  st.lkLoading.vsTeam=true;st.lookupError="";render();
  try{
    const g=st.lkPlayerType==="qb"?"pitching":"hitting";
    if(teamId){
      const d=await mlbFetch(`${MLB_API}/people/${id}/stats?stats=vsTeam&group=${g}&opposingTeamId=${teamId}&sportId=1`);
      const sp=(d.stats||[])[0]?.splits||[];
      const tm=st.lkTeamList.find(t=>t.id===teamId);
      st.lkVsTeamStats=sp.length?[{teamId,team:tm?.abbr||"",stat:sp.length===1?sp[0].stat:combSplits(sp)}]:[];
    }else{
      const results=[];
      const failedTeams=[];
      for(let i=0;i<st.lkTeamList.length;i+=10){
        const batch=st.lkTeamList.slice(i,i+10);
        const requests=batch.map(async tm=>{
          try{
            const d=await mlbFetch(`${MLB_API}/people/${id}/stats?stats=vsTeam&group=${g}&opposingTeamId=${tm.id}&sportId=1`);
            const sp=(d.stats||[])[0]?.splits||[];
            if(sp.length)return{teamId:tm.id,team:tm.abbr,stat:sp.length===1?sp[0].stat:combSplits(sp)};
          }catch(error){failedTeams.push(tm.abbr||String(tm.id))}
          return null;
        });
        results.push(...(await Promise.all(requests)).filter(Boolean));
        if(i+10<st.lkTeamList.length)await new Promise(resolve=>setTimeout(resolve,500));
      }
      if(failedTeams.length)console.warn(`⚠️ Lookup vs-team stats unavailable for ${failedTeams.length} team(s): ${failedTeams.join(", ")}`);
      st.lkVsTeamStats=results;
    }
    st.lkVsTeamStats.sort((a,b)=>(parseInt(b.stat?.gamesPlayed)||0)-(parseInt(a.stat?.gamesPlayed)||0));
  }catch(e){
    st.lkVsTeamStats=[];
    st.lookupError="Team matchup stats are temporarily unavailable.";
    reportNonFatal("Lookup vs-team request failed.",e);
  }
  st.lkLoading.vsTeam=false;render();
}
function combSplits(splits){
  const t={};const keys=["gamesPlayed","atBats","hits","doubles","triples","homeRuns","rbi","runs","stolenBases","baseOnBalls","strikeOuts","totalBases","plateAppearances","hitByPitch","sacFlies","wins","losses","gamesStarted","inningsPitched"];
  const stats=splits.map(s=>s.stat);for(const k of keys){const s=stats.reduce((a,s)=>a+(parseFloat(s[k])||0),0);if(s>0)t[k]=s}
  if(t.atBats>0){t.avg=(t.hits/t.atBats).toFixed(3);t.slg=((t.totalBases||0)/t.atBats).toFixed(3)}
  const pa=t.plateAppearances||(t.atBats+(t.baseOnBalls||0)+(t.hitByPitch||0)+(t.sacFlies||0));
  if(pa>0){t.obp=((t.hits+(t.baseOnBalls||0)+(t.hitByPitch||0))/pa).toFixed(3);t.ops=(parseFloat(t.obp||0)+parseFloat(t.slg||0)).toFixed(3)}
  return t;
}
async function searchVsP(q){if(q.length<2){st.lkVsPlayerResults=[];render();return}try{const d=await mlbFetch(`${MLB_API}/people/search?names=${encodeURIComponent(q)}&sportId=1&limit=8`);st.lkVsPlayerResults=(d.people||[]).map(p=>({id:p.id,name:p.fullName,pos:p.primaryPosition?.abbreviation||"",team:p.currentTeam?.abbreviation||""}));render()}catch(e){console.error(e)}}
function pickVsP(id,name){st.lkVsPlayerId=id;st.lkVsPlayerName=name;st.lkVsPlayerResults=[];fetchLkVsPlayer(st.lkPlayer.id,id)}
async function fetchLkVsPlayer(pid,oid){st.lkLoading.vsPlayer=true;st.lkVsPlayerResults=[];st.lookupError="";render();try{const g=st.lkPlayerType==="qb"?"pitching":"hitting";const d=await mlbFetch(`${MLB_API}/people/${pid}/stats?stats=vsPlayer&group=${g}&opposingPlayerId=${oid}`);const sp=(d.stats||[])[0]?.splits||[];st.lkVsPlayerStats=sp.length?sp[0].stat:null}catch(e){st.lkVsPlayerStats=null;st.lookupError="Head-to-head stats are temporarily unavailable.";reportNonFatal("Lookup head-to-head request failed.",e)}st.lkLoading.vsPlayer=false;render()}
function switchLkSub(t){st.lkSubTab=t;if(t==="vsTeam")st.lkVsTeamStats=null;render()}

async function loadTeams(){const yr=new Date().getMonth()>=3?new Date().getFullYear():new Date().getFullYear()-1;try{const d=await mlbFetch(`${MLB_API}/teams?sportId=1&season=${yr}`);st.lkTeamList=(d.teams||[]).map(t=>({id:t.id,name:t.name,abbr:t.abbreviation}))}catch(e){reportNonFatal("MLB team directory unavailable; Lookup team splits may be limited.",e)}}

function loadAllData(){
  st.loading=true;st.error=null;st.dataWarnings=[];st.lookupError="";resetDerived();render();
  Promise.all([
  loadTeams(),
  fetchOptionalSheet("Slate_Skill","The skill-player pool is unavailable."),
  fetchOptionalSheet("Skill_Game_Logs","Recent skill-player history is unavailable."),
  fetchOptionalSheet("Home_Away_Splits"),
  fetchOptionalSheet("Venue_Weather"),
  fetchOptionalSheet("Slate_QB"),
  fetchOptionalSheet("Schedule"),
  fetchOptionalSheet("Starting_QBs","Starting quarterbacks are unavailable."),
  fetchOptionalSheet("QB_Game_Logs","Recent quarterback history is unavailable."),
  fetchOptionalSheet("QB_Home_Away"),
  fetchSheet("Picks_Current")
    .then(rows=>({available:true,rows}))
    .catch(error=>{reportNonFatal("Picks_Current unavailable; using Daily_Picks history fallback.",error,"Current model picks are unavailable; showing the latest history snapshot.");return{available:false,rows:[]}}),
  fetchOptionalSheet("Daily_Picks"),
  fetchOptionalSheet("DK_Player_Props","Sportsbook markets are unavailable."),
  fetchOptionalSheet("All_Books_Props"),
  fetchOptionalSheet("Player_vs_Defense"),
  fetchOptionalSheet("Team_Rankings"),
  fetchOptionalSheet("Projections","Season projections are unavailable."),
  fetchOptionalSheet("Pick_Performance"),
  fetchOptionalSheet("Pick_Performance_Snapshots")
]).then(([_,tonight,logs,splits,weather,pitchers,schedule,pTonight,pLogs,pSplits,currentPickSource,picksHistory,props,allBooksProps,vsSP,teamRankings,projections,pickPerformance,pickPerformanceSnaps])=>{
  resetDerived();
  st.tonight=normalizeKeys(cleanRows(tonight));
  st.gameLogs=normalizeKeys(cleanRows(logs));
  st.splits=normalizeKeys(cleanRows(splits));
  st.weather=normalizeKeys(cleanRows(weather));
  st.pitchers=normalizeKeys(cleanRows(pitchers));
  st.schedule=normalizeKeys(cleanRows(schedule));
  st.pTonight=normalizeKeys(cleanRows(pTonight));
  st.pGameLogs=normalizeKeys(cleanRows(pLogs));
  st.pSplits=normalizeKeys(cleanRows(pSplits));
  const normalizePickRows=rows=>normalizeKeys(cleanRows(rows||[])).map(p=>({
    ...p,
    player: cleanName(rowField(p,"player","PLAYER_NAME")),
    prop_type: normalizePropMetric(rowField(p,"prop_type","METRIC")),
    lean: normalizeLeanText(rowField(p,"lean")),
    confidence: normalizeConfidence(rowField(p,"confidence")),
    DATE: normalizeDate(rowField(p,"DATE")),
    RUN_NUMBER: toNum(rowField(p,"RUN_NUMBER"))
  }));
  const normalizedCurrentPicks=normalizePickRows(currentPickSource.rows);
  st.picksHistory=normalizePickRows(picksHistory);
  st.picks=currentPickSource.available?normalizedCurrentPicks:st.picksHistory;
  console.log(
    `📍 Picks source: ${currentPickSource.available?"Picks_Current":"Daily_Picks fallback"} `+
    `(${st.picks.length} current, ${st.picksHistory.length} history)`
  );
	  st.props=normalizeKeys(cleanRows(props));
	  st.allBooksProps=normalizeKeys(cleanRows(allBooksProps||[]));
	  st.vsSP=normalizeKeys(cleanRows(vsSP));
	  const teamRankingRows=normalizeKeys(cleanRows(teamRankings||[]));
	  const teamRankingKeys=new Set(Object.keys(teamRankingRows[0]||{}).map(canonicalFieldKey));
	  // NFL team aggregates. The MLB baseline checked for off_k_pct/pit_hr9 here,
	  // which no football tab will ever have — it silently zeroed the tab.
	  const hasTeamRankingSchema=['team_abbr','passing_yards','rushing_yards'].every(key=>teamRankingKeys.has(key));
	  st.teamRankings=hasTeamRankingSchema?teamRankingRows:[];
	  if(teamRankingRows.length&&!hasTeamRankingSchema)console.warn('⚠️ Team_Rankings is not populated yet; ignoring GViz fallback data.');
	  st.projections=normalizeKeys(cleanRows(projections||[]));
	  st.pickPerformance=normalizeKeys(cleanRows(pickPerformance||[]));
	  st.pickPerformanceSnaps=normalizeKeys(cleanRows(pickPerformanceSnaps||[]));
	  const DASHBOARD_EXPECTS = {
	    Slate_Skill: ['player_name', 'team_abbr', 'opp_abbr', 'pos',
	                  'targets', 'target_share', 'snap_pct', 'fantasy_points_ppr'],
	    Slate_QB: ['player_name', 'team_abbr', 'opp_abbr',
	               'attempts', 'passing_yards', 'passing_tds'],
	    Picks_Current: ['DATE', 'RUN_NUMBER', 'player', 'prop_type', 'line', 'lean',
	                  'confidence', 'rationale', 'HIT'],
	    Daily_Picks: ['DATE', 'RUN_NUMBER', 'player', 'prop_type', 'line', 'lean',
	                  'confidence', 'rationale', 'HIT'],
	    DK_Player_Props: ['PLAYER_NAME', 'METRIC', 'DK_LINE', 'OVER_ODDS', 'UNDER_ODDS'],
	    All_Books_Props: ['PLAYER_NAME', 'METRIC', 'LINE', 'BOOK', 'OVER_ODDS', 'UNDER_ODDS'],
	    Team_Rankings: ['team_abbr', 'passing_yards', 'rushing_yards'],
	  };
	  const _schemaSources = {
	    Slate_Skill: st.tonight,
	    Picks_Current: normalizedCurrentPicks,
	    Daily_Picks: st.picksHistory,
	    DK_Player_Props: st.props,
	    All_Books_Props: st.allBooksProps,
	    Slate_QB: st.pitchers,
	    Team_Rankings: st.teamRankings,
	  };
	  const _schemaIssues = [];
	  for (const [sheet, expectedCols] of Object.entries(DASHBOARD_EXPECTS)) {
	    const rows = _schemaSources[sheet];
	    if (!rows || !rows.length) continue;
	    const actualCols = new Set(Object.keys(rows[0]));
	    const missing = expectedCols.filter(c => !actualCols.has(c));
	    if (missing.length) _schemaIssues.push(`${sheet}: missing [${missing.join(', ')}]`);
	  }
	  if (_schemaIssues.length) {
	    console.warn('⚠️ SCHEMA DRIFT DETECTED:');
	    _schemaIssues.forEach(i => console.warn('  ' + i));
	  } else {
	    console.log('✅ Dashboard schema audit: all expected columns present');
	  }
	  st.dataVersion+=1;
  syncDraftSlateSelection();
  st.latestPickDate=getLatestPickDate();
  const latestPickRun=getLatestPickRun();
  const latestPicks=st.latestPickDate?st.picks.filter(p=>normalizeDate(rowField(p,"DATE"))===st.latestPickDate&&toNum(rowField(p,"RUN_NUMBER"))===latestPickRun):[];
  st.pickGuard=getPickGuard(st.latestPickDate,latestPicks.length);
  st.loading=false;st.loadedAt=new Date().toLocaleTimeString();

  st.mode="skill";st.metric="REC";
  st.player=firstValidPlayer(st.tonight);

  if(!st.player&&st.pTonight.length>0){
    st.mode="qb";st.metric="PASS_YDS";
    st.player=firstValidPlayer(st.pTonight);
  }

  console.log(`🚀 Dashboard loaded — mode:${st.mode}, player:"${st.player}"`);
  console.log(`   Batters: ${st.tonight.length}, Logs: ${st.gameLogs.length}, Pitchers: ${st.pTonight.length}`);
  console.log(`   Props: ${st.props.length}, Picks: ${st.picks.length}, Weather: ${st.weather.length}`);
  console.log(`   Team rankings: ${st.teamRankings.length}`);
  if(st.pickGuard)console.warn(`⚠️ ${st.pickGuard.text}`);
  if(st.tonight.length>0)console.log(`   Skill player row 0 keys:`,Object.keys(st.tonight[0]).slice(0,8));
  if(st.pTonight.length>0)console.log(`   QB row 0 keys:`,Object.keys(st.pTonight[0]).slice(0,8));
  // JSON.stringify(undefined) returns undefined, not a string, so .slice()
  // throws on an empty slate. Only reachable when no rows loaded at all —
  // which is exactly when you most need the diagnostics to survive.
  if(!st.player){
    if(st.tonight.length)console.error(`❌ NO DEFAULT PLAYER FOUND. Skill player row 0:`,JSON.stringify(st.tonight[0]).slice(0,200));
    else console.error("❌ NO DEFAULT PLAYER FOUND — Slate_Skill returned no rows.");
  }
  if(!st.gameLogs.length)console.warn("⚠️ Skill_Game_Logs unavailable — dashboard loaded without game log history.");
  if(!st.tonight.length)console.warn("⚠️ Slate_Skill unavailable — dashboard loaded without skill-player rows.");
  if(!st.tonight.length&&!st.pTonight.length&&!st.props.length&&!st.picks.length){
    st.error="Could not load NFL dashboard data. Google returned no usable rows for the current dashboard sheets — has the engine run since the tab contract changed?";
  }
  render();
}).catch(err=>{
  console.error("❌ Load failed:",err);
  st.loading=false;
  st.error=err?.message?.startsWith("Sheet load failed:")?`Could not load required NFL sheet: ${err.message.replace("Sheet load failed: ","")}.`:"Could not load NFL dashboard data. A required sheet request failed.";
  render();
});
}
loadAllData();
