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
import projections as pj

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

# FantasyPros publishes separate ranking sets per format. The 'best-*' pages are
# best ball (ecr_type bo/bp) — distinct from 'redraft-*' and 'dynasty-*'.
BEST_BALL_PAGES = ["best-overall"]

# Underdog best ball is 0.5 PPR with 4-point passing TDs. Override with
# NFL_SCORING=ppr|half|standard|underdog if drafting a different format.
SCORING = os.getenv("NFL_SCORING", pj.DEFAULT_SCORING)

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
# MLB-CONTRACT TABS
# ============================================================================
# app.js is ported from MLBDesktop, so it expects that dashboard's tab and
# column contract. Its rowField() aliasing layer accepts either UPPER_SNAKE or
# lower_snake, so these builders emit generous column sets and let the
# dashboard pick what it needs. Extra columns are harmless.

SKILL_POSITIONS = ["RB", "WR", "TE"]


def _slate_identity(df: pd.DataFrame) -> pd.DataFrame:
    """Add the identity aliases every dashboard view expects."""
    out = df.copy()
    if "player_display_name" in out.columns:
        out["player_name"] = out["player_display_name"]
    if "team" in out.columns:
        out["team_abbr"] = out["team"]
    if "opponent_team" in out.columns:
        out["opp_abbr"] = out["opponent_team"]
    if "position" in out.columns:
        out["pos"] = out["position"]
    return out


def build_slate_tab(stats: pd.DataFrame, snaps: pd.DataFrame,
                    positions: list[str]) -> pd.DataFrame:
    """Season-to-date per-player aggregate for one position group.

    This is the "who's available and how are they used" surface. Pre-season it
    reflects last season, which is the correct projection baseline anyway.
    """
    if stats.empty or "position" not in stats.columns:
        return pd.DataFrame()

    pool = stats[stats["position"].isin(positions)].copy()
    if pool.empty:
        return pd.DataFrame()

    sum_cols = [c for c in [
        "targets", "receptions", "receiving_yards", "receiving_tds",
        "receiving_air_yards", "carries", "rushing_yards", "rushing_tds",
        "attempts", "completions", "passing_yards", "passing_tds",
        "passing_interceptions", "fantasy_points_ppr",
    ] if c in pool.columns]
    mean_cols = [c for c in [
        "target_share", "air_yards_share", "wopr", "racr",
        "passing_epa", "receiving_epa",
    ] if c in pool.columns]

    grouped = pool.groupby(["player_id", "player_display_name", "position"], dropna=False)
    agg = grouped.agg(
        {**{c: "sum" for c in sum_cols}, **{c: "mean" for c in mean_cols}}
    ).reset_index()
    agg["games"] = grouped.size().values

    # Latest team/opponent, so the slate reflects current affiliation rather
    # than whoever they played for in week 1.
    latest = (pool.sort_values("week")
                  .groupby("player_id", as_index=False)
                  .last()[["player_id", "team", "opponent_team"]])
    agg = agg.merge(latest, how="left", on="player_id")

    if not snaps.empty and "gsis_id" in snaps.columns and "offense_pct" in snaps.columns:
        snap_avg = (snaps.groupby("gsis_id", as_index=False)["offense_pct"]
                         .mean().rename(columns={"gsis_id": "player_id",
                                                 "offense_pct": "snap_pct"}))
        agg = agg.merge(snap_avg, how="left", on="player_id")

    for c in mean_cols + (["snap_pct"] if "snap_pct" in agg.columns else []):
        agg[c] = agg[c].round(4)

    agg = _slate_identity(agg)
    sort_col = "fantasy_points_ppr" if "fantasy_points_ppr" in agg.columns else "games"
    return agg.sort_values(sort_col, ascending=False).reset_index(drop=True)


def build_game_logs_tab(stats: pd.DataFrame, positions: list[str]) -> pd.DataFrame:
    """Per-week game logs for one position group — powers the log charts."""
    if stats.empty or "position" not in stats.columns:
        return pd.DataFrame()
    logs = stats[stats["position"].isin(positions)].copy()
    if logs.empty:
        return pd.DataFrame()

    keep = [c for c in [
        "player_id", "player_display_name", "position", "season", "week",
        "team", "opponent_team", "targets", "receptions", "receiving_yards",
        "receiving_tds", "receiving_air_yards", "target_share",
        "air_yards_share", "wopr", "racr", "carries", "rushing_yards",
        "rushing_tds", "attempts", "completions", "passing_yards",
        "passing_tds", "passing_interceptions", "fantasy_points_ppr",
    ] if c in logs.columns]
    out = _slate_identity(logs[keep])
    out["game_date"] = ""  # filled from Schedule join downstream
    return out.sort_values(["player_display_name", "week"]).reset_index(drop=True)


def build_schedule_tab(schedule: pd.DataFrame) -> pd.DataFrame:
    """Schedule with the home_abbr/away_abbr aliases the dashboard joins on."""
    if schedule.empty:
        return pd.DataFrame()
    out = schedule.copy()
    if "home_team" in out.columns:
        out["home_abbr"] = out["home_team"]
    if "away_team" in out.columns:
        out["away_abbr"] = out["away_team"]
    if "gameday" in out.columns:
        out["game_date"] = out["gameday"]
    if "gametime" in out.columns:
        out["game_time"] = out["gametime"]
    return out


def build_team_rankings_tab(team_stats: pd.DataFrame) -> pd.DataFrame:
    """Season team aggregates, used for matchup context and Leaders."""
    if team_stats.empty:
        return pd.DataFrame()
    out = team_stats.copy()
    if "team" in out.columns:
        out["team_abbr"] = out["team"]
    return out


def build_dk_props_tab(board: pd.DataFrame) -> pd.DataFrame:
    """Best-price board in MLB's DK_Player_Props column contract.

    Column names are UPPER_SNAKE because the ported prop renderers read
    p.PLAYER_NAME / p.METRIC / p.DK_LINE / p.OVER_ODDS / p.UNDER_ODDS directly
    rather than through the aliasing layer.
    """
    if board.empty:
        return pd.DataFrame()
    out = pd.DataFrame({
        "PLAYER_NAME": board["player"],
        "METRIC": board["metric"],
        "DK_LINE": board["line"],
        "OVER_ODDS": board.get("best_over_odds"),
        "UNDER_ODDS": board.get("best_under_odds"),
        "BOOK": board.get("best_over_book"),
        "REFERENCE_BOOK": board.get("best_over_book"),
        "BEST_OVER_BOOK": board.get("best_over_book"),
        "BEST_OVER_ODDS": board.get("best_over_odds"),
        "BEST_UNDER_BOOK": board.get("best_under_book"),
        "BEST_UNDER_ODDS": board.get("best_under_odds"),
        "BOOKS_QUOTING": board.get("books_quoting"),
        "GAME": board.get("event_away", "") + " @ " + board.get("event_home", ""),
        "LAST_UPDATED": board.get("commence_time"),
    })
    return out.reset_index(drop=True)


def build_all_books_props_tab(props: pd.DataFrame) -> pd.DataFrame:
    """Every per-book quote in MLB's All_Books_Props contract."""
    if props.empty:
        return pd.DataFrame()
    out = pd.DataFrame({
        "PLAYER_NAME": props["player"],
        "METRIC": props["metric"],
        "LINE": props["line"],
        "BOOK": props["book"],
        "OVER_ODDS": props.get("over_odds"),
        "UNDER_ODDS": props.get("under_odds"),
        "OVER_IMPLIED": props.get("fair_over_prob"),
        "UNDER_IMPLIED": props.get("fair_under_prob"),
        "HOLD": props.get("hold"),
        "LAST_UPDATED": props.get("last_update"),
    })
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
        # Stamp the tab's own name so the dashboard can prove it got the sheet
        # it asked for. gviz returns the FIRST sheet's data (HTTP 200) when a
        # tab doesn't exist, and column fingerprints can't catch it because
        # Schedule and Games legitimately share columns like game_id.
        clean["_tab"] = tab_name
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

    team_stats = nv.load_team_stats(seasons=[stats_season])
    print(f"   team stats: {len(team_stats)} rows")

    # Roster year runs ahead of the stats year — that's the point here, since
    # projections need who's on which team NOW, not last season.
    rosters_now = nv.load_rosters(seasons=[schedule_season])
    if rosters_now.empty:
        print(f"   ⚠️  no {schedule_season} rosters — falling back to {stats_season}")
        rosters_now = nv.load_rosters(seasons=[stats_season])
    print(f"   rosters {schedule_season}: {len(rosters_now)} rows")

    print("\n📈 Projections")
    best_ball_ecr = nv.load_ff_rankings("draft", page_types=BEST_BALL_PAGES)
    ff_ids = nv.load_ff_playerids()
    print(f"   best-ball consensus: {len(best_ball_ecr)} ranked")
    print(f"   scoring: {SCORING} ({pj.SCORING_FORMATS.get(SCORING, '?')} per reception)")
    projections = pj.build_projections(stats, rosters_now, best_ball_ecr, ff_ids,
                                       scoring=SCORING)
    if not projections.empty:
        # Stamp the format so the dashboard can label the board rather than
        # assuming PPR — the point totals are meaningless without it.
        projections["scoring_format"] = SCORING
    print(f"   projections: {len(projections)} players")

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
    games_tab = build_games_tab(schedule, odds, name_map)

    tabs = {
        # Tabs the ported MLB dashboard reads
        "Schedule": build_schedule_tab(games_tab),
        "Slate_Skill": build_slate_tab(stats, snaps, SKILL_POSITIONS),
        "Slate_QB": build_slate_tab(stats, snaps, ["QB"]),
        "Skill_Game_Logs": build_game_logs_tab(stats, SKILL_POSITIONS),
        "QB_Game_Logs": build_game_logs_tab(stats, ["QB"]),
        "Team_Rankings": build_team_rankings_tab(team_stats),
        "DK_Player_Props": build_dk_props_tab(board),
        "All_Books_Props": build_all_books_props_tab(props),
        "Injuries": build_injuries_tab(injuries),
        "Projections": projections,
        # Kept for reference / direct inspection
        "Games": games_tab,
        "Teams": build_teams_tab(teams),
        "PlayerForm": build_player_form_tab(stats, snaps),
    }

    print("\n📝 Writing to Google Sheets")
    sheets = get_gspread_client()
    write_to_sheets(sheets, SHEET_ID, tabs)

    elapsed = (datetime.now(eastern) - started).total_seconds()
    print(f"\n✅ Complete in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
