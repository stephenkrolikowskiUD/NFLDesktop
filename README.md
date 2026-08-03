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
- **No red zone columns** in weekly stats. Either aggregate play-by-play (~20 MB/season) or use `load_ff_opportunity()` expected-points, which is more useful for projections anyway.
- **nflverse update crons are manually re-enabled each September**, so early-Week-1 data can be stale even when requests succeed. `dataset_last_updated()` checks freshness cheaply.

## Run Mode

GitHub Actions, twice daily during active slates. Retire the `schedule:` block and keep `workflow_dispatch:` when the season ends, matching the NBA/World Cup pattern.

## Important Notes

- Keep the dashboard entry point named `index.html`; GitHub Pages depends on it.
- No private API keys in this repo, in the HTML/JS, or in git history.
- Public Sheet IDs are identifiers, not secrets — but the dashboard reads the workbook through an unauthenticated endpoint, so the *entire* workbook is world-readable, not just the rendered tabs. Treat "which tabs live in this workbook" as the real access-control boundary.
- Personal research tool, not betting advice.
