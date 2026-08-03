# @title 🏈 NFL Dashboard Engine (v1.1 — nflverse data layer) — 2026-08-02
#
# Data sources:
#   nflverse   — schedule, player stats, snap counts, injuries, rosters (free, no auth)
#   Odds API   — live multi-book moneylines, spreads, totals, player props
#
# nflverse schedules already carry spread_line / total_line, so baseline market
# numbers cost zero Odds API credits. Odds API is only needed for multi-book
# pricing and player props.

import json
import os
from datetime import datetime

import pandas as pd
import pytz
import gspread
from gspread_dataframe import set_with_dataframe
from google.auth import default
from google.oauth2.service_account import Credentials

import nflverse_loader as nv
import odds_client as oc

# ============================================================================
# CONFIGURATION
# ============================================================================

SPORT_LABEL = "NFL"
SHEET_ID = "1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0"
ODDS_SPORT = "americanfootball_nfl"
QUOTA_FLOOR_THIS_SPORT = int(os.getenv(f"{SPORT_LABEL}_ODDS_CREDIT_FLOOR", "500"))

# Only pay for props on games within this horizon. Books open prop markets
# progressively as kickoff approaches, so requesting the full 272-game season
# would mostly buy empty responses — and for the games that DO have props, one
# request per event per market batch adds up fast.
PROPS_WINDOW_DAYS = int(os.getenv("NFL_PROPS_WINDOW_DAYS", "8"))
SKIP_PROPS = os.getenv("NFL_SKIP_PROPS", "").lower() in {"1", "true", "yes"}

eastern = pytz.timezone("US/Eastern")

# ============================================================================
# UTILITIES
# ============================================================================

def load_secret(name: str, prompt_text: str | None = None,
                allow_missing: bool = False) -> str:
    """Env var first (GitHub Actions), then interactive prompt (local runs)."""
    env_val = os.environ.get(name)
    if env_val:
        return env_val
    if prompt_text:
        try:
            value = input(prompt_text).strip()
            if value:
                return value
        except (EOFError, KeyboardInterrupt):
            pass
    if allow_missing:
        print(f"⚠️  {name} not set — continuing without it")
        return ""
    raise RuntimeError(f"Missing required secret: {name}")


def get_gspread_client():
    """Authorize gspread from the service-account JSON.

    GOOGLE_SERVICE_ACCOUNT_JSON holds the JSON *content* (that's how it's stored
    as a GitHub Actions secret), not a path. GOOGLE_APPLICATION_CREDENTIALS is
    supported as a path for local runs.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    svc_json = (os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
                or os.environ.get("GSPREAD_SERVICE_ACCOUNT_JSON"))
    if svc_json:
        try:
            info = json.loads(svc_json)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"GOOGLE_SERVICE_ACCOUNT_JSON is set but isn't valid JSON ({e}). "
                "It must hold the full JSON key *content*, not a file path."
            ) from e
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        print(f"✅ Google auth via env ({info.get('client_email', 'unknown')})")
        return gspread.authorize(creds)

    key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path:
        if not os.path.exists(key_path):
            raise RuntimeError(
                f"GOOGLE_APPLICATION_CREDENTIALS points to a missing file: {key_path}"
            )
        creds = Credentials.from_service_account_file(key_path, scopes=scopes)
        print(f"✅ Google auth via key file ({os.path.basename(key_path)})")
        return gspread.authorize(creds)

    # Distinguish absent from invalid: an unset secret and a bad secret are very
    # different problems, and "auth unavailable" doesn't say which one happened.
    raise RuntimeError(
        "No Google credentials found — neither GOOGLE_SERVICE_ACCOUNT_JSON nor "
        "GOOGLE_APPLICATION_CREDENTIALS is set (both were empty, not invalid).\n"
        "  • GitHub Actions: add a repo secret named GOOGLE_SERVICE_ACCOUNT_JSON "
        "containing the full service-account JSON content.\n"
        "  • Local: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json\n"
        "Then confirm the Sheet is shared with that key's client_email as Editor."
    )


# ============================================================================
# ODDS API
# ============================================================================
# Requests, retries, and quota accounting all live in odds_client.OddsClient.

def extract_book_odds(events: list, preferred="draftkings", fallback="fanduel") -> pd.DataFrame:
    """Flatten Odds API events to one row per game, preferring a single book.

    Mirrors the MLB engine's approach: prefer DraftKings, fall back to FanDuel,
    then whatever book is present, so a book dropping a market doesn't blank
    the row.
    """
    rows = []
    for event in events:
        home = event.get("home_team", "")
        away = event.get("away_team", "")
        books = event.get("bookmakers", [])
        book = (next((b for b in books if b.get("key") == preferred), None)
                or next((b for b in books if b.get("key") == fallback), None)
                or (books[0] if books else None))
        if not book:
            continue

        row = {
            "odds_home_team": home,
            "odds_away_team": away,
            "commence_time": event.get("commence_time", ""),
            "bookmaker": book.get("title", ""),
        }
        for market in book.get("markets", []):
            key = market.get("key")
            # Not `oc` — that's the odds_client module alias at module scope.
            for outcome in market.get("outcomes", []):
                name = outcome.get("name")
                price = outcome.get("price")
                point = outcome.get("point")
                if key == "h2h":
                    if name == home:
                        row["live_home_ml"] = price
                    elif name == away:
                        row["live_away_ml"] = price
                elif key == "spreads":
                    if name == home:
                        row["live_home_spread"], row["live_home_spread_odds"] = point, price
                    elif name == away:
                        row["live_away_spread"], row["live_away_spread_odds"] = point, price
                elif key == "totals":
                    if name == "Over":
                        row["live_total"], row["live_over_odds"] = point, price
                    elif name == "Under":
                        row["live_under_odds"] = price
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================================================
# TRANSFORMS
# ============================================================================

# Odds API uses full team names; nflverse uses abbreviations.
def build_team_name_map(teams: pd.DataFrame) -> dict:
    if teams.empty or "team_name" not in teams.columns:
        return {}
    return dict(zip(teams["team_name"], teams["team_abbr"]))


def build_games_tab(schedule: pd.DataFrame, odds: pd.DataFrame,
                    name_map: dict) -> pd.DataFrame:
    """Schedule as the spine, live odds overlaid where available.

    Sign conventions differ between the two sources and are deliberately left
    as-is rather than normalized here:
      nflverse `spread_line`  → POSITIVE means the home team is favored (+3.5)
      book `live_home_spread` → NEGATIVE means the home team is favored (-3.5)
    Both describe the same line. Normalize at the point of comparison, and do
    not assume a shared sign when diffing them.
    """
    if schedule.empty:
        return pd.DataFrame()

    keep = [c for c in [
        "game_id", "season", "game_type", "week", "gameday", "weekday", "gametime",
        "away_team", "home_team", "away_score", "home_score",
        "spread_line", "total_line", "away_moneyline", "home_moneyline",
        "roof", "surface", "temp", "wind", "stadium", "div_game",
        "away_rest", "home_rest",
    ] if c in schedule.columns]
    games = schedule[keep].copy()

    if not odds.empty:
        odds = odds.copy()
        odds["home_abbr"] = odds["odds_home_team"].map(name_map)
        odds["away_abbr"] = odds["odds_away_team"].map(name_map)

        unmapped = odds[odds["home_abbr"].isna() | odds["away_abbr"].isna()]
        if not unmapped.empty:
            names = pd.unique(pd.concat([
                unmapped["odds_home_team"], unmapped["odds_away_team"]
            ]).dropna())
            print(f"   ⚠️  {len(unmapped)} odds rows unmapped to abbreviations: "
                  f"{list(names)[:6]}")

        odds = odds.dropna(subset=["home_abbr", "away_abbr"])
        odds_cols = [c for c in odds.columns
                     if c.startswith("live_") or c == "bookmaker"]
        games = games.merge(
            odds[["home_abbr", "away_abbr"] + odds_cols],
            how="left",
            left_on=["home_team", "away_team"],
            right_on=["home_abbr", "away_abbr"],
        ).drop(columns=["home_abbr", "away_abbr"], errors="ignore")

    return games


def build_teams_tab(teams: pd.DataFrame) -> pd.DataFrame:
    if teams.empty:
        return pd.DataFrame()
    keep = [c for c in [
        "team_abbr", "team_name", "team_nick", "team_conf", "team_division",
        "team_color", "team_color2", "team_logo_espn",
    ] if c in teams.columns]
    return teams[keep].copy()


def build_player_form_tab(stats: pd.DataFrame, snaps: pd.DataFrame,
                          top_n_weeks: int = 6) -> pd.DataFrame:
    """Recent-form table: last N weeks of usage per skill-position player.

    This is the raw input surface the projection model will consume — usage and
    share metrics, not projections themselves.
    """
    if stats.empty:
        return pd.DataFrame()

    skill = stats[stats["position"].isin(["QB", "RB", "WR", "TE"])].copy()
    if skill.empty:
        return pd.DataFrame()

    max_week = skill["week"].max()
    recent = skill[skill["week"] > max_week - top_n_weeks]

    cols = [c for c in [
        "player_id", "player_display_name", "position", "team", "opponent_team",
        "season", "week", "targets", "receptions", "receiving_yards",
        "receiving_tds", "receiving_air_yards", "target_share", "air_yards_share",
        "wopr", "racr", "carries", "rushing_yards", "rushing_tds",
        "attempts", "completions", "passing_yards", "passing_tds",
        "passing_epa", "receiving_epa", "fantasy_points_ppr",
    ] if c in recent.columns]
    out = recent[cols].copy()

    if not snaps.empty and "gsis_id" in snaps.columns:
        snap_cols = ["gsis_id", "season", "week", "offense_pct", "offense_snaps"]
        available = [c for c in snap_cols if c in snaps.columns]
        if {"gsis_id", "week"} <= set(available):
            out = out.merge(
                snaps[available].rename(columns={"gsis_id": "player_id"}),
                how="left", on=[c for c in ["player_id", "season", "week"]
                                if c in available or c == "player_id"],
            )

    return out.sort_values(["week", "fantasy_points_ppr"],
                           ascending=[False, False]).reset_index(drop=True)


def build_injuries_tab(injuries: pd.DataFrame) -> pd.DataFrame:
    if injuries.empty:
        return pd.DataFrame()
    keep = [c for c in [
        "season", "week", "team", "gsis_id", "full_name", "position",
        "report_primary_injury", "report_status",
        "practice_primary_injury", "practice_status",
    ] if c in injuries.columns]
    out = injuries[keep].copy()
    if "week" in out.columns:
        out = out.sort_values(["week", "team"], ascending=[False, True])
    return out.reset_index(drop=True)


# ============================================================================
# GOOGLE SHEETS
# ============================================================================

def write_to_sheets(client, sheet_id: str, tabs: dict) -> None:
    sheet = client.open_by_key(sheet_id)
    for tab_name, df in tabs.items():
        if df is None:
            continue
        if df.empty:
            # Writing an empty frame would wipe a tab that still holds usable
            # data from a previous run — skip instead. Same reasoning as the
            # MLB engine's empty-tab guard (see MLBDesktop ENGINE_AUDIT.md).
            print(f"   ⏭️  {tab_name}: empty, leaving existing tab untouched")
            continue
        try:
            ws = sheet.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            ws = sheet.add_worksheet(title=tab_name,
                                     rows=max(len(df) + 10, 100),
                                     cols=max(len(df.columns) + 5, 26))
            print(f"   ➕ created tab {tab_name}")
        ws.clear()
        # Sheets rejects NaN/NaT in JSON, and datetimes need to be strings.
        clean = df.copy()
        for col in clean.columns:
            if pd.api.types.is_datetime64_any_dtype(clean[col]):
                clean[col] = clean[col].astype(str)
        clean = clean.where(pd.notna(clean), "")
        set_with_dataframe(ws, clean, include_index=False, resize=True)
        print(f"   ✅ {tab_name}: {len(clean)} rows × {len(clean.columns)} cols")


# ============================================================================
# MAIN
# ============================================================================

def main():
    started = datetime.now(eastern)
    print(f"🏈 {SPORT_LABEL} Engine v1.1 — {started:%Y-%m-%d %H:%M:%S %Z}")

    odds_api_key = load_secret("ODDS_API_KEY", "🔑 Odds API Key: ", allow_missing=True)

    # nflverse labels a season by its September start, so Jan–Aug reports the
    # prior year. Ahead of kickoff, that prior season is the projection baseline.
    stats_season = nv.current_season()
    schedule_season = stats_season + 1 if started.month >= 3 else stats_season
    print(f"📅 stats baseline: {stats_season} · schedule: {schedule_season}")

    print("\n📡 nflverse")
    teams = nv.load_teams()
    print(f"   teams: {len(teams)}")

    schedule = nv.load_schedules(seasons=[schedule_season])
    if schedule.empty:
        print(f"   ⚠️  no {schedule_season} schedule — falling back to {stats_season}")
        schedule = nv.load_schedules(seasons=[stats_season])
    print(f"   schedule: {len(schedule)} games")

    stats = nv.load_player_stats(seasons=[stats_season])
    print(f"   player stats: {len(stats)} rows")

    snaps = nv.attach_gsis_id(nv.load_snap_counts(seasons=[stats_season]))
    print(f"   snap counts: {len(snaps)} rows")

    injuries = nv.load_injuries(seasons=[stats_season])
    print(f"   injuries: {len(injuries)} rows")

    print("\n📡 Odds API")
    odds = pd.DataFrame()
    props = pd.DataFrame()
    board = pd.DataFrame()

    if not odds_api_key:
        print("   ⚠️  no Odds API key — skipping live odds and props")
    else:
        odds_api = oc.OddsClient(odds_api_key, quota_floor=QUOTA_FLOOR_THIS_SPORT)
        try:
            odds = extract_book_odds(odds_api.fetch_featured())
            print(f"   featured odds: {len(odds)} games")

            if SKIP_PROPS:
                print("   ⏭️  props skipped (NFL_SKIP_PROPS set)")
            else:
                # /events is free, so narrowing the window costs nothing and
                # avoids paying per-event for games books haven't priced yet.
                upcoming = odds_api.fetch_events(within_days=PROPS_WINDOW_DAYS)
                print(f"   events within {PROPS_WINDOW_DAYS}d: {len(upcoming)} (free call)")

                if upcoming:
                    props = oc.add_fair_prices(odds_api.fetch_props(upcoming))
                    board = oc.best_price_board(props)
                    if props.empty:
                        print("   ℹ️  no props posted yet — books open these closer "
                              "to kickoff (empty responses are not charged)")
                    else:
                        print(f"   props: {len(props)} quotes · "
                              f"{props['player'].nunique()} players · "
                              f"{len(board)} unique lines")
        except oc.QuotaExhausted as e:
            # Keep whatever was already fetched and still write the sheet —
            # a partial refresh beats leaving the dashboard on stale data.
            print(f"   {e}")

        print(f"   💳 credits spent this run: {odds_api.spent} · remaining: {odds_api.remaining}")

    print("\n🔧 Building tabs")
    name_map = build_team_name_map(teams)
    tabs = {
        "Games": build_games_tab(schedule, odds, name_map),
        "Teams": build_teams_tab(teams),
        "PlayerForm": build_player_form_tab(stats, snaps),
        "Injuries": build_injuries_tab(injuries),
        "PlayerProps": props,
        "PropsBoard": board,
    }

    print("\n📝 Writing to Google Sheets")
    sheets = get_gspread_client()
    write_to_sheets(sheets, SHEET_ID, tabs)

    elapsed = (datetime.now(eastern) - started).total_seconds()
    print(f"\n✅ Complete in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
