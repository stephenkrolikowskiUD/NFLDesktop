# 🏈 NFL Grader (v1) — grades Daily_Picks, builds Pick_Performance
#
# Ported from MLBGrader5-4.py. Two mechanics are near-verbatim on purpose,
# because they're the parts that keep a betting-record table honest:
#   - grade_pick(): exact-match -> PUSH, else which side of the line the
#     actual value landed on. Reused UNCHANGED for binary props (anytime-TD):
#     odds_client.BINARY_MARKETS already gives them an implicit 0.5 line, so
#     actual=1/0 (scored or didn't) against line=0.5 needs no separate path.
#   - Pick_Performance's schema, dimensions, time windows, and Wilson-lower-
#     bound math are copied exactly, because app.js's confidence-tier
#     calibration UI (SMASH/STRONG floors) already expects this exact shape.
#
# What's genuinely different from MLB, not just renamed:
#   - Readiness is per-GAME, not per-DATE. MLB skips grading anything dated
#     today because "today's game hasn't finished" is a safe blanket rule when
#     every pick is a same-day game. NFL breaks that: a Thursday pick and a
#     Monday pick can share the same WEEK number while being days apart in
#     actual kickoff time. So readiness here is "has THIS pick's specific game
#     kicked off, plus a completion buffer" — resolved by joining the pick's
#     team+week back to Schedule for a real kickoff timestamp, not by looking
#     at DATE at all.
#   - Identity matching is player_id-first. MLB only ever had a name to match
#     on, so it has to detect+skip name/date collisions after the fact. Picks
#     here already carry player_id from generation, so that's the primary key;
#     name matching is only a fallback for legacy rows that predate this, with
#     the same ambiguity-detection MLB uses so an uncertain match is left
#     ungraded rather than silently wrong.

import math
import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz
import gspread
import json

from picks import actual_value_for_metric, BINARY_METRICS, TEAM_MARKET_METRICS  # single source of truth
from sports_common import (
    col_letter,
    get_gspread_client,
    load_sheet_grid,
    normalize_confidence,
    normalize_person_name,
)

SHEET_ID = "1vJvcOsMyBEz1ZMJy6BKapdfG3FlvPIpB0eD_dviQBd0"
eastern = pytz.timezone("US/Eastern")

# Buffer after scheduled kickoff before attempting to grade — covers game
# length (~3.5h) plus nflverse's own publish lag (observed up to a few hours
# after a slate, worse for late Sunday/Monday games). A pick found not-ready
# just stays ungraded for the next grader run, same as MLB's DNP retry.
GRADE_BUFFER_HOURS = 6
DNP_RETRY_WEEKS = 3

# --- Pick_Performance config, copied exactly from MLB ----------------------
PICK_PERF_MIN_SAMPLE = 25
PICK_PERF_STANDARD_ODDS = -115
PICK_PERF_WILSON_Z = 1.96
PICK_PERF_TIME_WINDOWS = {"last_7d": 7, "last_30d": 30, "last_90d": 90, "all_time": None}
PICK_PERF_SNAPSHOT_WINDOWS = ("all_time", "last_30d")
PICK_PERF_DIMENSIONS = (
    "confidence_norm", "selection_method_norm", "prop_type_norm", "lean_norm",
    "consensus_bucket", "odds_bucket", "clv_bucket", "week", "day_of_week",
)
PICK_PERFORMANCE_COLUMNS = [
    "DIMENSION_TYPE", "DIMENSION_VALUE", "TIME_WINDOW",
    "N_PICKS", "N_PICKS_DECISIVE", "N_SETTLED", "N_HITS", "N_MISSES", "N_PUSHES", "N_DNP",
    "HIT_RATE", "HIT_RATE_RAW", "PUSH_RATE", "DNP_RATE",
    "ROI_FLAT", "ROI_PER_PICK",
    "N_PRICED", "ACTUAL_PROFIT_UNITS", "ACTUAL_ROI_PER_PICK",
    "WILSON_LOWER_95", "MIN_SAMPLE_FLAG",
    "LAST_UPDATED",
]
PICK_PERFORMANCE_SNAPSHOT_COLUMNS = ["SNAPSHOT_DATE", "METRIC_KEY", "METRIC_VALUE", "N_PICKS", "TIME_WINDOW"]


# ============================================================================
# SMALL HELPERS — ported near-verbatim from MLBGrader5-4.py
# ============================================================================

def safe_float(val, default=None):
    if val is None:
        return default
    if isinstance(val, str):
        val = val.strip().replace(",", "")
        if not val or val.upper() in {"N/A", "NA", "NONE", "NULL", "DNP"}:
            return default
    try:
        num = float(val)
        return default if (math.isnan(num) or math.isinf(num)) else num
    except (TypeError, ValueError):
        return default


def american_profit_units(odds) -> float | None:
    price = safe_float(odds)
    if price is None or price == 0:
        return None
    return price / 100.0 if price > 0 else 100.0 / abs(price)


def realized_profit_units(hit, odds) -> float | None:
    result = str(hit or "").strip().upper()
    if result == "NO":
        return -1.0
    if result in {"PUSH", "DNP"}:
        return 0.0
    if result == "YES":
        return american_profit_units(odds)
    return None


def grade_pick(actual, line_val, lean) -> tuple[str, str]:
    """Returns (HIT_value, RESULT_value): HIT is YES/NO/PUSH, RESULT is
    HIT/MISS/PUSH — same tuple order and same column meanings as MLB, verified
    against MLBGrader5-4.py's own call site (hit_str, result_str = grade_pick(...)).
    Binary props (anytime-TD) need no special case: actual is already 1.0/0.0
    and line_val is 0.5, so this is the exact same comparison as any numeric prop.
    """
    if actual is None or line_val is None:
        return "", ""
    if actual == line_val:
        return "PUSH", "PUSH"
    if lean in ("UNDER", "FADE"):
        return ("YES", "HIT") if actual < line_val else ("NO", "MISS")
    return ("YES", "HIT") if actual > line_val else ("NO", "MISS")


def pick_odds_bucket(value) -> str:
    if pd.isna(value):
        return "unknown"
    odds = float(value)
    if odds >= 100:
        return "plus_money"
    if odds >= -125:
        return "-101_to_-125"
    if odds >= -150:
        return "-126_to_-150"
    if odds >= -200:
        return "-151_to_-200"
    return "below_-200"


def wilson_lower_bound(p, n, z=PICK_PERF_WILSON_Z) -> float:
    if n <= 0:
        return 0.0
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return max(0.0, (centre - margin) / denom)


# ============================================================================
# READINESS — per-game kickoff time, not per-DATE (see module docstring).
# ============================================================================

def build_kickoff_lookup(schedule: pd.DataFrame) -> dict:
    """(team, season, week) -> kickoff datetime, for both home and away teams."""
    lookup = {}
    if schedule.empty:
        return lookup
    for _, g in schedule.iterrows():
        try:
            kickoff = pd.to_datetime(f"{g.get('gameday','')} {g.get('gametime','00:00')}", errors="coerce")
        except Exception:
            kickoff = pd.NaT
        if pd.isna(kickoff):
            continue
        if getattr(kickoff, "tzinfo", None) is None:
            kickoff = eastern.localize(kickoff.to_pydatetime())
        key_season = g.get("season")
        key_week = g.get("week")
        for team in (g.get("home_team"), g.get("away_team")):
            if team:
                lookup[(team, key_season, key_week)] = kickoff
    return lookup


def pick_is_ready(pick: pd.Series, kickoff_lookup: dict, now) -> bool:
    """Has this specific pick's game kicked off, plus a completion buffer?
    Unknown kickoff (team/week not in schedule) errs toward NOT ready — a
    pick that's actually ready will simply retry successfully next run; one
    graded against a game that hasn't happened is unrecoverable.
    """
    key = (pick.get("team"), safe_float(pick.get("SEASON")), safe_float(pick.get("WEEK")))
    kickoff = kickoff_lookup.get(key)
    if kickoff is None or pd.isna(kickoff):
        return False
    return now >= (kickoff + timedelta(hours=GRADE_BUFFER_HOURS))


# ============================================================================
# BOX SCORE LOOKUP — player_id first, name+week fallback with ambiguity guard.
# ============================================================================

def build_box_lookup(game_logs: pd.DataFrame):
    """Returns (by_id, by_name, name_ambiguous, team_week_has_data).

    by_id is keyed on (player_id, season, week) — the primary, unambiguous
    path since picks already carry player_id. by_name exists only for rows
    that somehow lack one; name_ambiguous flags (name, season, week) keys that
    map to more than one player_id, mirroring MLB's refusal to guess between
    two same-named players rather than silently picking one.
    """
    by_id, by_name = {}, {}
    name_identity = {}
    name_ambiguous = set()
    team_week_has_data = set()

    for _, row in game_logs.iterrows():
        season, week = row.get("season"), row.get("week")
        pid = row.get("player_id")
        team = row.get("team")
        if pd.notna(team):
            team_week_has_data.add((team, season, week))
        if pd.notna(pid):
            by_id[(str(pid), season, week)] = row

        name_key = (normalize_person_name(row.get("player_display_name"), keep_digits=True, strip_chars="'`\\."), season, week)
        name_identity.setdefault(name_key, set()).add(str(pid))
        if name_key not in by_name:
            by_name[name_key] = row

    for key, ids in name_identity.items():
        if len(ids) > 1:
            name_ambiguous.add(key)

    return by_id, by_name, name_ambiguous, team_week_has_data


def find_actual(pick: pd.Series, by_id: dict, by_name: dict, name_ambiguous: set):
    """Returns (log_row_or_None, status) where status is 'ok', 'ambiguous', or
    'not_found'."""
    season, week = safe_float(pick.get("SEASON")), safe_float(pick.get("WEEK"))
    pid = str(pick.get("player_id") or "").strip()
    if pid and (pid, season, week) in by_id:
        return by_id[(pid, season, week)], "ok"

    name_key = (normalize_person_name(pick.get("player"), keep_digits=True, strip_chars="'`\\."), season, week)
    if name_key in name_ambiguous:
        return None, "ambiguous"
    if name_key in by_name:
        return by_name[name_key], "ok"
    return None, "not_found"


def build_schedule_result_lookup(schedule: pd.DataFrame) -> dict:
    """(season, week, team, opponent) -> schedule row for both team views."""
    lookup = {}
    if schedule.empty:
        return lookup
    for _, row in schedule.iterrows():
        season = row.get("season")
        week = row.get("week")
        home = str(row.get("home_team") or "").strip().upper()
        away = str(row.get("away_team") or "").strip().upper()
        if home and away:
            lookup[(season, week, home, away)] = row
            lookup[(season, week, away, home)] = row
    return lookup


def actual_value_for_team_market(pick: pd.Series, game_row: pd.Series):
    metric = str(pick.get("prop_type", "")).upper()
    team = str(pick.get("team") or "").strip().upper()
    home = str(game_row.get("home_team") or "").strip().upper()
    away = str(game_row.get("away_team") or "").strip().upper()
    home_score = safe_float(game_row.get("home_score"))
    away_score = safe_float(game_row.get("away_score"))
    if home_score is None or away_score is None:
        return None

    if metric == "MONEYLINE":
        team_score = home_score if team == home else away_score if team == away else None
        opp_score = away_score if team == home else home_score if team == away else None
        if team_score is None or opp_score is None:
            return None
        return 1.0 if team_score > opp_score else 0.0

    if metric == "SPREAD":
        if team == home:
            return float(home_score - away_score)
        if team == away:
            return float(away_score - home_score)
        return None

    if metric == "TOTAL":
        return float(home_score + away_score)

    return None


# ============================================================================
# GRADING PASS
# ============================================================================

def grade_daily_picks(client) -> None:
    sheet = client.open_by_key(SHEET_ID)
    try:
        ws = sheet.worksheet("Daily_Picks")
    except gspread.exceptions.WorksheetNotFound:
        print("⏭️  Daily_Picks doesn't exist yet — nothing to grade")
        return

    header, data_rows = load_sheet_grid(ws)
    if not data_rows:
        print("⏭️  Daily_Picks is empty — nothing to grade")
        return
    df = pd.DataFrame(data_rows, columns=header)
    print(f"📋 Daily_Picks: {len(df)} total rows")

    required = {"HIT", "player", "player_id", "team", "SEASON", "WEEK", "prop_type", "line", "lean"}
    missing = required - set(df.columns)
    if missing:
        print(f"❌ Daily_Picks is missing required column(s) {missing} — aborting rather than "
              f"grade against an assumption about what's there")
        return

    ungraded = df[df["HIT"].astype(str).str.strip() == ""]
    print(f"   {len(ungraded)} ungraded row(s)")
    if ungraded.empty:
        return

    print("\n📡 Loading schedule + game logs for grading...")
    import nflverse_loader as nv
    import NFLEnginev1 as eng

    seasons_needed = sorted({int(s) for s in pd.to_numeric(ungraded["SEASON"], errors="coerce").dropna().unique()})
    schedule = pd.concat([nv.load_schedules(seasons=[s]) for s in seasons_needed], ignore_index=True) if seasons_needed else pd.DataFrame()
    kickoff_lookup = build_kickoff_lookup(schedule)
    schedule_results = build_schedule_result_lookup(schedule)

    stats = pd.concat([nv.load_player_stats(seasons=[s]) for s in seasons_needed], ignore_index=True) if seasons_needed else pd.DataFrame()
    game_logs = pd.concat([
        eng.build_game_logs_tab(stats, eng.SKILL_POSITIONS),
        eng.build_game_logs_tab(stats, ["QB"]),
    ], ignore_index=True) if not stats.empty else pd.DataFrame()
    by_id, by_name, name_ambiguous, team_week_has_data = build_box_lookup(game_logs)
    print(f"   game logs: {len(game_logs)} rows across {len(seasons_needed)} season(s)")

    now = datetime.now(eastern)
    col_idx = {name: i for i, name in enumerate(header)}
    updates = []
    graded = hits = misses = pushes = dnp = not_ready = ambiguous_skipped = 0

    for idx, pick in ungraded.iterrows():
        sheet_row = idx + 2  # +1 for 0-index, +1 for header row
        if not pick_is_ready(pick, kickoff_lookup, now):
            not_ready += 1
            continue

        metric = str(pick.get("prop_type", "")).upper()
        team_week_key = (pick.get("team"), safe_float(pick.get("SEASON")), safe_float(pick.get("WEEK")))
        actual = None
        line_val = safe_float(pick.get("line"))

        if metric in TEAM_MARKET_METRICS:
            season = safe_float(pick.get("SEASON"))
            week = safe_float(pick.get("WEEK"))
            team = str(pick.get("team") or "").strip().upper()
            opponent = str(pick.get("opponent") or "").strip().upper()
            game_row = schedule_results.get((season, week, team, opponent))
            if game_row is None:
                not_ready += 1
                continue
            actual = actual_value_for_team_market(pick, game_row)
            if actual is None or line_val is None:
                continue
            status = "ok"
        else:
            log_row, status = find_actual(pick, by_id, by_name, name_ambiguous)

            if status == "ambiguous":
                ambiguous_skipped += 1
                print(f"   ⚠️  {pick.get('player')} (wk {pick.get('WEEK')}) — name maps to >1 player_id; "
                      f"leaving ungraded rather than risk grading the wrong person")
                continue

            if log_row is None:
                if team_week_key not in team_week_has_data:
                    # This team's data for that week isn't published yet at all —
                    # a lag issue, not a DNP. Retry next run.
                    continue
                updates.append((sheet_row, "ACTUAL_STAT", "DNP"))
                updates.append((sheet_row, "HIT", "DNP"))
                updates.append((sheet_row, "RESULT", "DNP"))
                updates.append((sheet_row, "REALIZED_PROFIT", "0"))
                updates.append((sheet_row, "ACTUAL_ROI_PER_PICK", "0"))
                dnp += 1
                continue

            actual = actual_value_for_metric(log_row, metric)
            actual = safe_float(actual)
            if actual is None or line_val is None:
                continue

        hit_str, result_str = grade_pick(actual, line_val, str(pick.get("lean", "")).upper())
        if hit_str == "PUSH":
            pushes += 1
        elif hit_str == "YES":
            hits += 1
        elif hit_str == "NO":
            misses += 1
        graded += 1

        profit = realized_profit_units(hit_str, pick.get("PICK_ODDS"))
        updates.append((sheet_row, "ACTUAL_STAT", str(actual)))
        updates.append((sheet_row, "HIT", hit_str))
        updates.append((sheet_row, "RESULT", result_str))
        if profit is not None:
            updates.append((sheet_row, "REALIZED_PROFIT", str(round(profit, 4))))
            updates.append((sheet_row, "ACTUAL_ROI_PER_PICK", str(round(profit, 4))))
        icon = "✅" if hit_str == "YES" else "❌" if hit_str == "NO" else "➖"
        print(f"   {icon} {pick.get('player')} | {pick.get('prop_type')} {pick.get('lean')} "
              f"{pick.get('line')} → {actual} → {hit_str}")

    if updates:
        cells = [{"range": f"{col_letter(col_idx[col])}{row}", "values": [[val]]}
                 for row, col, val in updates if col in col_idx]
        print(f"\n📤 Writing {len(cells)} cell updates to Daily_Picks...")
        ws.batch_update(cells)

    print(f"\n✅ Graded {graded} ({hits}-{misses}-{pushes} hit-miss-push), "
          f"{dnp} DNP, {not_ready} not ready yet, {ambiguous_skipped} skipped (ambiguous)")


# ============================================================================
# PICK_PERFORMANCE — schema/dimensions/windows copied from MLB verbatim.
# ============================================================================

def pick_perf_prepare_df(df_all: pd.DataFrame) -> pd.DataFrame:
    if df_all is None or df_all.empty or "HIT" not in df_all.columns:
        return pd.DataFrame()
    df = df_all[df_all["HIT"].isin(["YES", "NO", "PUSH", "DNP"])].copy()
    if df.empty:
        return df
    idx = df.index
    df["prop_type_norm"] = df.get("prop_type", pd.Series("", index=idx)).fillna("").astype(str).str.upper()
    df["lean_norm"] = df.get("lean", pd.Series("", index=idx)).fillna("").astype(str).str.upper()
    df["selection_method_norm"] = df.get("SELECTION_METHOD", pd.Series("", index=idx)).fillna("").astype(str).str.upper().replace({"": "GEMINI"})
    df["confidence_norm"] = df.get("confidence", pd.Series("", index=idx)).map(
        lambda v: normalize_confidence(v, allowed=("SMASH", "STRONG", "LEAN", "VALIDATED"))
    )
    df.loc[df["selection_method_norm"].eq("VALIDATED_MODEL"), "confidence_norm"] = "VALIDATED"
    df["pick_odds_f"] = pd.to_numeric(df.get("PICK_ODDS", pd.Series(np.nan, index=idx)), errors="coerce")
    df["odds_bucket"] = df["pick_odds_f"].map(pick_odds_bucket)
    df["realized_profit_f"] = pd.to_numeric(df.get("REALIZED_PROFIT", pd.Series(np.nan, index=idx)), errors="coerce")
    df["consensus_bucket"] = pd.to_numeric(df.get("CONSENSUS_COUNT", pd.Series(1, index=idx)), errors="coerce").fillna(1).astype(int)
    df["clv_open_f"] = pd.to_numeric(df.get("CLV_OPEN_LINE", pd.Series(np.nan, index=idx)), errors="coerce")
    df["clv_latest_f"] = pd.to_numeric(df.get("CLV_LATEST_LINE", pd.Series(np.nan, index=idx)), errors="coerce")
    df["clv_edge"] = np.where(
        df["lean_norm"].isin(["UNDER", "FADE"]),
        df["clv_open_f"] - df["clv_latest_f"],
        df["clv_latest_f"] - df["clv_open_f"],
    )
    df["clv_bucket"] = np.where(
        df["clv_open_f"].isna() | df["clv_latest_f"].isna(),
        "flat",
        np.where(df["clv_edge"] > 0, "positive", np.where(df["clv_edge"] < 0, "negative", "flat")),
    )
    df["week"] = df.get("WEEK", pd.Series("", index=idx)).astype(str)
    df["date_parsed"] = pd.to_datetime(df.get("DATE", pd.Series("", index=idx)), errors="coerce")
    df["day_of_week"] = df["date_parsed"].dt.strftime("%a").fillna("unknown")
    return df


def pick_perf_rate(hits: int, misses: int) -> float:
    n = hits + misses
    return np.nan if n <= 0 else hits / n


def pick_perf_metrics_row(df_slice: pd.DataFrame, dim_type: str, dim_value, window_name: str, timestamp_est: str) -> dict:
    n_picks = len(df_slice)
    n_hits = int((df_slice["HIT"] == "YES").sum())
    n_misses = int((df_slice["HIT"] == "NO").sum())
    n_pushes = int((df_slice["HIT"] == "PUSH").sum())
    n_dnp = int((df_slice["HIT"] == "DNP").sum())
    n_decisive = n_hits + n_misses
    n_settled = n_decisive + n_pushes
    hit_rate = pick_perf_rate(n_hits, n_misses)
    roi_flat = (n_hits * (100 / abs(PICK_PERF_STANDARD_ODDS)) - n_misses) * 100
    roi_per_pick = roi_flat / n_settled if n_settled > 0 else np.nan

    priced = df_slice[df_slice["HIT"].isin(["YES", "NO", "PUSH"]) & df_slice["pick_odds_f"].notna()].copy()
    if not priced.empty:
        missing = priced["realized_profit_f"].isna()
        priced.loc[missing, "realized_profit_f"] = priced.loc[missing].apply(
            lambda row: realized_profit_units(row["HIT"], row["pick_odds_f"]), axis=1)
    n_priced = len(priced)
    actual_profit = priced["realized_profit_f"].sum() if n_priced else np.nan
    actual_roi_per_pick = actual_profit / n_priced if n_priced else np.nan

    wilson_n = n_hits + n_misses
    wilson_p = n_hits / wilson_n if wilson_n > 0 else 0
    return {
        "DIMENSION_TYPE": dim_type, "DIMENSION_VALUE": "" if dim_value is None else str(dim_value),
        "TIME_WINDOW": window_name,
        "N_PICKS": n_picks, "N_PICKS_DECISIVE": n_decisive, "N_SETTLED": n_settled,
        "N_HITS": n_hits, "N_MISSES": n_misses, "N_PUSHES": n_pushes, "N_DNP": n_dnp,
        "HIT_RATE": round(hit_rate, 3) if pd.notna(hit_rate) else np.nan,
        "HIT_RATE_RAW": round(n_hits / n_decisive, 3) if n_decisive else np.nan,
        "PUSH_RATE": round(n_pushes / n_picks, 3) if n_picks else 0,
        "DNP_RATE": round(n_dnp / n_picks, 3) if n_picks else 0,
        "ROI_FLAT": round(roi_flat, 3),
        "ROI_PER_PICK": round(roi_per_pick, 3) if pd.notna(roi_per_pick) else np.nan,
        "N_PRICED": n_priced,
        "ACTUAL_PROFIT_UNITS": round(actual_profit, 3) if pd.notna(actual_profit) else np.nan,
        "ACTUAL_ROI_PER_PICK": round(actual_roi_per_pick, 4) if pd.notna(actual_roi_per_pick) else np.nan,
        "WILSON_LOWER_95": round(wilson_lower_bound(wilson_p, wilson_n), 3),
        "MIN_SAMPLE_FLAG": bool(n_decisive >= PICK_PERF_MIN_SAMPLE),
        "LAST_UPDATED": timestamp_est,
    }


def build_pick_performance(df_all: pd.DataFrame) -> pd.DataFrame:
    df = pick_perf_prepare_df(df_all)
    if df.empty:
        return pd.DataFrame(columns=PICK_PERFORMANCE_COLUMNS)
    today = datetime.now(eastern).date()
    timestamp_est = datetime.now(eastern).strftime("%Y-%m-%d %H:%M:%S %Z")
    rows = []
    for window_name, days in PICK_PERF_TIME_WINDOWS.items():
        win_df = df if days is None else df[
            df["date_parsed"].notna() & (df["date_parsed"] >= pd.Timestamp(today - timedelta(days=days)))
        ]
        if win_df.empty:
            continue
        rows.append(pick_perf_metrics_row(win_df, "overall", "", window_name, timestamp_est))
        for dim in PICK_PERF_DIMENSIONS:
            if dim not in win_df.columns:
                continue
            for dim_value, grp in win_df.groupby(dim, dropna=False):
                rows.append(pick_perf_metrics_row(grp, dim, dim_value, window_name, timestamp_est))
    metrics_df = pd.DataFrame(rows, columns=PICK_PERFORMANCE_COLUMNS)
    if metrics_df.empty:
        return metrics_df
    order = {name: i for i, name in enumerate(PICK_PERF_TIME_WINDOWS)}
    metrics_df["_o"] = metrics_df["TIME_WINDOW"].map(order).fillna(99)
    metrics_df = (metrics_df.sort_values(["_o", "DIMENSION_TYPE", "WILSON_LOWER_95"],
                                        ascending=[True, True, False])
                            .drop(columns=["_o"]).reset_index(drop=True))
    return metrics_df


def build_snapshots(metrics_df: pd.DataFrame) -> pd.DataFrame:
    if metrics_df.empty:
        return pd.DataFrame(columns=PICK_PERFORMANCE_SNAPSHOT_COLUMNS)
    today = datetime.now(eastern).strftime("%Y-%m-%d")
    overall = metrics_df[(metrics_df["DIMENSION_TYPE"] == "overall")
                         & (metrics_df["TIME_WINDOW"].isin(PICK_PERF_SNAPSHOT_WINDOWS))]
    rows = []
    for _, r in overall.iterrows():
        for metric_key in ("HIT_RATE", "ROI_PER_PICK", "WILSON_LOWER_95"):
            rows.append({
                "SNAPSHOT_DATE": today, "METRIC_KEY": metric_key,
                "METRIC_VALUE": r.get(metric_key), "N_PICKS": r.get("N_PICKS"),
                "TIME_WINDOW": r.get("TIME_WINDOW"),
            })
    return pd.DataFrame(rows, columns=PICK_PERFORMANCE_SNAPSHOT_COLUMNS)


def write_full_tab(client, tab_name: str, df: pd.DataFrame) -> None:
    from gspread_dataframe import set_with_dataframe
    if df.empty:
        print(f"⏭️  {tab_name}: nothing to write")
        return
    sheet = client.open_by_key(SHEET_ID)
    try:
        ws = sheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=tab_name, rows=max(len(df) + 10, 100), cols=max(len(df.columns) + 5, 26))
    ws.clear()
    clean = df.copy()
    clean["_tab"] = tab_name
    clean = clean.where(pd.notna(clean), "")
    set_with_dataframe(ws, clean, include_index=False, resize=True)
    print(f"✅ {tab_name}: {len(clean)} rows")


def append_snapshots(client, new_rows: pd.DataFrame) -> None:
    """Append-only, deduped against today's date — mirrors MLB's guard against
    writing the same day's snapshot twice if the grader runs more than once."""
    if new_rows.empty:
        return
    sheet = client.open_by_key(SHEET_ID)
    try:
        ws = sheet.worksheet("Pick_Performance_Snapshots")
    except gspread.exceptions.WorksheetNotFound:
        from gspread_dataframe import set_with_dataframe
        ws = sheet.add_worksheet(title="Pick_Performance_Snapshots",
                                 rows=max(len(new_rows) + 500, 1000), cols=10)
        clean = new_rows.copy()
        clean["_tab"] = "Pick_Performance_Snapshots"
        set_with_dataframe(ws, clean, include_index=False, resize=True)
        print(f"➕ created Pick_Performance_Snapshots, {len(new_rows)} row(s)")
        return

    existing = pd.DataFrame(ws.get_all_records())
    today = new_rows["SNAPSHOT_DATE"].iloc[0]
    if not existing.empty and "SNAPSHOT_DATE" in existing.columns:
        if (existing["SNAPSHOT_DATE"].astype(str) == str(today)).any():
            print(f"⏭️  Pick_Performance_Snapshots already has a row for {today} — skipping duplicate write")
            return

    clean = new_rows.copy()
    clean["_tab"] = "Pick_Performance_Snapshots"
    rows = clean.astype(str).values.tolist()
    ws.append_rows(rows, value_input_option="RAW")
    print(f"✅ Pick_Performance_Snapshots: appended {len(rows)} row(s)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"🏈 NFL Grader v1 — {datetime.now(eastern):%Y-%m-%d %H:%M:%S %Z}")
    client = get_gspread_client()

    grade_daily_picks(client)

    print("\n📊 Building Pick_Performance...")
    sheet = client.open_by_key(SHEET_ID)
    try:
        ws = sheet.worksheet("Daily_Picks")
        all_picks = pd.DataFrame(ws.get_all_records())
    except gspread.exceptions.WorksheetNotFound:
        all_picks = pd.DataFrame()

    metrics = build_pick_performance(all_picks)
    write_full_tab(client, "Pick_Performance", metrics)
    snapshots = build_snapshots(metrics)
    append_snapshots(client, snapshots)

    print("\n✅ Grader complete")


if __name__ == "__main__":
    main()
