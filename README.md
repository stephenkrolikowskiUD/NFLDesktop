# NFL DFS Dashboard

A personal NFL player-prop and spread research dashboard for turning weekly NFL data, live odds, AI picks, and team selection combos into one mobile-first view.

This repo is the GitHub Pages frontend for the NFL system. The engine writes data to Google Sheets, and the dashboard reads the workbook through public Sheets CSV endpoints.

## Status: In Development (Week 1 of 5)

## What It Does

- Shows weekly slate: matchups, spreads, moneylines, and team context
- Surfaces AI picks across multiple boards: moneyline picks, spread picks, team combos
- Supports team selections for building multi-leg combinations
- Displays pick performance analytics (post-launch)

## How It Works

1. `NFLEnginev1.py` pulls NFL data from Big Balls Sports Data API, Odds API for spreads/odds, and writes to Google Sheets
2. The dashboard (`index.html` + `styles.css` + `app.js`) loads those tabs through Google Sheets CSV endpoints. No build step — vanilla HTML/CSS/JS
3. Post-launch: Grader will score picks and feed back to Stats tab

## Key Tabs

- **Dashboard**: weekly slate, matchups, spreads, team context
- **Picks**: moneyline picks, spread picks, team combos
- **Teams**: team selection interface for building combos
- **Lookup**: team search and deeper context
- **Stats**: pick performance analytics (post-launch)
- **Info**: method notes and glossary

## Run Mode

Automated via GitHub Actions: engine runs 2× per day during active slates.

## Data Sources

- Google Sheets workbook: `[TBD]`
- Big Balls Sports Data API (schedules, team info, game state)
- The Odds API (spreads, moneylines, props)
- OpenWeather (stadium conditions)

## Setup

### Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run engine: `python NFLEnginev1.py`
   - When prompted, paste your API keys (same flow as MLBDesktop)
   - Keys are `BIG_BALLS_API_KEY`, `ODDS_API_KEY`, `GOOGLE_SERVICE_ACCOUNT_JSON` path

### GitHub Secrets (for Actions)
Set these in repo Settings → Secrets and variables → Actions:
- `BIG_BALLS_API_KEY`
- `ODDS_API_KEY`
- `GEMINI_API_KEY`
- `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON as a secret)

### Google Sheet
- ID: `1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0`
- Tabs: Games, Picks, SpreadPicks, Teams, Standings, PlayerProps, TeamCombos, Projections
- Service account must have write access

## Important Notes

- Keep the dashboard entry point named `index.html`; GitHub Pages depends on it.
- No private API keys live in this repo, HTML/JS, or git history.
- .env is in .gitignore and will never be committed.
- This is a personal research tool, not betting advice.
