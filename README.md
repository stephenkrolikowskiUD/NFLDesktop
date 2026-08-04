# NFL DFS Dashboard

A personal NFL research dashboard for turning weekly NFL data, usage metrics, live odds, and projections into one mobile-first view.

This repo is the GitHub Pages frontend for the NFL system. The engine writes data to Google Sheets, and the dashboard reads the workbook through public Sheets CSV endpoints.

## Status: In Development

Week 1 kickoff is **2026-09-09** (NE @ SEA).

- ✅ nflverse data layer with direct-parquet fallback
- ✅ Schedule, spreads, totals, moneylines, snap counts, injuries, usage shares
- ✅ Dashboard ported from MLBDesktop (55 renderers, shared design system)
- ✅ Player props with multi-book best-price routing
- ✅ Season-long projection model, backtested over 7 seasons
- ✅ Best Ball draft board
- ✅ Age/decline and depth-chart role adjustment
- ⬜ Weekly picks (moneyline, spread, player props)
- ⬜ Team selections / combo builder
- ⬜ Grader + Pick Performance
- ⬜ Lookup rebuild on nflverse (was MLB Stats API)

## How It Works

1. `NFLEnginev1.py` pulls nflverse data (via `nflverse_loader.py`) plus live odds, then writes tabs to the Google Sheet.
2. The dashboard (`index.html` + `styles.css` + `app.js`) reads those tabs through Sheets CSV endpoints. No build step — plain HTML/CSS/JS, deployed via GitHub Pages.
3. `app.js` is organized around named per-view renderers with a thin `render()` orchestrator, following the pattern established in MLBDesktop.

## Data Sources

- **nflverse** — schedule, player stats, snap counts, injuries, rosters, play-by-play. Public release assets, **no API key, no rate limit**.
- **The Odds API** (`americanfootball_nfl`) — multi-book pricing and player props.
- **Google Sheets workbook** — `1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0`

Baseline spreads, totals, and moneylines come from nflverse at zero Odds API cost. Odds API credits are spent only on multi-book comparison and props.

### Why nflverse and not a sports-data API

`nfl_data_py` was deprecated and archived in September 2025. Its successor is [`nflreadpy`](https://github.com/nflverse/nflreadpy), which is what `nflverse_loader.py` wraps.

`nflverse_loader.py` exists because nflreadpy 0.1.5 **hardcodes season bounds** — `load_pbp(seasons=[2026])` raises `ValueError: Season must be between 1999 and 2025`, and will keep raising even after 2026 data is published. The repo has had no commits since 2025-11-23. Every loader therefore falls back to reading the parquet release asset directly, which has no such bound. A wrapper outage becomes a no-op instead of a Week 1 blackout.

## Sheet Tabs (written by the engine)

| Tab | Contents |
|---|---|
| `Games` | Full season schedule with spreads, totals, moneylines, venue, roof, rest |
| `Teams` | Team metadata, colors, conference/division |
| `PlayerForm` | Recent usage: targets, target share, air yards share, WOPR, snap %, PPR |
| `Injuries` | Report and practice status by week |
| `PlayerProps` | Every prop quote per book, with no-vig fair probabilities and hold |
| `PropsBoard` | Best price per player/market/line across all five books |
| `Projections` | Season-long projections with best-ball consensus alongside |

Tabs are only written when they have rows — an empty frame is skipped so a thin run can't wipe a tab that still holds usable data.

## Player Props & Odds API Cost

Props come from `/v4/sports/{sport}/events/{eventId}/odds` — **one request per event**. There is no bulk props endpoint.

Cost is `markets_returned × regions`, and three details make this far cheaper than it first looks:

- **`/events` is free** (0 credits), so the engine lists events and narrows the window before spending anything.
- **You're billed for markets *returned*, not requested**, and empty responses aren't charged. Over-requesting markets on a game whose books haven't opened costs nothing.
- **`bookmakers=` replaces `regions=`** for costing — 10 books count as 1 region.

Tuning knobs:

| Env var | Default | Purpose |
|---|---|---|
| `NFL_PROPS_WINDOW_DAYS` | `8` | Only pull props for games within N days |
| `NFL_SKIP_PROPS` | unset | Set to `1` to skip props entirely |
| `NFL_ODDS_CREDIT_FLOOR` | `500` | Abort before spending below this many credits |

The engine reads `x-requests-last` after each call, so the log reports **actual** credits spent, not an estimate.

⚠️ **This API key is shared with MLBDesktop**, which runs 4×/day against the same monthly quota. Watch the floor during season overlap.

### Bookmaker key traps

- There is **no `caesars` key** — Caesars is `williamhill_us` (legacy William Hill US). Using `caesars` throws `INVALID_BOOKMAKERS`.
- **`espnbet` is in region `us2`**, not `us`. Querying `regions=us` returns four books and silently omits it — no error. Always pass `bookmakers=`, never `regions=`.
- Market keys always use `yds`, never `yards`. The "longest" markets are inconsistently ordered: `player_pass_longest_completion` but `player_rush_longest`.
- `player_pass_interceptions` is the QB throwing them; `player_defensive_interceptions` is the defender catching them.

## Season-Long Projections & Best Ball

`projections.py` produces per-player season projections for QB/RB/WR/TE, surfaced on the **Best Ball** tab.

**Method:** per-game production rates from last season → shrunk toward a prior by sample size → scaled by projected availability → ranked by **value over replacement**, with FantasyPros best-ball consensus (ECR) shown alongside.

Three design decisions worth knowing:

1. **VORP, not raw points.** Raw projected points aren't comparable across positions — you start one QB but three WRs. Ranking by raw points puts every startable QB above every skill player and makes consensus look wrong about quarterbacks when it isn't.
2. **The prior is consensus, fit per position.** Shrinking a player who missed time toward "average QB including third-stringers" buries him; consensus already knows Burrow is elite despite a short season. The curve is fit **separately per position**, because ECR is an *overall* rank — pick 56 is roughly QB6 (~300 pts) but WR30 (far fewer), and one global curve maps every mid-round QB to a skill player's total.
3. **Model and consensus are never blended into one ranking.** Both are shown with the delta explicit, because the backtest found the model's *ranking* no better than naive (see below). A disagreement is a prompt to look closer, not an edge.

**Not modeled in v1.** Two of these are visibly biting, and the Disagreement sort surfaces them cleanly:

- ~~No age/decline curve~~ — **added**, see below.
- ~~No role-change modeling~~ — **added**, see below. This turned out to be the single most valuable feature in the model.

Also absent: scheme/coaching changes, injury-return curves, explicit team pace/pass-rate context, and rookie production (nflverse carries no college data — players with no prior-season usage are imputed from consensus and flagged `no data`).

### Backtest results

`backtest.py` trains on season N and scores against N+1. Seven folds (2018→2019 … 2024→2025), evaluated on the top 150 by model rank, Underdog scoring:

| | Model | Naive carry-forward |
|---|---|---|
| Rank correlation | **0.662** | 0.616 |
| MAE (points) | **53.8** | 60.9 |
| Mean bias | −1.3 | — |

Scored on the top 200 by *prior-season* points — a **model-independent** set, so every model version is judged on identical players. Beats naive on ranking in **all 7 folds**.

Positional bias is now within ±4.2% everywhere (QB +2.8%, RB +0.8%, TE −4.2%, WR −3.7%), down from a −12.3% tight-end shortfall.

**Methodology correction worth knowing about.** Earlier versions of this table scored the top N *by model rank*, which let each model version pick its own exam — change the model and the scored population changes, so the baseline's number drifts and versions stop being comparable. Under that flawed metric an earlier build appeared to beat naive on ranking; on a fair set it was actually **losing** (0.599 vs 0.612). Use `--eval-set naive` (the default now); `--eval-set model` is retained for the different question of "how good are the players I'd actually draft."

**The depth-chart adjustment is what makes this model work.** Without it, rank correlation is 0.599 against naive's 0.612 — worse than carrying last season forward. With it, 0.656. Everything else (shrinkage, availability, consensus prior, age) is worth about as much as the single fact of whether a player is currently a starter.

Still a modest edge over a trivial baseline, so treat the board as a cross-check on consensus rather than an override.

Confirmed by backtest:

- ~~Over-projects players who changed teams by ~+20 points~~ — **fixed**, now +1. The age adjustment took it to +11 and the depth-chart adjustment closed the rest: players who switch teams often land in a different depth role, and the chart captures that directly.
- ~~Under-projects tight ends by ~12%~~ — **fixed**, now −4.2%. The cause was the *statistic*, not the tight-end cells: depth multipliers were fit as the median ratio, and outcomes are right-skewed enough that the median sits well below the ratio which balances totals (TE1 0.913 vs 0.997). Refit as `sum(actual)/sum(projected)`.
- ~~Availability over-projected by ~1.3 games~~ — **halved to +0.88**. `LEAGUE_AVG_GAMES` was assumed at 15.0; the measured population mean is 13.6. Swept to 14.0, which minimizes point bias.
- **Overall bias now −1.3 points**, down from +11.6 at the start of the session.
- Largest remaining: players who changed teams, +8.8 points.
- ~~Under-projects players who missed time by ~−17 points~~ — **fixed** by raising `AVAILABILITY_PRIOR_WEIGHT` to 10; now +1 point
- Mild overall over-projection, ~+9 points
- Availability rank correlation is only 0.17, but per-player availability still beats a flat league average on MAE (56.2 vs 59.6), so it stays

**Not confirmed:** an earlier draft of this README claimed the model ran ~11 ranks low on WRs and ~17 high on TEs. The backtest does **not** support that — all positions over-project fairly uniformly (QB +3.3%, RB +6.8%, TE +5.8%, WR +6.3%). That pattern was disagreement with the single 2026 consensus snapshot, not a model defect.

**Cannot be validated:** nflverse's `ff_rankings` ships a single scrape date, so no historical expert consensus exists and the consensus-anchored prior is untestable. `--proxy-consensus` substitutes prior-season finish, but that makes partial-season players *worse* (−24.2 vs −17.1) — someone who missed time has a poor prior-season finish, so the proxy reinforces the exact pessimism real expert rankings would correct. The proxy tests the mechanism, not the thing that makes it work.

```bash
python backtest.py --start 2018 --end 2024 --top 150
python backtest.py --start 2018 --end 2024 --top 150 --proxy-consensus
```

### Age adjustment (measured, not assumed)

Derived by regressing `log(actual / projected)` on age across the backtest folds, then refitting with each fold held out to test whether the slope survives:

| Pos | Slope/yr | Leave-one-out range | Applied? |
|---|---|---|---|
| RB | −0.046 | −0.034 … −0.056 | ✅ stable |
| WR | −0.024 | −0.017 … −0.029 | ✅ stable |
| QB | +0.007 | −0.003 … +0.020 | ❌ crosses zero |
| TE | +0.000 | −0.017 … +0.009 | ❌ crosses zero |

**QB and TE get no adjustment** — their slopes flip sign depending on which fold is held out, so applying one would fit noise. That RBs decline steeply while QBs don't is also what football knowledge predicts, which is mild independent support that the RB/WR effects are real.

Applied *relative to* a reference age (the position's mean), so a typical-aged player is unchanged and only the age differential moves. The raw fitted intercepts sat near 0.65, but that reflects the model's overall over-projection rather than aging — anchoring keeps the two corrections separate.

Validated out-of-sample (slopes fit excluding the scored fold): MAE improved in **6 of 7 folds**, mean rank correlation 0.628 → 0.640.

Unexpected side benefit: the **changed-teams bias fell from +19 to +11 points**. Many players who switch teams are older veterans, so age was the underlying confound — and correcting it fixed most of that bias without the accuracy cost that shrinking those players directly had incurred.

These are empirical constants, not laws. Refit periodically.

### Depth-chart (role) adjustment — the model's most valuable feature

Median `actual / projected` by position and depth rank, from each target season's **season-opening** depth chart:

| Rank | QB | RB | WR | TE |
|---|---|---|---|---|
| 1 (starter) | 1.046 | 0.946 | 0.963 | 0.913 |
| 2 | **0.141** | 0.787 | 0.604 | 0.544 |
| 3+ | 0.126 | 0.465 | 0.359 | 0.268 |

This addresses the model's biggest structural blind spot: projections come from last season's usage, so a player who is now a backup still carries a starter's workload forward. A backup quarterback delivers about **14%** of the naive projection.

Every cell has n ≥ 21 and a tight leave-one-out range (all spreads < 0.25), so unlike the age slopes none flip direction depending on which fold is held out.

Fitted on the **full population**, not just top-ranked projections. A top-250 cut left QB2 with n=9, falling back to a pooled 0.649 — wildly wrong for someone who doesn't take snaps. Widening to all players gave QB2 n=107.

**Snapshot timing is load-bearing.** nflverse's 2025+ depth chart feed is a continuous `dt` snapshot stream with no season or week. Reading the *newest* snapshot of a completed season leaks the future and misreads anyone benched late — it measurably degraded a fold (rank correlation 0.606 → 0.569). So `depth_ranks(snapshot=...)` takes `"earliest"` for backtesting finished seasons and `"latest"` for the upcoming one, where newest genuinely means current preseason.

Caveat: pre-2025 depth charts have no preseason rows at all (`game_type` is REG onward), so those folds fall back to week 1. A week-1 depth chart is published at the season start rather than in August — camp reporting makes most of it knowable earlier, but it isn't strictly point-in-time.

### Scoring

Defaults to **Underdog** best ball: 0.5 per reception, 0.04/passing yard, **4-point passing TDs**, −1 per interception, 6-point rushing/receiving TDs, −2 fumble lost, 2 per 2-pt conversion.

Points are computed from components rather than nflverse's `fantasy_points`, which uses generic standard scoring (6-point passing TDs, −2 interceptions) and would put projections on the wrong scale.

| `NFL_SCORING` | Per reception |
|---|---|
| `underdog` (default) | 0.5 |
| `half` | 0.5 |
| `ppr` | 1.0 |
| `standard` | 0.0 |

Replacement levels assume Underdog's 12-team lineup (1 QB / 2 RB / 3 WR / 1 TE / 1 FLEX), with flex spots apportioned to RB and WR. Override via `build_projections(replacement_ranks=...)`.

⚠️ Consensus ECR ordering is PPR-flavored, so in `standard` the point scale self-calibrates but the consensus *ordering* still reflects reception-heavy assumptions.

## Setup

### Local
```bash
pip install -r requirements.txt
python NFLEnginev1.py
```
Prompts for the Odds API key if it isn't in the environment. For the Sheets write, set either:
- `GOOGLE_SERVICE_ACCOUNT_JSON` — the service-account JSON **content**, or
- `GOOGLE_APPLICATION_CREDENTIALS` — a **path** to the key file

### GitHub Secrets (for Actions)
- `ODDS_API_KEY`
- `GEMINI_API_KEY`
- `OPENWEATHER_API_KEY`
- `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON content)

nflverse needs no secret.

## Known Data Gotchas

- **Sign conventions differ.** nflverse `spread_line` is *positive* when the home team is favored; book spreads are *negative*. Both describe the same line. Normalize at comparison, never assume.
- **Snap counts have no `gsis_id`** — only `pfr_player_id`. `attach_gsis_id()` routes through the players crosswalk and reports match coverage (~99.8%). Without it, players silently vanish rather than erroring.
- **`load_teams()` returns ~36 rows, not 32** — includes relocated franchises (OAK, SD, STL, LA). Don't assume a clean 32-row join.
- **Depth charts schema broke in 2025.** Pre-2025 has 15 columns keyed by season/week; 2025+ has 12 different columns keyed by a `dt` snapshot timestamp. Loading a span across that boundary silently returns a nulled union.
- **`practice_status` contains a literal whitespace value** upstream; sanitized in `load_injuries()`.
- **A missing Sheets tab returns HTTP 200 with the *first* sheet's data.** Google's gviz CSV endpoint does not 404 on an unknown `sheet=` name — it silently falls back. A misspelled or not-yet-written tab therefore renders another tab's rows as if they were real. `app.js` guards this with a per-tab `requires` fingerprint column; don't remove it. (Caught live: the Props view showed 272 rows of `Games` data.)
- **No red zone columns** in weekly stats. Either aggregate play-by-play (~20 MB/season) or use `load_ff_opportunity()` expected-points, which is more useful for projections anyway.
- **nflverse update crons are manually re-enabled each September**, so early-Week-1 data can be stale even when requests succeed. `dataset_last_updated()` checks freshness cheaply.

## Run Mode

GitHub Actions, twice daily during active slates. Retire the `schedule:` block and keep `workflow_dispatch:` when the season ends, matching the NBA/World Cup pattern.

## Important Notes

- Keep the dashboard entry point named `index.html`; GitHub Pages depends on it.
- No private API keys in this repo, in the HTML/JS, or in git history.
- Public Sheet IDs are identifiers, not secrets — but the dashboard reads the workbook through an unauthenticated endpoint, so the *entire* workbook is world-readable, not just the rendered tabs. Treat "which tabs live in this workbook" as the real access-control boundary.
- Personal research tool, not betting advice.
