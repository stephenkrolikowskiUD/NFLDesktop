# NFLDesktop Roadmap

_Last updated: 2026-09-22_

## Where We Are
NFL is no longer a greenfield build. The core dashboard, engine, season-long projection layer, Lookup, and game-market board are live. The first real Week 1 player-prop run completed on September 3: 138 unique lines across 52 players produced 14 validated Gemini consensus picks, which wrote to `Picks_Current` and the append-only `Daily_Picks` ledger with regular-season phase and model identity stamped correctly.

The pick workflow is split deliberately: `Picks_Weekly` is the curated all-week decision board, `Picks_Current` is the nearest unstarted game-day slice, and `Daily_Picks` is the complete historical ledger for grading and CLV. On September 7, the kickoff parser, history preservation, and board-row disclosure behavior were corrected before opening kickoff. On September 10, live-season rollover and early-season baseline guards were added after a September run incorrectly requested 2027 nflverse data and then exposed a one-game 2026 baseline that collapsed the player-context board. On September 13, player-prop eligibility was made fail-closed against current roster and depth-chart identities, with weekly-board revalidation to remove stale player picks without altering history. The Best Ball board can now also prefer a current FantasyPros API consensus feed when a personal key is present, while preserving the nflverse best-ball snapshot as a labelled fallback.

The first Week 1 grading report is quarantined, not a model conclusion. The audit found that player props were joining live odds events to a player's last historical team/opponent, while the grader settled by player ID + week without confirming the stored matchup. That let wrong-event rows, including future-dated rows, inherit a real Week 1 box score. The original 26.1% / -47.0% headline is therefore not a valid scorecard. The clean rebuild is 15 decisive picks at 46.7% and -13.0% ROI, explicitly low sample. A second independent review hardened the persistent weekly boards, protected settled results from overwrite, restored legacy team-market rescue, and made performance deduplication preserve changed lines and selection methods. The first quarantine run predated the new audit fields, so the overwritten legacy values cannot be reconstructed from the ledger; future quarantines are now auditable.

FantasyPros API consensus is configured as an optional source for the draft board. The free personal API key uses FantasyPros' documented public base URL (`/public/v2/json`) with the `x-api-key` header; this was briefly misrouted to the separate production namespace and correctly rejected with HTTP 403. The public consensus endpoint rejects the documented `position=ALL` parameter in live use, so the client now fetches and combines `QB`, `RB`, `WR`, and `TE` rankings independently, retaining successful positions if another request fails. September 19 production verification succeeded with 40 HALF-redraft rankings and a 100% ECR crosswalk. The workflow also now stamps an explicit regular-season model version/era and refreshes at noon ET Sunday after early inactive reports.

The Week 2 audit independently reproduced all 83 settled grades from fresh nflverse logs: 39 wins, 44 losses, 47.0% hit rate, and -8.3% price ROI. Nine legacy bad-context rows were correctly quarantined and no new schedule-invalid rows appeared after the September 15 hardening. The audit found the main remaining problem was recommendation quality: raw prior-season line-clear rates were being treated as forecasts, producing severely overconfident probabilities. Week 3 moves live publication to the calibrated v2 model: a no-vig market prior, current-season evidence weighting, real expected-return math, no volume padding, and a distinct model cohort. Plus-money, anytime-touchdown, and injury-flagged props remain research-only. The public shortlist and slips now consume that same production board rather than a separate raw-rate scan; all candidates remain in the append-only ledger so the policy can be evaluated honestly rather than erasing misses.

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
- ✅ Optional FantasyPros API consensus for draft rankings, with labelled
  nflverse best-ball fallback when no personal API key is configured
- ✅ Explicit model-only disclosure when both FantasyPros API and nflverse
  consensus sources are unavailable; no silent source downgrade
- ✅ Week 2 grades independently verified against fresh nflverse game logs
- ✅ Week 3 temporary publication guardrails: 3/3 Gemini consensus, no
  plus-money or anytime-TD Playable picks, and SMASH-only overs

## In Progress
- 🟠 Pick calibration repair — replace raw prior-season line-clear frequency with a shrunk, calibrated probability before treating it as model hit rate or EV
- 🟠 Measurement repair — distinguish user-visible board exposure from the complete research ledger, persist authoritative injury context, and make CLV movement measurable
- 🟠 Defensive context repair — derive actual opponent yards/rates allowed instead of labelling offensive team totals as defense
- 🟡 Best Ball board layout polish and mobile compaction
- 🟡 Game Builder presentation and entry ergonomics
- 🟡 Season-long projection explainer / trust layer

## Current Sprint Priorities
1. **Evaluate and harden the Week 3 recommendation policy**
   - Run the engine with the temporary publication gates and verify the shortlist contains only 3/3, non-plus-money recommendations
   - Confirm STRONG overs and all anytime-touchdown props remain visible for research but never receive Playable status
   - Record board exposure separately from research-ledger inclusion so performance describes what users actually saw
   - Replace raw historical line-clear rates with sample-aware, calibrated estimates before restoring broader Playable eligibility
   - Persist source injury status and report timestamp with each pick; Gemini commentary must not be the audit field
   - Replace fake defensive labels with correctly derived opponent-allowed statistics
   - Redesign CLV comparison so it follows a defined market/book rather than selecting the line nearest the opener

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
