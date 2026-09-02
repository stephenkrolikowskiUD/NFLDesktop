from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

REGULAR_SEASON_ODDS_SPORT = "americanfootball_nfl"
PRESEASON_ODDS_SPORT = "americanfootball_nfl_preseason"
REGULAR_SEASON_PHASE = "regular-season"
PRESEASON_PHASE = "preseason"


@dataclass(frozen=True)
class NFLSeasonPhase:
    phase: str
    odds_sport: str
    active_week: int | None

    @property
    def is_preseason(self) -> bool:
        return self.phase == PRESEASON_PHASE

    @property
    def game_type(self) -> str:
        return "PRE" if self.is_preseason else "REG"


def _coerce_now(now=None) -> pd.Timestamp:
    now_ts = pd.Timestamp(now or datetime.now())
    if now_ts.tzinfo is not None:
        now_ts = now_ts.tz_localize(None)
    return now_ts


def schedule_kickoff_series(schedule: pd.DataFrame) -> pd.Series:
    if schedule.empty:
        return pd.Series(dtype="datetime64[ns]")
    dates = schedule.get("gameday", pd.Series("", index=schedule.index)).astype(str)
    times = schedule.get("gametime", pd.Series("00:00", index=schedule.index)).astype(str)
    return pd.to_datetime(dates + " " + times, errors="coerce")


def preseason_week_for_kickoff(kickoff: pd.Timestamp, regular_opener: pd.Timestamp | None) -> int:
    """Stable negative week numbers for synthetic preseason slates."""
    if pd.isna(kickoff):
        return -1
    if regular_opener is None or pd.isna(regular_opener):
        return -1
    days_before_opener = max(0, (regular_opener.normalize() - kickoff.normalize()).days)
    return -int(days_before_opener // 7 + 1)


def stamp_preseason_weeks(games: pd.DataFrame) -> pd.DataFrame:
    if games.empty or "game_type" not in games.columns or "week" not in games.columns:
        return games

    out = games.copy()
    out["_kickoff"] = schedule_kickoff_series(out)
    game_type = out["game_type"].astype(str).str.upper()
    week_num = pd.to_numeric(out["week"], errors="coerce")
    reg_kickoffs = out.loc[game_type.eq("REG") & out["_kickoff"].notna(), "_kickoff"]
    regular_opener = reg_kickoffs.min() if not reg_kickoffs.empty else None
    needs_week = game_type.eq("PRE") & week_num.isna() & out["_kickoff"].notna()
    if needs_week.any():
        out.loc[needs_week, "week"] = out.loc[needs_week, "_kickoff"].apply(
            lambda kickoff: preseason_week_for_kickoff(kickoff, regular_opener)
        ).astype(int)
    return out.drop(columns="_kickoff", errors="ignore")


def current_preseason_week(games: pd.DataFrame, now=None) -> int | None:
    if games.empty or "game_type" not in games.columns or "week" not in games.columns:
        return None

    pre = games[games["game_type"].astype(str).str.upper().eq("PRE")].copy()
    if pre.empty:
        return None
    pre["_kickoff"] = schedule_kickoff_series(pre)
    pre["week_num"] = pd.to_numeric(pre["week"], errors="coerce")
    pre = pre[pre["_kickoff"].notna() & pre["week_num"].notna()].sort_values("_kickoff")
    if pre.empty:
        return None

    now_ts = _coerce_now(now)
    upcoming = pre[pre["_kickoff"] >= now_ts]
    sample = upcoming if not upcoming.empty else pre
    return int(sample.iloc[0]["week_num"])


def current_regular_week(schedule: pd.DataFrame, now=None) -> int | None:
    if schedule.empty or "week" not in schedule.columns:
        return None

    now_ts = _coerce_now(now)
    sched = schedule.copy()
    sched["_kickoff"] = schedule_kickoff_series(sched)
    upcoming = sched[sched["_kickoff"] >= now_ts]
    if not upcoming.empty:
        return int(upcoming.sort_values("_kickoff")["week"].iloc[0])

    past = sched[sched["_kickoff"].notna()]
    if not past.empty:
        return int(past.sort_values("_kickoff")["week"].iloc[-1])
    return None


def resolve_season_phase(schedule: pd.DataFrame, now=None, *, odds_sport_override: str = "") -> NFLSeasonPhase:
    stamped_schedule = stamp_preseason_weeks(schedule)
    override = str(odds_sport_override or "").strip()
    if override:
        phase = PRESEASON_PHASE if override == PRESEASON_ODDS_SPORT else REGULAR_SEASON_PHASE
        week = current_preseason_week(stamped_schedule, now=now) if phase == PRESEASON_PHASE else current_regular_week(schedule, now=now)
        return NFLSeasonPhase(phase=phase, odds_sport=override, active_week=week)

    if schedule.empty or "game_type" not in schedule.columns:
        return NFLSeasonPhase(
            phase=REGULAR_SEASON_PHASE,
            odds_sport=REGULAR_SEASON_ODDS_SPORT,
            active_week=current_regular_week(schedule, now=now),
        )

    now_ts = _coerce_now(now)
    sched = schedule.copy()
    sched["_kickoff"] = schedule_kickoff_series(sched)
    kickoff_rows = sched[sched["_kickoff"].notna()].sort_values("_kickoff")
    upcoming = sched[sched["_kickoff"] >= now_ts].sort_values("_kickoff")
    sample = upcoming if not upcoming.empty else sched.sort_values("_kickoff")
    if sample.empty:
        return NFLSeasonPhase(
            phase=REGULAR_SEASON_PHASE,
            odds_sport=REGULAR_SEASON_ODDS_SPORT,
            active_week=current_regular_week(schedule, now=now),
        )

    next_type = str(sample.iloc[0].get("game_type", "")).strip().upper()
    has_preseason_rows = sched["game_type"].astype(str).str.upper().eq("PRE").any()
    earliest_kickoff = kickoff_rows["_kickoff"].iloc[0] if not kickoff_rows.empty else None

    force_preseason = (
        not has_preseason_rows
        and next_type == "REG"
        and earliest_kickoff is not None
        and now_ts.month == 8
        and now_ts < earliest_kickoff
        and (earliest_kickoff - now_ts).days <= 35
    )
    is_preseason = force_preseason or next_type == "PRE"
    phase = PRESEASON_PHASE if is_preseason else REGULAR_SEASON_PHASE
    odds_sport = PRESEASON_ODDS_SPORT if is_preseason else REGULAR_SEASON_ODDS_SPORT
    week = current_preseason_week(stamped_schedule, now=now) if is_preseason else current_regular_week(schedule, now=now)
    return NFLSeasonPhase(phase=phase, odds_sport=odds_sport, active_week=week)


def infer_pick_phase(row: pd.Series) -> str | None:
    explicit = str(row.get("SEASON_PHASE") or "").strip().lower()
    if explicit in {PRESEASON_PHASE, REGULAR_SEASON_PHASE}:
        return explicit

    odds_sport = str(row.get("ODDS_SPORT") or "").strip()
    if odds_sport == PRESEASON_ODDS_SPORT:
        return PRESEASON_PHASE
    if odds_sport == REGULAR_SEASON_ODDS_SPORT:
        return REGULAR_SEASON_PHASE

    game_type = str(row.get("GAME_TYPE") or "").strip().upper()
    if game_type == "PRE":
        return PRESEASON_PHASE
    if game_type == "REG":
        return REGULAR_SEASON_PHASE

    week = pd.to_numeric(pd.Series([row.get("WEEK")]), errors="coerce").iloc[0]
    if pd.notna(week) and float(week) < 0:
        return PRESEASON_PHASE

    for field in ("MODEL_ERA", "MODEL_VERSION", "CONSENSUS_TAG"):
        text = str(row.get(field) or "").strip().lower()
        if "preseason" in text:
            return PRESEASON_PHASE
        if "regular-season" in text or "regular_season" in text:
            return REGULAR_SEASON_PHASE

    return None
