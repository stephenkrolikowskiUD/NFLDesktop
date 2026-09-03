# NFLDesktop — working rules

These are process rules distilled from real bugs found in this repo, not a
restatement of README.md's "Known Data Gotchas" (data-source quirks) or
PLAN.md (current sprint status) — read those too, they're both current and
maintained. This file is for conventions worth re-checking on every change,
because violating them has already caused real, shipped bugs.

## Season phase has exactly one source of truth

"Are we in preseason or regular season?" must be answered in one place and
read everywhere else. As of the 2026-08-30 review, it was answered five
different ways at once — `resolve_odds_sport`'s calendar heuristic,
`resolve_model_identity`'s phase branch, a workflow env override,
`NFLGrader1.py`'s hardcoded date-literal fallback, and a per-row
`game_type == "PRE"` check — and they disagreed with each other on the same
row on the same day (WEEK correctly said preseason while MODEL_ERA said
regular season, live, 10 days before kickoff).

**Before adding a new preseason/regular-season branch anywhere**, grep for
`resolve_season_phase`, `infer_pick_phase`, `SEASON_PHASE`, `ODDS_SPORT`,
and `GAME_TYPE` first. The single source of truth now lives in
`nfl_phase.py`: the engine resolves the active phase once from schedule
context, writes that phase onto pick rows, and the grader reads the stored
phase metadata instead of re-guessing from dates.

Update on 2026-09-02: the old multi-guess setup (`resolve_odds_sport`,
`resolve_model_identity`, row-level `game_type == "PRE"`, and the grader's
date fallback) has been consolidated behind `nfl_phase.py`. Do not reintroduce
new independent phase heuristics elsewhere.

## A static override must be at least as phase-aware as what it overrides

If a value is normally computed dynamically (e.g. from the current season
phase) and a workflow/env override exists to pin it, the override itself
needs the same phase-awareness, or it will silently defeat the dynamic logic
for every case the dynamic logic was actually right about. Setting
`NFL_MODEL_VERSION`/`NFL_MODEL_ERA` unconditionally in `nfl-engine.yml` to a
regular-season value did this — it overrode the correct preseason answer for
the ~10 days between setting it and Week 1 actually starting. An override
should either compute its own phase check before applying, or be added only
once the condition it assumes is actually true.

Update on 2026-08-30: that unconditional override has already been removed.
Do not re-add it unless the override logic itself is phase-aware.

## One identity/dedup concept, one key function

This repo has repeatedly grown a second implementation of an existing check
instead of extending the first: a second live-odds-presence check next to
`generate_preseason_game_picks`'s own, a second week-resolution function next
to `nv.current_week` (with a different, wrong empty-fallback direction), and
a second dedup key (`_market_fallback_key`) next to `_pick_key` that encodes
a different rule for the same row shape. When you need "does this game have
live odds," "what week is it," or "is this pick a duplicate of that one,"
grep for the existing function first and extend it. If it doesn't handle
your case, that's a sign the existing function needs a parameter, not that
you need a sibling.

## A sentinel value that will never match a real key needs its own signal

Grading/lookup code here treats "not found in the lookup" as "not ready yet,
retry next run" (`not_ready`, benign). That's correct for a pick whose game
genuinely hasn't happened. It silently becomes wrong the moment a stamped
value (a negative synthetic week, a blank team) can *never* appear in the
real lookup table it's checked against — the row now retries forever with no
way to tell "will resolve later" apart from "will never resolve." If you
introduce a synthetic/placeholder value for anything that gets graded later,
either make sure the grader's lookup can represent that value, or give the
"this can never match" case a distinct counter/log line, not silence into
`not_ready`.

## Verify a pipeline change by executing it against a constructed row

"Unit-tested against live data" in this codebase has meant reading the
data through the changed function, not exercising every code path with a
row shaped like what a real run will actually produce. The
`assemble_pick_tabs` crash (MODEL_VERSION/MODEL_ERA columns assumed present,
never set by either pick-generator) shipped despite that — it only fires
once a pick is actually generated, which hadn't happened yet in production.
Before trusting a fix to `picks.py`, `NFLEnginev1.py`, or `NFLGrader1.py`,
construct one fake row of the shape the changed path will see in prod and
run the actual function against it, not just read the diff.

Concrete example from 2026-08-30: `assemble_pick_tabs()` crashed because
`DataFrame.get("MODEL_VERSION", "")` returned a scalar string, not a Series,
and the next `.astype(...)` exploded the moment a real pick row was built.
The fix was to use a same-index default Series helper and then verify it by
executing `assemble_pick_tabs()` against a constructed one-row preseason
moneyline pick.

## Current launch status lives in PLAN.md

This file is for durable repo rules and bug-shaped lessons. For date-sensitive
status, pre-kickoff checklists, and "what is still open right now," read
`PLAN.md` first.

## Sheet-derived UI strings must be escaped at render time

`app.js` already has an `esc()` convention for strings that came from Sheets,
API rows, or any other mutable data source. Keep using it every time a render
path gets rewritten. The featured-pick / hero-play templates are especially
easy to regress here because redesign work tends to rebuild those strings from
scratch and reintroduce raw interpolation. If a value is ultimately row data,
escape it in the last template that renders it, even if an upstream helper
already "should" have normalized it.

## Team metadata is a real dashboard dependency, not optional garnish

The NFL UI now uses the `Teams` sheet for visible product features: team logos,
nickname lookups, matchup identity, and branded game-market / shortlist cards.
That means `loadTeams()` in `app.js` cannot stay a stub, and dashboard-only
engine runs cannot skip writing `Teams` just because the page can technically
render without it. If logos disappear, check both sides: whether the frontend
is actually loading `Teams`, and whether `NFLEnginev1.py` is still publishing
that tab in every mode.

## Picks boards should read like editorial boards, not audit tables

The easiest way for this dashboard to look "AI-generated" is to render every
pick surface as a grid of repeated pills and flat fact rows. The better pattern
for NFL Picks is: strong hierarchy for the featured play, quieter footer-style
provenance, logos/matchup identity where relevant, and one clear reason-to-bet
sentence instead of repeating the same fact three ways. When touching
`renderFeaturedPick`, `renderPickBoardRow`, or the related CSS, preserve that
editorial feel instead of drifting back toward a spreadsheet-shaped layout.

The same rule applies to support surfaces around picks. `Model Picks` health /
freshness summaries and the `Draft` contest-slate chooser should read like
compact tape or market-window UI, not a stack of equal-weight cards or a cloud
of pills. Show a few high-signal numbers, a short preview of live games, and
put the full chooser or rationale behind an explicit open state.

Related UI convention from 2026-09-03: the weekly board, next-game-day board,
and append-only audit trail are three different products. `Picks_Weekly` is the
active-week board and must accumulate qualified picks as Thursday, Sunday, and
Monday markets open. `Picks_Current` is only the nearest unstarted game-day
slice of that board; it must clear or advance after kickoff rather than showing
expired picks. `Daily_Picks` is archival history for grading and CLV. Do not
blend these surfaces or let a fallback masquerade as the authoritative board
without saying so explicitly.

## No real project/account identifiers in fallback paths, even for convenience

Local credential auto-detection (`sports_common.py`'s
`DEFAULT_GOOGLE_CREDENTIAL_PATHS`) is fine as a documented local
convenience (see README.md), but the fallback path list should never name a
real GCP project id or key filename verbatim — that's identifying
information about live infrastructure, committed to source, regardless of
whether the key content itself is present. Use a placeholder path plus a
loud "no credentials found, checked: X" error instead.
