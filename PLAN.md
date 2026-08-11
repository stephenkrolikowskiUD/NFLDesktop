# NFLDesktop Roadmap

_Last updated: 2026-08-11_

## Where We Are
NFL is no longer a greenfield build. The core dashboard, engine, season-long projection layer, and Lookup are all live. The remaining work is the weekly picks + grading loop, which currently has real client-side UI (confidence tiers, calibration) but no backend at all — no pick generation, no grading, no data ever reaches those tabs. That's the one piece standing between here and the Week 1 Launch Bar below.

## Shipped
- ✅ nflverse-first data pipeline (schedule, rosters, weekly stats, snap counts, injuries, depth-chart context)
- ✅ Odds API integration for NFL lines and player props
- ✅ Google Sheets pipeline feeding the dashboard
- ✅ Dashboard shell ported from MLBDesktop with NFL pages wired up
- ✅ Season-long projection model and 7-season backtest
- ✅ Best Ball board live
- ✅ 0.5 PPR / full PPR scoring toggle
- ✅ Queue, drafted, and taken state with persistence
- ✅ Bye-week pressure, team concentration, and QB stack pressure
- ✅ Round-context helper (`best overall`, `take now`, `can wait`)
- ✅ Game Builder foundation with contest-slate filtering
- ✅ Leaders / Picks / Model Performance / Info surfaces online
- ✅ Mobile navigation pass, including Best Ball access on phone
- ✅ Lookup rebuilt on nflverse-native data (projections, game logs, props, team rankings, schedule — no external API calls)

## In Progress
- 🔴 Weekly picks generation + grading — client-side confidence-tier UI (SMASH/STRONG, historical-floor calibration) exists, but there is no engine-side pipeline at all: no Gemini integration, and nothing writes `Picks_Current`/`Daily_Picks`/`Pick_Performance`. This is backend work, not polish.
- 🟡 Best Ball board layout polish and mobile compaction
- 🟡 Game Builder presentation and entry ergonomics
- 🟡 Season-long projection explainer / trust layer

## Current Sprint Priorities
1. **Weekly picks generation + grader loop (backend, not polish)**
   - Wire actual pick generation (Gemini review layer over the market/form model) so `Picks_Current`/`Daily_Picks` have real rows
   - Build the grading loop so `Pick_Performance` gets populated and the existing SMASH/STRONG calibration UI has something to calibrate against
   - Until this exists, the Info page describes this as planned rather than active — keep it that way rather than re-claiming it's live

2. **Best Ball draft helper polish**
   - Tighten layout so the board stays primary
   - Keep queue, round context, and pressure cards useful without wasting space
   - Add clearer ADP / timing signals so we know who to take now versus who can wait

3. **Season-long projection helper**
   - Keep projections trustworthy and explain disagreements vs consensus
   - Surface projection context cleanly in the board and related views
   - Make scoring-source, disagreement, and watchlist context obvious at the top of the board

## Next Up After This Sprint
- ADP-aware draft timing layer
  - Distinguish `best player overall` from `best player you can wait on`
  - Add room-turn / pick-window pressure
- Weekly contest workflow
  - Sharper slate filtering for non-full-slate contests
  - Better handoff between Game Builder and Picks
- Lookup expansion
  - richer team context, matchup context, and role signals
- Grader maturity
  - stronger weekly feedback loop before regular season volume ramps

## Not In Scope Right Now
- Full framework migration
- Fancy infra changes before Week 1
- Cross-sport unification into one app before NFL launch

## Week 1 Launch Bar
By Week 1 kickoff we want:
- A stable engine run writing clean NFL data to Sheets
- A usable weekly picks workflow
- A dependable Best Ball board
- Lookup good enough for real draft / research use
- Model-performance feedback that tells us what to trust

## Working Principles
- Prefer nflverse and owned calculations over fragile paid APIs when possible
- Keep the dashboard lightweight and deployable on GitHub Pages
- Ship practical workflow wins first, then polish
- Use the board daily so the roadmap follows real usage, not theory
