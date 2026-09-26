"""DVOA-style NFL matchup ratings built from public nflverse play-by-play.

These are not FTN's proprietary DVOA values. They combine EPA per play and
success rate, split by run/pass and offense/defense, with prior-season
shrinkage. The pick model only receives a small capped probability adjustment;
the market remains the primary prior.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


PRIOR_TEAM_SHRINK_PLAYS = 100.0
PRIOR_SEASON_EQUIV_PLAYS = 80.0
MATCHUP_PROBABILITY_POINTS_PER_SD = 0.01
MAX_MATCHUP_PROBABILITY_ADJUSTMENT = 0.025

TEAM_ALIASES = {"LAR": "LA", "STL": "LA", "OAK": "LV", "SD": "LAC", "JAC": "JAX"}

RUSH_METRICS = {"RUSH_YDS", "RUSH_TDS", "CARRIES"}
PASS_METRICS = {"PASS_YDS", "PASS_TDS", "COMP", "ATT", "REC", "REC_YDS", "REC_TDS", "TGT"}


def _team(value) -> str:
    if value is None or pd.isna(value):
        return ""
    team = str(value or "").strip().upper()
    return TEAM_ALIASES.get(team, team)


def _numeric(frame: pd.DataFrame, column: str, default=0.0) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def prepare_efficiency_plays(pbp: pd.DataFrame) -> pd.DataFrame:
    """Reduce raw PBP to valid offensive run/pass plays with EPA and success."""
    if pbp is None or pbp.empty or not {"posteam", "defteam", "epa"}.issubset(pbp.columns):
        return pd.DataFrame(columns=["offense", "defense", "split", "epa", "success"])

    out = pbp.copy()
    if "season_type" in out.columns:
        out = out[out["season_type"].astype(str).str.upper().eq("REG")]
    if "no_play" in out.columns:
        out = out[_numeric(out, "no_play").fillna(0).eq(0)]
    for excluded in ("qb_kneel", "qb_spike", "two_point_attempt"):
        if excluded in out.columns:
            out = out[_numeric(out, excluded).fillna(0).eq(0)]

    rush = _numeric(out, "rush_attempt").fillna(0).eq(1)
    passed = _numeric(out, "pass_attempt").fillna(0).eq(1)
    if not rush.any() and not passed.any() and "play_type" in out.columns:
        play_type = out["play_type"].astype(str).str.lower()
        rush = play_type.eq("run")
        passed = play_type.eq("pass")
    out = out[rush | passed].copy()
    if out.empty:
        return pd.DataFrame(columns=["offense", "defense", "split", "epa", "success"])

    rush = _numeric(out, "rush_attempt").fillna(0).eq(1)
    out["split"] = np.where(rush, "rush", "pass")
    out["offense"] = out["posteam"].map(_team)
    out["defense"] = out["defteam"].map(_team)
    out["epa"] = _numeric(out, "epa", np.nan)
    if "success" in out.columns:
        out["success"] = _numeric(out, "success", np.nan).fillna((out["epa"] > 0).astype(float))
    else:
        out["success"] = (out["epa"] > 0).astype(float)
    return out.dropna(subset=["epa", "success"]).loc[
        lambda frame: frame["offense"].ne("") & frame["defense"].ne(""),
        ["offense", "defense", "split", "epa", "success"],
    ]


def _summaries(plays: pd.DataFrame, team_column: str) -> pd.DataFrame:
    if plays.empty:
        return pd.DataFrame(columns=["team", "split", "plays", "epa_sum", "success_sum"])
    grouped = plays.groupby([team_column, "split"], as_index=False).agg(
        plays=("epa", "size"), epa_sum=("epa", "sum"), success_sum=("success", "sum")
    )
    return grouped.rename(columns={team_column: "team"})


def _league_rates(plays: pd.DataFrame, split: str) -> tuple[float, float]:
    sample = plays[plays["split"].eq(split)] if not plays.empty else plays
    if sample.empty:
        return 0.0, 0.5
    return float(sample["epa"].mean()), float(sample["success"].mean())


def _posterior_rate(prior_row, current_row, prior_league: float, current_league: float,
                    value_column: str) -> tuple[float, float]:
    prior_n = float(prior_row.get("plays", 0.0)) if prior_row is not None else 0.0
    prior_sum = float(prior_row.get(value_column, 0.0)) if prior_row is not None else 0.0
    prior_estimate = (
        (prior_sum + prior_league * PRIOR_TEAM_SHRINK_PLAYS)
        / (prior_n + PRIOR_TEAM_SHRINK_PLAYS)
        if prior_n > 0 else prior_league
    )
    current_n = float(current_row.get("plays", 0.0)) if current_row is not None else 0.0
    current_sum = float(current_row.get(value_column, 0.0)) if current_row is not None else 0.0
    if current_n <= 0:
        return prior_estimate, 0.0
    anchor = prior_estimate if prior_n > 0 else current_league
    estimate = (
        current_sum + anchor * PRIOR_SEASON_EQUIV_PLAYS
    ) / (current_n + PRIOR_SEASON_EQUIV_PLAYS)
    return estimate, current_n


def _zscore(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    std = numeric.std(ddof=0)
    if pd.isna(std) or std <= 1e-9:
        return pd.Series(0.0, index=values.index)
    return (numeric - numeric.mean()) / std


def build_team_matchup_ratings(prior_pbp: pd.DataFrame,
                               current_pbp: pd.DataFrame) -> pd.DataFrame:
    """Build shrunk run/pass offense and defense ratings for all NFL teams."""
    prior = prepare_efficiency_plays(prior_pbp)
    current = prepare_efficiency_plays(current_pbp)
    if prior.empty and current.empty:
        return pd.DataFrame()

    prior_off, current_off = _summaries(prior, "offense"), _summaries(current, "offense")
    prior_def, current_def = _summaries(prior, "defense"), _summaries(current, "defense")
    teams = sorted(set(prior["offense"]) | set(prior["defense"]) |
                   set(current["offense"]) | set(current["defense"]))
    rows = []
    for team in teams:
        row = {"team_abbr": team}
        for split in ("rush", "pass"):
            prior_league_epa, prior_league_success = _league_rates(prior, split)
            current_league_epa, current_league_success = _league_rates(current, split)
            for side, prior_summary, current_summary in (
                ("off", prior_off, current_off), ("def", prior_def, current_def)
            ):
                prior_match = prior_summary[
                    prior_summary["team"].eq(team) & prior_summary["split"].eq(split)
                ]
                current_match = current_summary[
                    current_summary["team"].eq(team) & current_summary["split"].eq(split)
                ]
                prior_record = prior_match.iloc[0] if not prior_match.empty else None
                current_record = current_match.iloc[0] if not current_match.empty else None
                epa, current_plays = _posterior_rate(
                    prior_record, current_record, prior_league_epa, current_league_epa, "epa_sum"
                )
                success, _ = _posterior_rate(
                    prior_record, current_record, prior_league_success, current_league_success,
                    "success_sum"
                )
                suffix = "_allowed" if side == "def" else ""
                row[f"{side}_{split}_epa{suffix}"] = epa
                row[f"{side}_{split}_success{suffix}"] = success
                row[f"{side}_{split}_current_plays"] = current_plays
        rows.append(row)

    ratings = pd.DataFrame(rows)
    for split in ("rush", "pass"):
        ratings[f"off_{split}_score"] = (
            _zscore(ratings[f"off_{split}_epa"]) +
            _zscore(ratings[f"off_{split}_success"])
        ) / 2.0
        # Higher defense-ease score means the defense is more favorable to face.
        ratings[f"def_{split}_ease_score"] = (
            _zscore(ratings[f"def_{split}_epa_allowed"]) +
            _zscore(ratings[f"def_{split}_success_allowed"])
        ) / 2.0
        ratings[f"off_{split}_rank"] = ratings[f"off_{split}_score"].rank(
            ascending=False, method="min"
        ).astype(int)
        ratings[f"def_{split}_rank"] = ratings[f"def_{split}_ease_score"].rank(
            ascending=True, method="min"
        ).astype(int)
    return ratings.sort_values("team_abbr").reset_index(drop=True)


def matchup_probability_adjustment(ratings: pd.DataFrame, offense: str,
                                   defense: str, metric: str) -> tuple[float, float]:
    """Return (matchup score, OVER probability adjustment) for one prop."""
    if ratings is None or ratings.empty:
        return 0.0, 0.0
    metric = str(metric or "").upper()
    split = "rush" if metric in RUSH_METRICS else "pass" if metric in PASS_METRICS or metric == "INT" else ""
    if not split:
        return 0.0, 0.0
    offense_row = ratings[ratings["team_abbr"].eq(_team(offense))]
    defense_row = ratings[ratings["team_abbr"].eq(_team(defense))]
    if offense_row.empty or defense_row.empty:
        return 0.0, 0.0
    score = (
        0.4 * float(offense_row.iloc[0][f"off_{split}_score"])
        + 0.6 * float(defense_row.iloc[0][f"def_{split}_ease_score"])
    )
    if metric == "INT":
        score *= -1.0
    adjustment = float(np.clip(
        score * MATCHUP_PROBABILITY_POINTS_PER_SD,
        -MAX_MATCHUP_PROBABILITY_ADJUSTMENT,
        MAX_MATCHUP_PROBABILITY_ADJUSTMENT,
    ))
    return round(score, 4), round(adjustment, 4)
