# NFLDesktop Roadmap

_Last updated: 2026-08-28_

## Where We Are
NFL is no longer a greenfield build. The core dashboard, engine, season-long projection layer, Lookup, and preseason game-market board are all live. The weekly picks + grading backend (`picks.py`, `NFLGrader1.py`) is now **code-complete, but still launch-sensitive** — Gemini consensus generation, market-line validation, a deterministic no-Gemini fallback, preseason team-market picks when player props are not posted yet, and a full grader with per-game readiness gating and Pick_Performance aggregation all exist. It has been tested at the function level against real nflverse/Sheet data throughout, but **has not been proven end-to-end in production on a real live player-prop slate**. As of August 28, 2026, the highest-risk preseason defects were the wrong WEEK stamp on synthetic preseason picks, a regular-season model-era handoff gap, and fallback logic that could emit both moneyline sides of the same game. Those are now fixed in code, but the live Gemini path and live odds-outage monitoring still need a real run before Week 1. Until that live pass is confirmed, treat this as "built, not yet proven," and keep the Info page's "planned, not yet active" copy as-is rather than flipping it to describe this as running.

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
- 🟠 Weekly picks generation + grading — code-complete, unproven in full production. `picks.py` (Gemini 3-pass consensus + recovery, market-line snap-to-validation, SMASH cap, deterministic VALIDATED_MODEL fallback, plus preseason team-market picks from spreads/moneylines/totals) and `NFLGrader1.py` (per-game kickoff-based readiness, player_id-first identity matching with ambiguity detection, team-market grading, Pick_Performance/Snapshots in MLB's exact schema) are both built and unit-tested against live nflverse/Sheet data. What's still open: a real Gemini player-prop run has not been confirmed, the regular live picks-to-grader loop still needs a completed real slate, and the sportsbook-outage warning path still needs a deliberate live dry run. The `GEMINI_API_KEY` secret needs to be confirmed set in this repo (shared with MLB) before the next real player-prop run will exercise the AI path. Before the first regular-season run, explicitly set `NFL_MODEL_VERSION` and `NFL_MODEL_ERA` in the workflow so Week 1 production picks land under a stable regular-season identity even if defaults are already safe.
- 🟡 Best Ball board layout polish and mobile compaction
- 🟡 Game Builder presentation and entry ergonomics
- 🟡 Season-long projection explainer / trust layer

## Current Sprint Priorities
1. **Prove the picks + grader loop end to end (backend is built, needs a live pass)**
   - Confirm `GEMINI_API_KEY` is set as a repo secret, explicitly set `NFL_MODEL_VERSION` / `NFL_MODEL_ERA` for the regular-season workflow, then let a real Thu/Sun/Mon engine run populate `Picks_Current`/`Daily_Picks` with actual Gemini player-prop output
   - Let `NFLGrader1.py` run against a completed gameday and confirm `Pick_Performance` populates with real hit/miss data for both player props and team-market rows
   - Force one monitored outage-path run before Week 1 by withholding or breaking the Odds API call and confirming the dashboard surfaces the sportsbook warning instead of quietly looking healthy off baseline-only data
   - Only once that's confirmed working: flip the Info page's "planned, not yet active" copy to describe this as live

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
