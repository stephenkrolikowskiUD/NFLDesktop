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
from sports_common import (
    col_letter,
    DEFAULT_GOOGLE_CREDENTIAL_PATHS,
    get_gspread_client,
    load_secret,
    safe_records_df,
)

# ============================================================================
# CONFIGURATION
# ============================================================================

SPORT_LABEL = "NFL"
SHEET_ID = os.getenv("NFL_SHEET_ID", "1lcwCUprWZA8JWTfuI8cTGaKXZwvDmQ80E0bH3AVimkY")
REGULAR_SEASON_ODDS_SPORT = "americanfootball_nfl"
PRESEASON_ODDS_SPORT = "americanfootball_nfl_preseason"
MODEL_VERSION_OVERRIDE = os.getenv("NFL_MODEL_VERSION", "").strip()
MODEL_ERA_OVERRIDE = os.getenv("NFL_MODEL_ERA", "").strip()
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
KEEP_REFERENCE_TABS = os.getenv("NFL_KEEP_REFERENCE_TABS", "").lower() in {"1", "true", "yes"}

eastern = pytz.timezone("US/Eastern")

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


def _schedule_kickoff_series(schedule: pd.DataFrame) -> pd.Series:
    if schedule.empty:
        return pd.Series(dtype="datetime64[ns]")
    dates = schedule.get("gameday", pd.Series("", index=schedule.index)).astype(str)
    times = schedule.get("gametime", pd.Series("00:00", index=schedule.index)).astype(str)
    return pd.to_datetime(dates + " " + times, errors="coerce")


def _preseason_week_for_kickoff(kickoff: pd.Timestamp, regular_opener: pd.Timestamp | None) -> int:
    """Stable negative week numbers for preseason slates."""
    if pd.isna(kickoff):
        return -1
    if regular_opener is None or pd.isna(regular_opener):
        return -1
    days_before_opener = max(0, (regular_opener.normalize() - kickoff.normalize()).days)
    return -int(days_before_opener // 7 + 1)


def stamp_preseason_weeks(games: pd.DataFrame) -> pd.DataFrame:
    """Fill missing week values on synthetic preseason rows.

    Synthetic PRE rows come from live odds when nflverse has not exposed a
    preseason schedule spine yet. Leaving those blank forces later logic to
    borrow the regular-season current week, which is how preseason picks ended
    up stamped as Week 1. Negative preseason weeks keep those rows distinct.
    """
    if games.empty or "game_type" not in games.columns or "week" not in games.columns:
        return games

    out = games.copy()
    out["_kickoff"] = _schedule_kickoff_series(out)
    game_type = out["game_type"].astype(str).str.upper()
    week_num = pd.to_numeric(out["week"], errors="coerce")
    reg_kickoffs = out.loc[game_type.eq("REG") & out["_kickoff"].notna(), "_kickoff"]
    regular_opener = reg_kickoffs.min() if not reg_kickoffs.empty else None
    needs_week = game_type.eq("PRE") & week_num.isna() & out["_kickoff"].notna()
    if needs_week.any():
        out.loc[needs_week, "week"] = out.loc[needs_week, "_kickoff"].apply(
            lambda kickoff: _preseason_week_for_kickoff(kickoff, regular_opener)
        ).astype(int)
    return out.drop(columns="_kickoff", errors="ignore")


def current_preseason_week(games: pd.DataFrame, now: datetime) -> int | None:
    """Resolve the active preseason week from the actual PRE slate in games_tab."""
    if games.empty or "game_type" not in games.columns or "week" not in games.columns:
        return None

    pre = games[games["game_type"].astype(str).str.upper().eq("PRE")].copy()
    if pre.empty:
        return None
    pre["_kickoff"] = _schedule_kickoff_series(pre)
    pre["week_num"] = pd.to_numeric(pre["week"], errors="coerce")
    pre = pre[pre["_kickoff"].notna() & pre["week_num"].notna()].sort_values("_kickoff")
    if pre.empty:
        return None

    now_ts = pd.Timestamp(now)
    if now_ts.tzinfo is not None:
        now_ts = now_ts.tz_localize(None)
    upcoming = pre[pre["_kickoff"] >= now_ts]
    sample = upcoming if not upcoming.empty else pre
    return int(sample.iloc[0]["week_num"])


def has_live_game_market_odds(games: pd.DataFrame, *, game_type: str | None = None) -> bool:
    """Only count real live-book fields, not baseline schedule market data."""
    if games.empty:
        return False

    sample = games.copy()
    if game_type and "game_type" in sample.columns:
        sample = sample[sample["game_type"].astype(str).str.upper().eq(game_type.upper())]
    if sample.empty:
        return False

    live_cols = [
        "live_home_spread", "live_away_spread",
        "live_home_spread_odds", "live_away_spread_odds",
        "live_total", "live_over_odds", "live_under_odds",
        "live_home_ml", "live_away_ml",
    ]
    available = [col for col in live_cols if col in sample.columns]
    if not available:
        return False
    return sample[available].apply(pd.to_numeric, errors="coerce").notna().any(axis=None)


def resolve_model_identity(schedule_season: int, odds_sport: str) -> tuple[str, str]:
    """Prevent regular-season picks from inheriting the preseason model label."""
    phase = "preseason" if odds_sport == PRESEASON_ODDS_SPORT else "regular-season"
    model_version = MODEL_VERSION_OVERRIDE or f"nfl-{schedule_season}-{phase}-v1"
    model_era = MODEL_ERA_OVERRIDE or model_version
    return model_version, model_era


def log_launch_readiness(odds_sport: str, model_version: str, model_era: str) -> None:
    """Make launch-sensitive config obvious in the run log."""
    if odds_sport != PRESEASON_ODDS_SPORT:
        if not MODEL_VERSION_OVERRIDE or not MODEL_ERA_OVERRIDE:
            print("⚠️  regular-season model identity is using code defaults — "
                  "set NFL_MODEL_VERSION and NFL_MODEL_ERA explicitly in the workflow before Week 1")
        if model_version == model_era:
            print("   ℹ️  model era matches model version for this run")
    else:
        if MODEL_VERSION_OVERRIDE or MODEL_ERA_OVERRIDE:
            print("   ℹ️  preseason run is using explicit model identity overrides")


def log_pick_generation_outcome(*, preseason_team_markets_live: bool, board: pd.DataFrame,
                                player_ctx: pd.DataFrame | None = None,
                                gemini_key_present: bool = False,
                                fresh_picks: pd.DataFrame | None = None) -> None:
    """Explain why a run produced no picks, instead of leaving a silent zero."""
    if preseason_team_markets_live:
        if fresh_picks is not None and fresh_picks.empty:
            print("   ⚠️  preseason team-market mode found no qualified rows — "
                  "inspect Game_Markets / live odds before kickoff")
        return

    if board.empty:
        return

    board_rows = len(board)
    player_ctx_rows = 0 if player_ctx is None else len(player_ctx)
    fresh_rows = 0 if fresh_picks is None else len(fresh_picks)

    if not gemini_key_present:
        print("   ⚠️  live player props are present but GEMINI_API_KEY is missing — "
              "the board can only use deterministic fallback")

    if fresh_rows > 0:
        return

    if player_ctx_rows == 0:
        print(f"   ⚠️  {board_rows} player-prop line(s) were live, but none survived "
              "player-context assembly — inspect projections / logs / injuries joins")
        return

    print(f"   ⚠️  {board_rows} player-prop line(s) and {player_ctx_rows} priced context row(s) "
          "were available, but picks generation returned 0 rows — inspect Gemini output or validation gates")


def resolve_odds_sport(schedule: pd.DataFrame, now: datetime) -> str:
    """Choose the Odds API sport key from the actual next slate.

    An env override always wins. Otherwise, look at the next scheduled kickoff:
    if that slate is preseason, request preseason odds; once the next slate is
    regular season, switch back automatically.
    """
    override = os.getenv("NFL_ODDS_SPORT", "").strip()
    if override:
        return override

    if schedule.empty or "game_type" not in schedule.columns:
        return REGULAR_SEASON_ODDS_SPORT

    sched = schedule.copy()
    sched["_kickoff"] = _schedule_kickoff_series(sched)
    # Schedule kickoffs are parsed as naive wall-clock timestamps from nflverse.
    # `started` is timezone-aware Eastern, so compare on the same naive footing
    # rather than mixing aware/naive pandas timestamps.
    now_ts = pd.Timestamp(now)
    if now_ts.tzinfo is not None:
        now_ts = now_ts.tz_localize(None)
    kickoff_rows = sched[sched["_kickoff"].notna()].sort_values("_kickoff")
    upcoming = sched[sched["_kickoff"] >= now_ts].sort_values("_kickoff")
    sample = upcoming if not upcoming.empty else sched.sort_values("_kickoff")
    if sample.empty:
        return REGULAR_SEASON_ODDS_SPORT

    next_type = str(sample.iloc[0].get("game_type", "")).strip().upper()
    has_preseason_rows = sched["game_type"].astype(str).str.upper().eq("PRE").any()
    earliest_kickoff = kickoff_rows["_kickoff"].iloc[0] if not kickoff_rows.empty else None

    # Some nflverse schedule pulls expose only the 272-game regular-season slate
    # even while the real calendar is still in preseason. In that case the next
    # visible kickoff is Week 1, but we still want preseason odds until the
    # regular-season opener is close enough to be the actual active slate.
    if (not has_preseason_rows and next_type == "REG" and earliest_kickoff is not None
            and now_ts.month == 8
            and now_ts < earliest_kickoff
            and (earliest_kickoff - now_ts).days <= 35):
        return PRESEASON_ODDS_SPORT

    return PRESEASON_ODDS_SPORT if next_type == "PRE" else REGULAR_SEASON_ODDS_SPORT


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
        schedule_keys = set(zip(games["home_team"], games["away_team"]))
        games = games.merge(
            odds[["home_abbr", "away_abbr"] + odds_cols],
            how="left",
            left_on=["home_team", "away_team"],
            right_on=["home_abbr", "away_abbr"],
        ).drop(columns=["home_abbr", "away_abbr"], errors="ignore")

        # In late August the schedule feed can still be regular-season only
        # even while the Odds API correctly returns live preseason games. When
        # that happens, none of those odds rows have a schedule spine to merge
        # onto, so the live preseason board would otherwise disappear inside
        # games_tab and the preseason picker would emit 0 rows. Preserve those
        # unmatched odds rows as odds-only PRE games instead.
        unmatched = odds[
            ~odds.apply(
                lambda row: (row.get("home_abbr"), row.get("away_abbr")) in schedule_keys,
                axis=1,
            )
        ].copy()
        if not unmatched.empty:
            kickoff = pd.to_datetime(unmatched["commence_time"], utc=True, errors="coerce")
            kickoff_est = kickoff.dt.tz_convert(eastern)
            extras = pd.DataFrame({
                "game_id": "",
                "season": kickoff_est.dt.year.fillna(pd.Timestamp.now(tz=eastern).year).astype(int),
                "game_type": "PRE",
                "week": "",
                "gameday": kickoff_est.dt.strftime("%Y-%m-%d"),
                "weekday": kickoff_est.dt.strftime("%A"),
                "gametime": kickoff_est.dt.strftime("%I:%M %p").str.lstrip("0"),
                "away_team": unmatched["away_abbr"].astype(str),
                "home_team": unmatched["home_abbr"].astype(str),
                "away_score": pd.NA,
                "home_score": pd.NA,
                "spread_line": pd.NA,
                "total_line": pd.NA,
                "away_moneyline": pd.NA,
                "home_moneyline": pd.NA,
                "roof": "",
                "surface": "",
                "temp": pd.NA,
                "wind": pd.NA,
                "stadium": "",
                "div_game": pd.NA,
                "away_rest": pd.NA,
                "home_rest": pd.NA,
            })
            for col in odds_cols:
                extras[col] = unmatched[col].values
            games = pd.concat([games, extras], ignore_index=True, sort=False)
            print(f"   ℹ️  preserved {len(unmatched)} unmatched odds row(s) as synthetic PRE games")

    return stamp_preseason_weeks(games)


def build_game_markets_tab(games: pd.DataFrame) -> pd.DataFrame:
    """Flatten game-level markets into one row per bettable side.

    This gives the dashboard a team-market surface that still works in
    preseason, when the provider may post spreads/totals before player props.
    """
    if games.empty:
        return pd.DataFrame()

    rows = []
    for _, game in games.iterrows():
        home = str(game.get("home_team", "")).strip().upper()
        away = str(game.get("away_team", "")).strip().upper()
        week = game.get("week", "")
        season = game.get("season", "")
        kickoff_date = game.get("gameday", "")
        kickoff_time = game.get("gametime", "")
        kickoff = f"{kickoff_date} {kickoff_time}".strip()
        matchup = f"{away} @ {home}".strip(" @")
        book = game.get("bookmaker", "") or "baseline"

        live_home_spread = game.get("live_home_spread")
        live_away_spread = game.get("live_away_spread")
        # nflverse `spread_line` is positive when the HOME team is favored,
        # which is the inverse of sportsbook display convention. Normalize it
        # here so every emitted team-market row reads like an actual bet slip.
        baseline_home_spread = (-game.get("spread_line")
                                if pd.notna(game.get("spread_line")) else None)
        baseline_away_spread = (-baseline_home_spread
                                if pd.notna(baseline_home_spread) else None)
        home_spread = (live_home_spread if pd.notna(live_home_spread)
                       else baseline_home_spread)
        away_spread = (live_away_spread if pd.notna(live_away_spread)
                       else baseline_away_spread)
        home_spread_odds = game.get("live_home_spread_odds", "")
        away_spread_odds = game.get("live_away_spread_odds", "")

        total_line = game.get("live_total")
        if pd.isna(total_line):
            total_line = game.get("total_line")
        over_odds = game.get("live_over_odds", "")
        under_odds = game.get("live_under_odds", "")

        home_ml = game.get("live_home_ml")
        away_ml = game.get("live_away_ml")
        if pd.isna(home_ml):
            home_ml = game.get("home_moneyline")
        if pd.isna(away_ml):
            away_ml = game.get("away_moneyline")

        if pd.notna(home_spread):
            rows.append({
                "SEASON": season,
                "WEEK": week,
                "GAME": matchup,
                "GAME_TYPE": game.get("game_type", ""),
                "KICKOFF": kickoff,
                "BOOK": book,
                "MARKET_TYPE": "SPREAD",
                "TEAM": home,
                "OPPONENT": away,
                "SELECTION": f"{home} {home_spread:+g}",
                "LINE": float(home_spread),
                "ODDS": home_spread_odds,
                "HOME_TEAM": home,
                "AWAY_TEAM": away,
            })
        if pd.notna(away_spread):
            rows.append({
                "SEASON": season,
                "WEEK": week,
                "GAME": matchup,
                "GAME_TYPE": game.get("game_type", ""),
                "KICKOFF": kickoff,
                "BOOK": book,
                "MARKET_TYPE": "SPREAD",
                "TEAM": away,
                "OPPONENT": home,
                "SELECTION": f"{away} {away_spread:+g}",
                "LINE": float(away_spread),
                "ODDS": away_spread_odds,
                "HOME_TEAM": home,
                "AWAY_TEAM": away,
            })

        if pd.notna(home_ml):
            rows.append({
                "SEASON": season,
                "WEEK": week,
                "GAME": matchup,
                "GAME_TYPE": game.get("game_type", ""),
                "KICKOFF": kickoff,
                "BOOK": book,
                "MARKET_TYPE": "MONEYLINE",
                "TEAM": home,
                "OPPONENT": away,
                "SELECTION": f"{home} to win",
                "LINE": "",
                "ODDS": home_ml,
                "HOME_TEAM": home,
                "AWAY_TEAM": away,
            })
        if pd.notna(away_ml):
            rows.append({
                "SEASON": season,
                "WEEK": week,
                "GAME": matchup,
                "GAME_TYPE": game.get("game_type", ""),
                "KICKOFF": kickoff,
                "BOOK": book,
                "MARKET_TYPE": "MONEYLINE",
                "TEAM": away,
                "OPPONENT": home,
                "SELECTION": f"{away} to win",
                "LINE": "",
                "ODDS": away_ml,
                "HOME_TEAM": home,
                "AWAY_TEAM": away,
            })

        if pd.notna(total_line):
            total_value = float(total_line)
            rows.extend([
                {
                    "SEASON": season,
                    "WEEK": week,
                    "GAME": matchup,
                    "GAME_TYPE": game.get("game_type", ""),
                    "KICKOFF": kickoff,
                    "BOOK": book,
                    "MARKET_TYPE": "TOTAL",
                    "TEAM": "",
                    "OPPONENT": "",
                    "SELECTION": f"Over {total_value:g}",
                    "LINE": total_value,
                    "ODDS": over_odds,
                    "HOME_TEAM": home,
                    "AWAY_TEAM": away,
                },
                {
                    "SEASON": season,
                    "WEEK": week,
                    "GAME": matchup,
                    "GAME_TYPE": game.get("game_type", ""),
                    "KICKOFF": kickoff,
                    "BOOK": book,
                    "MARKET_TYPE": "TOTAL",
                    "TEAM": "",
                    "OPPONENT": "",
                    "SELECTION": f"Under {total_value:g}",
                    "LINE": total_value,
                    "ODDS": under_odds,
                    "HOME_TEAM": home,
                    "AWAY_TEAM": away,
                },
            ])

    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


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
            prior = safe_records_df(ws)

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
    return safe_records_df(ws)


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
    odds_sport = resolve_odds_sport(schedule, started)
    model_version, model_era = resolve_model_identity(schedule_season, odds_sport)
    print(f"🧬 model version: {model_version} · era: {model_era}")
    log_launch_readiness(odds_sport, model_version, model_era)

    if not odds_api_key:
        print("   ⚠️  no Odds API key — skipping live odds and props")
    else:
        odds_api = oc.OddsClient(
            odds_api_key,
            quota_floor=QUOTA_FLOOR_THIS_SPORT,
            sport=odds_sport,
        )
        try:
            print(f"   sport key: {odds_sport}")
            if odds_sport == PRESEASON_ODDS_SPORT:
                print("   ℹ️  preseason mode: team markets should populate first; "
                      "player props may stay empty until books open them")
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
    game_markets_tab = build_game_markets_tab(games_tab)
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
            key_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "") or next(
                (path for path in DEFAULT_GOOGLE_CREDENTIAL_PATHS if os.path.exists(path)),
                "",
            )
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
    week = (current_preseason_week(games_tab, started)
            if odds_sport == PRESEASON_ODDS_SPORT
            else nv.current_week(schedule, now=started))
    preseason_team_markets_live = (
        odds_sport == PRESEASON_ODDS_SPORT
        and board.empty
        and has_live_game_market_odds(games_tab, game_type="PRE")
    )

    if SKIP_PICKS:
        print("   ⏭️  picks skipped (NFL_SKIP_PICKS set)")
    elif current_weekday.lower() not in PICKS_DAYS and not preseason_team_markets_live:
        print(f"   ⏭️  {current_weekday} is not a picks day "
              f"({', '.join(sorted(PICKS_DAYS))}) — leaving Picks_Current as-is")
    elif week is None:
        print("   ⚠️  could not determine current week — skipping picks")
    elif board.empty and not preseason_team_markets_live:
        # No real market lines yet means nothing to validate a pick against —
        # generating anyway would mean either inventing lines or running the
        # deterministic fallback on zero data. Neither is worth doing.
        print("   ⏭️  no player props posted yet — skipping picks generation")
    else:
        if preseason_team_markets_live:
            print("   ℹ️  preseason team-market mode: generating picks from spreads, moneylines, and totals")
            fresh_picks = pk.generate_preseason_game_picks(
                games_tab, week=week, season=schedule_season
            )
            print(f"   preseason picker: {len(fresh_picks)} candidate row(s)")
            log_pick_generation_outcome(
                preseason_team_markets_live=True,
                board=board,
                fresh_picks=fresh_picks,
            )
        else:
            gemini_key = load_secret("GEMINI_API_KEY", "🤖 Gemini API Key: ", allow_missing=True)
            all_logs = pd.concat([skill_logs, qb_logs], ignore_index=True) if not qb_logs.empty else skill_logs
            player_ctx = pk.build_player_context(board, all_logs, projections, injuries)
            print(f"   player context: {len(player_ctx)} priced prop rows")

            games_str = build_week_games_str(schedule, week)
            fresh_picks = pk.generate_weekly_picks(gemini_key, GEMINI_MODEL, player_ctx,
                                                   games_str, week=week, season=schedule_season)
            log_pick_generation_outcome(
                preseason_team_markets_live=False,
                board=board,
                player_ctx=player_ctx,
                gemini_key_present=bool(gemini_key),
                fresh_picks=fresh_picks,
            )
        prior_daily = fetch_prior_daily_picks(sheets, SHEET_ID)
        picks_current, daily_picks_new = pk.assemble_pick_tabs(
            fresh_picks, prior_daily, week=week, season=schedule_season,
            model_version=model_version, model_era=model_era)
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
        "Game_Markets": game_markets_tab,
        "Projections": projections,
        "Picks_Current": picks_current,
    }
    if KEEP_REFERENCE_TABS:
        tabs.update({
            # Reference-only tabs are useful for manual inspection, but the
            # live dashboard itself does not read them.
            "Injuries": build_injuries_tab(injuries),
            "Games": games_tab,
            "Teams": build_teams_tab(teams),
            "PlayerForm": build_player_form_tab(stats, snaps),
        })

    print("\n📝 Writing to Google Sheets")
    if not KEEP_REFERENCE_TABS:
        print("   ℹ️  dashboard-only sheet mode: skipping reference tabs (Injuries, Games, Teams, PlayerForm)")
    write_to_sheets(
        sheets,
        SHEET_ID,
        tabs,
        generated_at=generated_at,
        model_version=model_version,
        model_era=model_era,
    )
    append_daily_picks(sheets, SHEET_ID, daily_picks_new,
                       generated_at=generated_at,
                       model_version=model_version, model_era=model_era)
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
