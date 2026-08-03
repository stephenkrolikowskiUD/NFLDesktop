# NFL DFS Dashboard

A personal NFL research dashboard for turning weekly NFL data, usage metrics, live odds, and projections into one mobile-first view.

This repo is the GitHub Pages frontend for the NFL system. The engine writes data to Google Sheets, and the dashboard reads the workbook through public Sheets CSV endpoints.

## Status: In Development

Week 1 kickoff is **2026-09-09** (NE @ SEA). Data pipeline is live; the projection model is the next build.

- ✅ nflverse data layer with direct-parquet fallback
- ✅ Schedule, spreads, totals, moneylines, snap counts, injuries, usage shares
- ✅ Dashboard reads Sheets by tab name
- ⬜ Projection model
- ⬜ Picks (moneyline, spread, player props)
- ⬜ Team selections / combo builder
- ⬜ Grader + Pick Performance

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
