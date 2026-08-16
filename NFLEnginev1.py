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

import nflverse_loader as nv
import odds_client as oc
import projections as pj
import picks as pk
from sports_common import col_letter, get_gspread_client

# ============================================================================
# CONFIGURATION
# ============================================================================

SPORT_LABEL = "NFL"
SHEET_ID = "1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0"
ODDS_SPORT = "americanfootball_nfl"
MODEL_VERSION = os.getenv("NFL_MODEL_VERSION", "nfl-2026-preseason-v1")
MODEL_ERA = os.getenv("NFL_MODEL_ERA", MODEL_VERSION)
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

# Picks generation runs on gamedays only — a "Wednesday practice-report" cron
# firing shouldn't also regenerate the board. Comma-separated day names,
# matched case-insensitively; add "Saturday,Friday" here once those become
# real gamedays later in the season, no code change needed.
PICKS_DAYS = {d.strip().lower() for d in
             os.getenv("NFL_PICKS_DAYS", "Thursday,Sunday,Monday").split(",") if d.strip()}
SKIP_PICKS = os.getenv("NFL_SKIP_PICKS", "").lower() in {"1", "true", "yes"}
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

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


# ============================================================================
# ODDS API
# ============================================================================
# Requests, retries, and quota accounting all live in odds_client.OddsClient.

def extract_book_odds(events: list, preferred="draftkings", fallback="fanduel") -> pd.DataFrame:
    """Flatten Odds API events to one row per game, preferring a single book.

    Prefer DraftKings, fall back to FanDuel, then whatever book is present, so
    a book dropping a market doesn't blank the row.
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
# DASHBOARD-CONTRACT TABS
# ============================================================================
# app.js was ported from MLBDesktop, so some tab and column names are shared.
# Its rowField() aliasing layer accepts either UPPER_SNAKE or lower_snake, so
# these builders emit generous column sets and let the dashboard pick what it
# needs. Extra columns are harmless.

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


def build_player_props_tab(board: pd.DataFrame) -> pd.DataFrame:
    """Best-price board in the dashboard's Player_Props column contract.

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
        "BEST_OVER_LAST_UPDATED": board.get("best_over_last_update"),
        "BEST_UNDER_BOOK": board.get("best_under_book"),
        "BEST_UNDER_ODDS": board.get("best_under_odds"),
        "BEST_UNDER_LAST_UPDATED": board.get("best_under_last_update"),
        "BOOKS_QUOTING": board.get("books_quoting"),
        "GAME": board.get("event_away", "") + " @ " + board.get("event_home", ""),
        "LAST_UPDATED": board.get("best_over_last_update").fillna(
            board.get("best_under_last_update")
        ).fillna(board.get("commence_time")),
    })
    return out.reset_index(drop=True)


def build_all_books_props_tab(props: pd.DataFrame) -> pd.DataFrame:
    """Every per-book quote in the dashboard's All_Books_Props contract."""
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


def _safe_records_df(ws) -> pd.DataFrame:
    try:
        records = ws.get_all_records(default_blank="")
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame(records or [])


def _add_prop_opening_snapshot(current: pd.DataFrame, prior: pd.DataFrame,
                               *, key_cols: list[str],
                               over_col: str = "OVER_ODDS",
                               under_col: str = "UNDER_ODDS",
                               over_book_col: str | None = None,
                               under_book_col: str | None = None,
                               last_updated_col: str = "LAST_UPDATED",
                               generated_at: str = "") -> pd.DataFrame:
    """Persist first-seen prices so later runs can measure movement.

    CLV needs an opening snapshot to compare against. The engine rewrites whole
    tabs each run, so without carrying the first seen price forward, every run
    becomes its own "open" and movement is lost.
    """
    if current.empty:
        return current

    out = current.copy()
    prior_lookup = {}
    if not prior.empty:
        missing = [c for c in key_cols if c not in prior.columns]
        if not missing:
            keyed = prior.drop_duplicates(subset=key_cols, keep="first")
            for _, row in keyed.iterrows():
                key = tuple(str(row.get(col, "")) for col in key_cols)
                prior_lookup[key] = row

    def implied(odds):
        value = oc.american_to_implied(odds)
        return None if pd.isna(value) else float(value)

    open_over, open_under = [], []
    open_over_book, open_under_book = [], []
    open_captured_at, over_delta_pp, under_delta_pp = [], [], []

    for _, row in out.iterrows():
        key = tuple(str(row.get(col, "")) for col in key_cols)
        prev = prior_lookup.get(key)

        prev_open_over = prev.get("OPEN_OVER_ODDS", "") if prev is not None else ""
        prev_open_under = prev.get("OPEN_UNDER_ODDS", "") if prev is not None else ""
        prev_open_over_book = prev.get("OPEN_OVER_BOOK", "") if prev is not None else ""
        prev_open_under_book = prev.get("OPEN_UNDER_BOOK", "") if prev is not None else ""
        prev_captured = prev.get("OPEN_CAPTURED_AT", "") if prev is not None else ""

        current_over = row.get(over_col, "")
        current_under = row.get(under_col, "")

        opening_over = prev_open_over if prev_open_over != "" else current_over
        opening_under = prev_open_under if prev_open_under != "" else current_under
        opening_over_book = prev_open_over_book if prev_open_over_book != "" else (row.get(over_book_col, "") if over_book_col else "")
        opening_under_book = prev_open_under_book if prev_open_under_book != "" else (row.get(under_book_col, "") if under_book_col else "")
        captured_at = prev_captured if prev_captured != "" else row.get(last_updated_col, "") or generated_at

        cur_over_prob = implied(current_over)
        open_over_prob = implied(opening_over)
        cur_under_prob = implied(current_under)
        open_under_prob = implied(opening_under)

        open_over.append(opening_over)
        open_under.append(opening_under)
        open_over_book.append(opening_over_book)
        open_under_book.append(opening_under_book)
        open_captured_at.append(captured_at)
        over_delta_pp.append(round((cur_over_prob - open_over_prob) * 100, 2) if cur_over_prob is not None and open_over_prob is not None else "")
        under_delta_pp.append(round((cur_under_prob - open_under_prob) * 100, 2) if cur_under_prob is not None and open_under_prob is not None else "")

    out["OPEN_OVER_ODDS"] = open_over
    out["OPEN_UNDER_ODDS"] = open_under
    out["OPEN_OVER_BOOK"] = open_over_book
    out["OPEN_UNDER_BOOK"] = open_under_book
    out["OPEN_CAPTURED_AT"] = open_captured_at
    out["OVER_CLV_DELTA_PP"] = over_delta_pp
    out["UNDER_CLV_DELTA_PP"] = under_delta_pp
    return out


# ============================================================================
# GOOGLE SHEETS
# ============================================================================

def write_to_sheets(
    client,
    sheet_id: str,
    tabs: dict,
    *,
    generated_at: str,
    model_version: str,
    model_era: str,
) -> None:
    sheet = client.open_by_key(sheet_id)
    for tab_name, df in tabs.items():
        if df is None:
            continue
        if df.empty:
            # Writing an empty frame would wipe a tab that still holds usable
            # data from a previous run, so skip instead.
            print(f"   ⏭️  {tab_name}: empty, leaving existing tab untouched")
            continue
        try:
            ws = sheet.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            ws = sheet.add_worksheet(title=tab_name,
                                     rows=max(len(df) + 10, 100),
                                     cols=max(len(df.columns) + 5, 26))
            print(f"   ➕ created tab {tab_name}")
            prior = pd.DataFrame()
        else:
            prior = _safe_records_df(ws)

        if tab_name == "All_Books_Props":
            df = _add_prop_opening_snapshot(
                df,
                prior,
                key_cols=["PLAYER_NAME", "METRIC", "LINE", "BOOK"],
                over_col="OVER_ODDS",
                under_col="UNDER_ODDS",
                over_book_col="BOOK",
                under_book_col="BOOK",
                last_updated_col="LAST_UPDATED",
                generated_at=generated_at,
            )
        elif tab_name == "Player_Props":
            df = _add_prop_opening_snapshot(
                df,
                prior,
                key_cols=["PLAYER_NAME", "METRIC", "DK_LINE", "GAME"],
                over_col="BEST_OVER_ODDS",
                under_col="BEST_UNDER_ODDS",
                over_book_col="BEST_OVER_BOOK",
                under_book_col="BEST_UNDER_BOOK",
                last_updated_col="LAST_UPDATED",
                generated_at=generated_at,
            )

        ws.clear()
        # Sheets rejects NaN/NaT in JSON, and datetimes need to be strings.
        clean = df.copy()
        # Stamp the tab's own name so the dashboard can prove it got the sheet
        # it asked for. gviz returns the FIRST sheet's data (HTTP 200) when a
        # tab doesn't exist, and column fingerprints can't catch it because
        # Schedule and Games legitimately share columns like game_id.
        clean["_tab"] = tab_name
        clean["_generated_at"] = generated_at
        clean["_model_version"] = model_version
        clean["_model_era"] = model_era
        for col in clean.columns:
            if pd.api.types.is_datetime64_any_dtype(clean[col]):
                clean[col] = clean[col].astype(str)
        clean = clean.where(pd.notna(clean), "")
        set_with_dataframe(ws, clean, include_index=False, resize=True)
        print(f"   ✅ {tab_name}: {len(clean)} rows × {len(clean.columns)} cols")


def build_week_games_str(schedule: pd.DataFrame, week: int) -> str:
    """Plain-text matchup block for this week, fed straight into the picks
    prompt — mirrors MLB's games_context text, simplified since NFL's weekly
    slate doesn't need per-game weather/starter context repeated per line
    (that's already on the per-prop player_ctx rows instead)."""
    if schedule.empty or "week" not in schedule.columns:
        return "(schedule unavailable)"
    games = schedule[schedule["week"] == week]
    if games.empty:
        return f"(no games found for week {week})"
    lines = []
    for _, g in games.sort_values("gameday").iterrows():
        lines.append(f"{g.get('away_team','?')} @ {g.get('home_team','?')} "
                     f"— {g.get('gameday','')} {g.get('gametime','')} "
                     f"(spread {g.get('spread_line','?')}, total {g.get('total_line','?')})")
    return "\n".join(lines)


def fetch_prior_daily_picks(client, sheet_id: str) -> pd.DataFrame:
    """Existing Daily_Picks rows, read before this run's picks are built.

    picks.assemble_pick_tabs() needs today's prior rows to compute RUN_NUMBER
    (max existing + 1) and to dedup same-day repeats — that has to happen
    before we know what to write, unlike every other tab here which is a
    stateless full rebuild each run.
    """
    try:
        sheet = client.open_by_key(sheet_id)
        ws = sheet.worksheet("Daily_Picks")
    except Exception:
        return pd.DataFrame()
    return _safe_records_df(ws)


def refresh_clv_daily_picks(client, sheet_id: str, props_board: pd.DataFrame, *,
                            timestamp_label: str, season: int, week: int) -> None:
    """Refresh CLV fields for the current NFL week on still-ungraded picks.

    NFL's board can stay live across Thu/Sun/Mon within the same week, so CLV
    is tracked by (season, week, player, metric, team) rather than by DATE.
    The current comparison line is chosen from the same player's currently
    posted lines using the nearest available line to the original pick line.
    """
    if props_board is None or props_board.empty:
        print("   ⏭️  Daily_Picks CLV: no current props board")
        return

    sheet = client.open_by_key(sheet_id)
    try:
        ws = sheet.worksheet("Daily_Picks")
    except gspread.exceptions.WorksheetNotFound:
        print("   ⏭️  Daily_Picks CLV: Daily_Picks tab missing")
        return

    values = ws.get_all_values()
    if not values:
        print("   ⏭️  Daily_Picks CLV: no rows yet")
        return

    header, rows = values[0], values[1:]
    if not rows:
        print("   ⏭️  Daily_Picks CLV: history empty")
        return

    clv_cols = ["CLV_OPEN_LINE", "CLV_LATEST_LINE", "CLV_DELTA", "CLV_LAST_UPDATE"]
    sheet_header = list(header)
    missing_clv = [col for col in clv_cols if col not in sheet_header]
    if missing_clv:
        sheet_header.extend(missing_clv)
        end_col = col_letter(len(sheet_header) - 1)
        ws.update(f"A1:{end_col}1", [sheet_header], value_input_option="RAW")
        header = sheet_header
        for row in rows:
            row.extend([""] * len(missing_clv))

    col_idx = {name: i for i, name in enumerate(header)}
    required = {"player", "team", "prop_type", "line", "SEASON", "WEEK", "HIT"}
    if not required.issubset(col_idx):
        print("   ⚠️  Daily_Picks CLV: required columns missing, skipping refresh")
        return

    line_map = {}
    for _, prop in props_board.iterrows():
        try:
            line_val = float(prop.get("line"))
        except (TypeError, ValueError):
            continue
        teams = {str(prop.get("event_home", "")).strip().upper(),
                 str(prop.get("event_away", "")).strip().upper()}
        teams.discard("")
        if not teams:
            continue
        key_base = (pk._norm_name(prop.get("player", "")),
                    str(prop.get("metric", "")).strip().upper())
        for team in teams:
            line_map.setdefault((*key_base, team), []).append(line_val)

    updates = []
    refreshed = 0
    for row_num, row in enumerate(rows, start=2):
        hit_val = str(row[col_idx["HIT"]]).strip().upper()
        if hit_val:
            continue
        try:
            row_season = int(float(row[col_idx["SEASON"]]))
            row_week = int(float(row[col_idx["WEEK"]]))
        except (TypeError, ValueError):
            continue
        if row_season != season or row_week != week:
            continue

        player_key = pk._norm_name(row[col_idx["player"]])
        metric = str(row[col_idx["prop_type"]]).strip().upper()
        team = str(row[col_idx["team"]]).strip().upper()
        candidates = line_map.get((player_key, metric, team), [])
        if not candidates:
            continue

        open_raw = row[col_idx["CLV_OPEN_LINE"]] or row[col_idx["line"]]
        try:
            open_line = float(open_raw)
        except (TypeError, ValueError):
            continue
        latest_line = min(candidates, key=lambda val: abs(val - open_line))
        delta = round(latest_line - open_line, 1)

        updates.extend([
            {"range": f"{col_letter(col_idx['CLV_OPEN_LINE'])}{row_num}", "values": [[f"{open_line:g}"]]},
            {"range": f"{col_letter(col_idx['CLV_LATEST_LINE'])}{row_num}", "values": [[f"{latest_line:g}"]]},
            {"range": f"{col_letter(col_idx['CLV_DELTA'])}{row_num}", "values": [[f"{delta:g}"]]},
            {"range": f"{col_letter(col_idx['CLV_LAST_UPDATE'])}{row_num}", "values": [[timestamp_label]]},
        ])
        refreshed += 1

    if updates:
        ws.batch_update(updates)
        print(f"   ✅ Daily_Picks CLV: refreshed {refreshed} row(s)")
    else:
        print("   ⏭️  Daily_Picks CLV: nothing eligible to refresh")


def append_daily_picks(client, sheet_id: str, df: pd.DataFrame, *,
                       generated_at: str, model_version: str, model_era: str) -> None:
    """Append-only write for Daily_Picks — the one tab that must never be
    cleared, since it's the pick history the grader and Pick_Performance
    depend on. Every other tab in write_to_sheets() is a full stateless
    rebuild; this one is deliberately not.
    """
    if df.empty:
        print("   ⏭️  Daily_Picks: no new picks to append")
        return

    clean = df.copy()
    clean["_tab"] = "Daily_Picks"
    clean["_generated_at"] = generated_at
    clean["_model_version"] = model_version
    clean["_model_era"] = model_era
    clean = clean.where(pd.notna(clean), "")
    # Fixed column order matters here in a way it doesn't for the clear+rewrite
    # tabs: append_rows appends by POSITION, not by header name, so a reordered
    # frame would silently write values into the wrong columns of existing rows.
    cols = list(clean.columns)

    sheet = client.open_by_key(sheet_id)
    try:
        ws = sheet.worksheet("Daily_Picks")
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title="Daily_Picks",
                                 rows=max(len(clean) + 500, 1000),
                                 cols=max(len(cols) + 5, 40))
        set_with_dataframe(ws, clean[cols], include_index=False, resize=True)
        print(f"   ➕ created Daily_Picks, {len(clean)} row(s)")
        return

    sheet_header = ws.row_values(1)
    if sheet_header:
        missing_in_sheet = [c for c in cols if c not in sheet_header]
        if missing_in_sheet:
            sheet_header = sheet_header + missing_in_sheet
            end_col = col_letter(len(sheet_header) - 1)
            ws.update(f"A1:{end_col}1", [sheet_header], value_input_option="RAW")
        for col in sheet_header:
            if col not in clean.columns:
                clean[col] = ""
        cols = sheet_header

    rows = clean[cols].astype(str).values.tolist()
    ws.append_rows(rows, value_input_option="RAW")
    print(f"   ✅ Daily_Picks: appended {len(rows)} row(s)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    started = datetime.now(eastern)
    generated_at = started.strftime("%Y-%m-%d %H:%M:%S %Z")
    print(f"🏈 {SPORT_LABEL} Engine v1.1 — {generated_at}")
    print(f"🧬 model version: {MODEL_VERSION} · era: {MODEL_ERA}")

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
    # "latest" is correct for the upcoming season — the newest snapshot is the
    # current pre-season depth chart.
    depth = nv.depth_ranks(seasons=[schedule_season], snapshot="latest")
    print(f"   depth chart: {len(depth)} players")
    projections = pj.build_projections(stats, rosters_now, best_ball_ecr, ff_ids,
                                       scoring=SCORING, depth=depth)
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
    skill_logs = build_game_logs_tab(stats, SKILL_POSITIONS)
    qb_logs = build_game_logs_tab(stats, ["QB"])

    # Authorized once here rather than per-use — picks needs it early to read
    # prior Daily_Picks state, and the final write below reuses this same
    # client instead of re-authorizing.
    try:
        sheets = get_gspread_client()
        svc_json = (os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
                    or os.environ.get("GSPREAD_SERVICE_ACCOUNT_JSON"))
        if svc_json:
            info = json.loads(svc_json)
            print(f"✅ Google auth via env ({info.get('client_email', 'unknown')})")
        else:
            key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
            print(f"✅ Google auth via key file ({os.path.basename(key_path)})")
    except RuntimeError as e:
        if "No Google credentials found" in str(e):
            raise RuntimeError(
                "No Google credentials found — neither GOOGLE_SERVICE_ACCOUNT_JSON nor "
                "GOOGLE_APPLICATION_CREDENTIALS is set (both were empty, not invalid).\n"
                "  • GitHub Actions: add a repo secret named GOOGLE_SERVICE_ACCOUNT_JSON "
                "containing the full service-account JSON content.\n"
                "  • Local: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json\n"
                "Then confirm the Sheet is shared with that key's client_email as Editor."
            ) from e
        raise

    print("\n🎯 Weekly Picks")
    picks_current = pd.DataFrame()
    daily_picks_new = pd.DataFrame()
    current_weekday = started.strftime("%A")
    week = nv.current_week(schedule)

    if SKIP_PICKS:
        print("   ⏭️  picks skipped (NFL_SKIP_PICKS set)")
    elif current_weekday.lower() not in PICKS_DAYS:
        print(f"   ⏭️  {current_weekday} is not a picks day "
              f"({', '.join(sorted(PICKS_DAYS))}) — leaving Picks_Current as-is")
    elif week is None:
        print("   ⚠️  could not determine current week — skipping picks")
    elif board.empty:
        # No real market lines yet means nothing to validate a pick against —
        # generating anyway would mean either inventing lines or running the
        # deterministic fallback on zero data. Neither is worth doing.
        print("   ⏭️  no player props posted yet — skipping picks generation")
    else:
        gemini_key = load_secret("GEMINI_API_KEY", "🤖 Gemini API Key: ", allow_missing=True)
        all_logs = pd.concat([skill_logs, qb_logs], ignore_index=True) if not qb_logs.empty else skill_logs
        player_ctx = pk.build_player_context(board, all_logs, projections, injuries)
        print(f"   player context: {len(player_ctx)} priced prop rows")

        games_str = build_week_games_str(schedule, week)
        fresh_picks = pk.generate_weekly_picks(gemini_key, GEMINI_MODEL, player_ctx,
                                               games_str, week=week, season=schedule_season)
        prior_daily = fetch_prior_daily_picks(sheets, SHEET_ID)
        picks_current, daily_picks_new = pk.assemble_pick_tabs(
            fresh_picks, prior_daily, week=week, season=schedule_season)
        print(f"   picks: {len(picks_current)} current · {len(daily_picks_new)} new to Daily_Picks")

    tabs = {
        # Tabs the NFL dashboard reads
        "Schedule": build_schedule_tab(games_tab),
        "Slate_Skill": build_slate_tab(stats, snaps, SKILL_POSITIONS),
        "Slate_QB": build_slate_tab(stats, snaps, ["QB"]),
        "Skill_Game_Logs": skill_logs,
        "QB_Game_Logs": qb_logs,
        "Team_Rankings": build_team_rankings_tab(team_stats),
        "Player_Props": build_player_props_tab(board),
        "All_Books_Props": build_all_books_props_tab(props),
        "Injuries": build_injuries_tab(injuries),
        "Projections": projections,
        "Picks_Current": picks_current,
        # Kept for reference / direct inspection
        "Games": games_tab,
        "Teams": build_teams_tab(teams),
        "PlayerForm": build_player_form_tab(stats, snaps),
    }

    print("\n📝 Writing to Google Sheets")
    write_to_sheets(
        sheets,
        SHEET_ID,
        tabs,
        generated_at=generated_at,
        model_version=MODEL_VERSION,
        model_era=MODEL_ERA,
    )
    append_daily_picks(sheets, SHEET_ID, daily_picks_new,
                       generated_at=generated_at,
                       model_version=MODEL_VERSION, model_era=MODEL_ERA)
    if not board.empty and week is not None:
        refresh_clv_daily_picks(
            sheets,
            SHEET_ID,
            board,
            timestamp_label=generated_at,
            season=schedule_season,
            week=week,
        )

    elapsed = (datetime.now(eastern) - started).total_seconds()
    print(f"\n✅ Complete in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
