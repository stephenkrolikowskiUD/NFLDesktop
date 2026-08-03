# @title 🏈 NFL Dashboard Engine (v1.0 — Data Pipeline) — 2026-08-02
import pandas as pd
import numpy as np
import requests
import json
import time
import os
from datetime import datetime, timedelta
import pytz
import gspread
from gspread_dataframe import set_with_dataframe
from google.auth import default
from google.oauth2.service_account import Credentials

# ============================================================================
# CONFIGURATION
# ============================================================================

SPORT_LABEL = "NFL"
SHEET_ID = "1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_TTL_SECONDS = 3600  # 1 hour
QUOTA_FLOOR_THIS_SPORT = 100  # Guard Odds API quota

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Timezone
eastern = pytz.timezone('US/Eastern')

# ============================================================================
# UTILITIES
# ============================================================================

def load_secret(key_name: str, prompt: str = None, allow_missing: bool = False) -> str:
    """Load secret from env or prompt user. allow_missing=True returns empty string if not found."""
    if key_name in os.environ:
        return os.environ[key_name]
    if prompt:
        value = input(prompt).strip()
        if value:
            return value
    if allow_missing:
        print(f"⚠️  {key_name} not set (optional)")
        return ""
    raise ValueError(f"Missing required {key_name}")

def record_odds_quota(resp) -> int | None:
    """Capture x-requests-remaining from Odds API response."""
    try:
        remaining = int(resp.headers.get('x-requests-remaining', '99999'))
        print(f"📊 Odds API quota: {remaining} remaining")
        return remaining
    except (AttributeError, TypeError, ValueError):
        return None

def check_quota_or_abort(resp, context: str) -> None:
    """Abort if Odds API quota below floor."""
    remaining = record_odds_quota(resp)
    if remaining is None:
        return
    if remaining < QUOTA_FLOOR_THIS_SPORT:
        msg = f"🛑 QUOTA GUARD: {remaining} remaining < {SPORT_LABEL} floor {QUOTA_FLOOR_THIS_SPORT} ({context}). Aborting."
        print(msg)
        raise RuntimeError(msg)

def cached_fetch(cache_key: str, fetch_fn):
    """Return cached payload if fresh, else fetch and cache."""
    path = os.path.join(CACHE_DIR, f"{SPORT_LABEL}_{cache_key}.json")
    if os.path.exists(path) and (time.time() - os.path.getmtime(path)) < CACHE_TTL_SECONDS:
        age = int(time.time() - os.path.getmtime(path))
        try:
            with open(path) as f:
                cached = json.load(f)
            print(f"💾 Cache hit: {cache_key} (age {age}s)")
            return cached
        except Exception as e:
            print(f"⚠️  Cache unreadable for {cache_key} ({e}) — refetching")
    data = fetch_fn()
    if data:
        tmp_path = f"{path}.tmp"
        try:
            with open(tmp_path, 'w') as f:
                json.dump(data, f)
            os.replace(tmp_path, path)
        except Exception as e:
            print(f"⚠️  Could not cache {cache_key}: {e}")
    return data

# ============================================================================
# BIG BALLS API (NFL Schedule, Team Info, Game State)
# ============================================================================

def fetch_nfl_schedule(api_key: str, week: int = None) -> list:
    """Fetch NFL schedule from Big Balls Sports Data API."""
    base_url = "https://api.bigballsdata.com/v1/nfl"

    try:
        if week:
            url = f"{base_url}/schedule?week={week}"
        else:
            url = f"{base_url}/schedule"

        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️  Big Balls schedule fetch failed: {resp.status_code}")
            return []
    except Exception as e:
        print(f"⚠️  Big Balls schedule error: {e}")
        return []

def fetch_nfl_teams(api_key: str) -> list:
    """Fetch NFL teams from Big Balls."""
    base_url = "https://api.bigballsdata.com/v1/nfl/teams"

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(base_url, headers=headers, timeout=10)

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️  Big Balls teams fetch failed: {resp.status_code}")
            return []
    except Exception as e:
        print(f"⚠️  Big Balls teams error: {e}")
        return []

# ============================================================================
# ODDS API (Spreads, Moneylines, Props)
# ============================================================================

def fetch_odds(api_key: str) -> dict:
    """Fetch live NFL odds from The Odds API."""
    url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h,spreads",  # Moneylines and spreads
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        check_quota_or_abort(resp, "odds fetch")

        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️  Odds API fetch failed: {resp.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️  Odds API error: {e}")
        return {}

# ============================================================================
# DATA TRANSFORMATIONS
# ============================================================================

def transform_games(schedule: list, odds: dict) -> pd.DataFrame:
    """Transform schedule + odds into games DataFrame."""
    games = []

    for game in schedule:
        away_team = game.get("away_team", "")
        home_team = game.get("home_team", "")
        start_time = game.get("start_time", "")

        # Find matching odds for this game
        game_odds = {}
        for odds_game in odds.get("games", []):
            if (odds_game.get("away_team") == away_team or
                odds_game.get("home_team") == home_team):
                game_odds = odds_game
                break

        spread = "—"
        moneyline_home = "—"
        moneyline_away = "—"

        for bookmaker in game_odds.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market.get("key") == "spreads":
                    for outcome in market.get("outcomes", []):
                        if outcome.get("name") == home_team:
                            spread = f"{home_team} {outcome.get('point', 0)}"
                if market.get("key") == "h2h":
                    for outcome in market.get("outcomes", []):
                        if outcome.get("name") == home_team:
                            moneyline_home = outcome.get("odds", "—")
                        if outcome.get("name") == away_team:
                            moneyline_away = outcome.get("odds", "—")

        games.append({
            "away_team": away_team,
            "home_team": home_team,
            "start_time": start_time,
            "spread": spread,
            "moneyline_home": moneyline_home,
            "moneyline_away": moneyline_away,
        })

    return pd.DataFrame(games)

def generate_picks(games_df: pd.DataFrame) -> pd.DataFrame:
    """Generate basic moneyline picks (placeholder logic)."""
    picks = []

    for _, game in games_df.iterrows():
        # Simple heuristic: pick home team
        picks.append({
            "team": game["home_team"],
            "pick_type": "moneyline",
            "confidence": "medium",
            "reasoning": "home field advantage",
        })

    return pd.DataFrame(picks)

def generate_spread_picks(games_df: pd.DataFrame) -> pd.DataFrame:
    """Generate spread picks (placeholder logic)."""
    picks = []

    for _, game in games_df.iterrows():
        # Simple heuristic: pick away team spread
        picks.append({
            "team": game["away_team"],
            "spread": game["spread"],
            "confidence": "low",
            "reasoning": "contrarian",
        })

    return pd.DataFrame(picks)

# ============================================================================
# GOOGLE SHEETS WRITER
# ============================================================================

def write_to_sheets(sheet_id: str, data_dict: dict) -> None:
    """Write data to Google Sheets."""
    try:
        # Authenticate (assumes GOOGLE_APPLICATION_CREDENTIALS env var set)
        creds = Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id)

        # Clear and write each tab
        for tab_name, df in data_dict.items():
            try:
                worksheet = sheet.worksheet(tab_name)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = sheet.add_worksheet(title=tab_name, rows=1, cols=1)

            worksheet.clear()
            set_with_dataframe(worksheet, df, include_index=False, allow_formulas=True)
            print(f"✅ Wrote {len(df)} rows to {tab_name}")

    except Exception as e:
        print(f"⚠️  Failed to write to Sheets: {e}")

# ============================================================================
# MAIN ENGINE
# ============================================================================

def main():
    print(f"🏈 {SPORT_LABEL} Engine v1.0 starting at {datetime.now(eastern)}")

    # Load API keys
    big_balls_key = load_secret("BIG_BALLS_API_KEY", "🔑 Big Balls API Key: ")
    odds_api_key = load_secret("ODDS_API_KEY", "🔑 Odds API Key: ")
    gemini_key = load_secret("GEMINI_API_KEY", "🤖 Gemini API Key: ", allow_missing=True)

    if not SHEET_ID:
        raise ValueError("SHEET_ID not set in config")

    # Fetch data
    print("📡 Fetching NFL schedule...")
    schedule = cached_fetch("schedule", lambda: fetch_nfl_schedule(big_balls_key))

    print("📡 Fetching teams...")
    teams = cached_fetch("teams", lambda: fetch_nfl_teams(big_balls_key))

    print("📡 Fetching odds...")
    odds = cached_fetch("odds", lambda: fetch_odds(odds_api_key))

    # Transform data
    print("🔧 Transforming data...")
    games_df = transform_games(schedule, odds)
    teams_df = pd.DataFrame(teams) if teams else pd.DataFrame()
    picks_df = generate_picks(games_df)
    spread_picks_df = generate_spread_picks(games_df)

    # Write to Sheets
    print("📝 Writing to Google Sheets...")
    data_to_write = {
        "Games": games_df,
        "Picks": picks_df,
        "SpreadPicks": spread_picks_df,
        "Teams": teams_df,
    }
    write_to_sheets(SHEET_ID, data_to_write)

    print(f"✅ Engine run complete at {datetime.now(eastern)}")

if __name__ == "__main__":
    main()
