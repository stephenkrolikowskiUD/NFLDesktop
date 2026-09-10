# NFLDesktop Roadmap

_Last updated: 2026-09-10_

## Where We Are
NFL is no longer a greenfield build. The core dashboard, engine, season-long projection layer, Lookup, and game-market board are live. The first real Week 1 player-prop run completed on September 3: 138 unique lines across 52 players produced 14 validated Gemini consensus picks, which wrote to `Picks_Current` and the append-only `Daily_Picks` ledger with regular-season phase and model identity stamped correctly.

The pick workflow is split deliberately: `Picks_Weekly` is the curated all-week decision board, `Picks_Current` is the nearest unstarted game-day slice, and `Daily_Picks` is the complete historical ledger for grading and CLV. On September 7, the kickoff parser, history preservation, and board-row disclosure behavior were corrected before opening kickoff. On September 10, live-season rollover and early-season baseline guards were added after a September run incorrectly requested 2027 nflverse data and then exposed a one-game 2026 baseline that collapsed the player-context board. The remaining proof point is a completed Week 1 game flowing through `NFLGrader1.py` into `Pick_Performance`; the grader has not yet settled a real regular-season pick.

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
- ✅ Season-phase resolution consolidated in `nfl_phase.py` and used by engine + grader
- ✅ Live Gemini player-prop generation proven through GitHub Actions on a real Week 1 board
- ✅ Separate weekly, next-game-day, and append-only history pick surfaces
- ✅ Team logo support and compact matrix-based picks presentation
- ✅ Current-week injury guard: confirmed unavailable players are excluded before
  pick generation, and teammate absences are passed as review context

## In Progress
- 🟠 Weekly picks grading — generation is live; settlement remains unproven. `picks.py` runs Gemini three-pass consensus + recovery, validates every line against the live market, and preserves every qualified pick in `Daily_Picks` even when the display boards limit a player to one prop. `NFLGrader1.py` has per-game kickoff readiness, player_id-first matching, team-market grading, and `Pick_Performance` aggregation. What remains: confirm completed Week 1 player and team picks grade correctly, including push treatment and CLV refresh, then verify the sportsbook-outage warning with a deliberate monitored dry run.
- 🟡 Best Ball board layout polish and mobile compaction
- 🟡 Game Builder presentation and entry ergonomics
- 🟡 Season-long projection explainer / trust layer

## Current Sprint Priorities
1. **Prove the picks + grader loop end to end (generation is live; settlement needs its first real pass)**
   - Let `NFLGrader1.py` run after the Thursday opener and confirm `Pick_Performance` receives real hit/miss/push results for player and team-market picks
   - Confirm `Picks_Current` clears immediately after each game-day slate begins and advances to the next unstarted game day
   - Force one monitored outage-path run after launch by withholding or breaking the Odds API call and confirming the dashboard surfaces the sportsbook warning instead of quietly looking healthy off baseline-only data
   - Resolve legacy preseason rows that cannot map to a real schedule as explicit DNP/archival records rather than retrying forever
   - Re-run the engine after confirmed Week 1 inactives and verify the log reports
     excluded unavailable prop rows plus teammate absence context

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
