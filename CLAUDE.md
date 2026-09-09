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

## Sheet freshness may be row-level or tab-level

Reference tabs such as `Skill_Game_Logs` and `QB_Game_Logs` do not carry a
row-level `LAST_UPDATED` field. The engine stamps every written dashboard tab
with `_generated_at` instead. Any freshness UI must check both fields before
calling a populated tab "No data"; otherwise the dashboard can show live L10
evidence beside a false red source-health warning.

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

For ranked pick matrices, the actual call is primary, player names are
supporting context, and visual weight must decay after the top few rows. Use
the tier-colored row edge/rank as the conviction signal; do not reintroduce
separate tier chips, dots, or a redundant market column. Best Ball controls
must be compact native controls rather than a wall of pills, roster status must
be one inline strip, and player badges are reserved for exceptions such as a
one-turn risk or a data-quality warning, never the default state.

`CALIBRATION_SCORE` is an internal ordering feature, not a user-facing metric.
Never print its raw numeric value in a pick rationale; explain tier floors or
visible evidence in plain language instead. Active-roster `headshot_url` values
must travel through `Slate_Skill`, `Slate_QB`, and `Projections`. Use fixed-size
circular player headshots in pick matrices and Best Ball, with initials as the
fallback for a missing or failed image, never a broken image element.

Related UI convention from 2026-09-03: the weekly board, next-game-day board,
and append-only audit trail are three different products. `Picks_Weekly` is the
active-week board and must accumulate qualified picks as Thursday, Sunday, and
Monday markets open. `Picks_Current` is only the nearest unstarted game-day
slice of that board; it must clear or advance after kickoff rather than showing
expired picks. `Daily_Picks` is archival history for grading and CLV. Do not
blend these surfaces or let a fallback masquerade as the authoritative board
without saying so explicitly.

An empty `Picks_Current` can be correct when the nearest scheduled game day
has no qualified play while `Picks_Weekly` is populated. Keep the empty
daily-board message, but let health and freshness use the weekly snapshot;
never label this state as an engine outage or a missing model run.

Run-health targets are board-specific: the weekly board is measured against
its broad 14-pick review target, while the focused next-slate board is a
three-pick product. Never render a healthy 3/3 next-slate delivery as 3/14.

`This Week's Shortlist` is a full-week surface and must source its model
recommendations from `Picks_Weekly`. It may scan the live market board across
the whole slate, but it must never inherit the three-pick `Picks_Current`
slice used by the focused next-game-day tab.

Shortlist cards use player headshots as the name anchor and a compact pair of
team logos as matchup context. Both must preserve their existing initials or
team-abbreviation fallbacks; visual assets clarify a pick but never replace
its name, matchup, or call.

The player analysis workspace uses the larger hero headshot beside the player
identity in its header. Keep the prop call separate on the opposite side so
the portrait adds recognition without competing with the decision.

Game Builder matchup cards use the same compact pair of team logos before the
matchup label. Keep the text label, kickoff, and availability data visible;
logos improve scan speed but must not become logos-only controls.

During the Week 1 launch window, Dash and Picks carry one compact beta notice
with an honest research-not-guarantee disclaimer and a direct Quick Tour link
to Info. Keep it brief and editorial, not a modal, repeated warning, or
marketing card.

The "current" game day comes from `Schedule`, not from whichever date happens
to have a curated pick. If the Wednesday opener has no qualified play, show an
empty Wednesday slate; do not skip it and label Thursday as the next NFL game
day. The dashboard label must use the same schedule-derived date.

When the nearest scheduled game has live player-prop context but the broad
weekly ranking leaves its `Picks_Current` slice empty, run a separate,
real-line-only next-slate pass for that game. A next-slate surface is not a
leftover filter of the weekly board; it must deliver a concise dedicated board
or explicitly report that the game has no priced player context.

`Slate_Skill` and `Slate_QB` use historical stats for performance context only.
Their player team, position, and active eligibility must come from the current
season roster; their opponent must be stamped from the next scheduled game.
Never filter a current contest using a historical team or opponent: that shows
moved players on the wrong team and can silently remove an entire position
group when the selected matchup differs from Week 18.

The Draft QB pool must come from `Slate_QB`. `Starting_QBs` is supplemental
confirmation data and may legitimately be empty before beat reports arrive;
never let an empty `Starting_QBs` tab replace the roster-backed QB slate.

### Display curation may never run before the historical ledger

The one-prop-per-player rule is a decision-board convenience, not a data
retention rule. Apply it in `build_weekly_pick_board()` (and therefore its
`Picks_Current` slice), never in `assemble_pick_tabs()` before `Daily_Picks`
is derived. A second qualified prop for the same player can be hidden from the
current board, but it must be written to the append-only ledger for later
grading, CLV, and model evaluation.

### Kickoff fields cross a format boundary

Odds-derived player props use Eastern 12-hour times such as `8:20 PM`.
nflverse schedule stamping uses 24-hour times such as `20:20`. Any code that
filters, expires, or grades pick rows must accept both formats and use the
authoritative schedule kickoff when it is available. Never silently downgrade
an unparseable kickoff to a date-only eligibility decision: that is how a
finished game remained in `Picks_Current` after kickoff.

### Pick rationale disclosure must retain native toggle behavior

`renderPickBoardRow()` uses `<details>/<summary>` so the matrix stays
scannable while evidence remains available. Do not attach the old full-row
`pickClick()` navigation handler to the `<summary>`: it prevents the native
open/close action. Player navigation, if needed, belongs on an explicit link
or control inside the row, not on the disclosure trigger.

## Survivor is a schedule tool, not a pick-model surface

The Survivor tab is intentionally client-side. It derives the next regular
season week from `Schedule`, ranks unused teams by current fair win probability
and a four-week save-value adjustment, and stores used teams in browser local
storage under `nfl-survivor-used-v1`. Do not write Survivor choices into
`Daily_Picks`, grade them as model picks, or add new API calls just to render
the helper. A marked-used team must disappear from the candidate board and
remain visible in the used strip so it can be restored deliberately.

## No real project/account identifiers in fallback paths, even for convenience

Local credential auto-detection (`sports_common.py`'s
`DEFAULT_GOOGLE_CREDENTIAL_PATHS`) is fine as a documented local
convenience (see README.md), but the fallback path list should never name a
real GCP project id or key filename verbatim — that's identifying
information about live infrastructure, committed to source, regardless of
whether the key content itself is present. Use a placeholder path plus a
loud "no credentials found, checked: X" error instead.
