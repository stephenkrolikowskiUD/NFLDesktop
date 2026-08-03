# NFLDesktop Build Plan (5 weeks)

## Scope
Full build (parity with MLBDesktop) + new features:
- **Team Selections** — select teams for combo picks
- **Spreads** — surface spread picks alongside moneylines
- Same data pattern: Python engine → Google Sheets → vanilla HTML/JS dashboard

## Data Sources
- **Odds API**: `americanfootball_nfl` for live odds
- **Big Balls Sports Data API**: schedules, team stats, game state, play-by-play
- **OpenWeather API**: stadium conditions
- **Google Sheets**: workbook for dashboard data

## Timeline (5 weeks)

### Week 1 (Aug 2–8): Data Pipeline & Infrastructure
- [ ] Set up Big Balls API integration (schedules, team roster, game state)
- [ ] Set up Odds API for NFL (moneylines, spreads, player props)
- [ ] Create NFLDesktop Google Sheet with base tabs
- [ ] Python engine scaffold: `NFLEnginev1.py` (data pull, minimal picks logic)
- [ ] Deploy initial engine run to Sheets
- First commit: working data pipeline

### Week 2 (Aug 9–15): Dashboard Skeleton
- [ ] Dashboard HTML/CSS/JS scaffold (copy MLBDesktop structure)
- [ ] Load NFL Sheets data into dashboard
- [ ] Build Dashboard tab (matchups, spreads, team info)
- [ ] Build basic navigation
- First visual deploy: dashboard loads data from Sheets

### Week 3 (Aug 16–22): Picks Logic & Team Selections
- [ ] Implement picks generation logic (moneyline + spread picks)
- [ ] Build team selections feature (combo builder for teams)
- [ ] Build Picks tab with multiple sub-views
- [ ] Connect picks to Sheets workflow
- Working picks board with team combos

### Week 4 (Aug 23–29): Remaining Tabs & Polish
- [ ] Leaders tab (team stats, trending)
- [ ] Team Builder tab (spread/moneyline combo builder)
- [ ] Lookup tab (team/player search)
- [ ] Stats/Performance tracking (minimal; scale post-launch)
- [ ] Info/Help tab
- [ ] Style refinement, mobile UX

### Week 5 (Aug 30–Sep 5): Testing & Launch Prep
- [ ] End-to-end QA (all tabs, data flow, edge cases)
- [ ] GitHub Actions setup (engine runs 2×/day during active slates)
- [ ] Grader logic (basic win/loss tracking)
- [ ] GitHub Pages deployment
- [ ] Live with Week 1 kickoff

## Key Design Decisions
- **Team Selections**: new feature, requires clean data model (teams, rosters, spread tiers)
- **Spreads**: layer spreads alongside ML in all pick surfaces
- **No Framework**: vanilla HTML/JS only, reusing MLBDesktop patterns
- **Stateless Picks**: picks generated server-side in engine, displayed client-side

## Known Constraints
- 1,000 req/day free tier on Big Balls (throttle aggressively during live play; pre-build dashboard)
- No official NFL API like statsapi.mlb.com; Big Balls is the best option
- 32 stadiums need hardcoded lat/long for weather lookups

## Success Criteria
- Week 1 slates fully populated
- Moneylines + spreads surfaced
- Team selections working end-to-end
- Pick generation running automatically
- No framework tech debt
