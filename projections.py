# 📈 Season-long projections (v1)
#
# WHAT THIS IS: per-game production rates from last season, shrunk toward the
# positional mean by sample size, scaled by projected availability, with
# FantasyPros best-ball consensus (ECR) carried alongside — never blended into
# one opaque number.
#
# WHAT THE BACKTEST SAYS (see backtest.py; 7 folds 2018->2025, top 200 on a
# model-independent eval set): this now beats a naive carry-forward on both MAE
# and rank correlation. The edge is real, but still modest enough that the
# board should be used as a cross-check on consensus, not a blind override.
#
# Biggest remaining weakness: players who changed teams still run a little hot,
# though the age + depth-chart adjustments cut that bias dramatically. The
# consensus-anchored prior below also CANNOT be validated directly — nflverse
# ships one ECR scrape date, so no historical consensus series exists.
#
# Deliberately still NOT modeled (each needs extra data or a football judgment
# layer we do not yet trust enough to hard-code):
#   - scheme/coaching changes
#   - injury-return curves
#   - explicit team pace / pass-rate context
#   - rookie production from college data (nflverse carries none)
# Rookies are therefore imputed from consensus only, and flagged as such.

import re

import numpy as np
import pandas as pd

POSITION_GROUPS = ["QB", "RB", "WR", "TE"]

# Prior weight, expressed in games. A player with SHRINK_GAMES games of history
# gets a 50/50 blend of their own rate and the positional mean.
SHRINK_GAMES = 4.0
# Changing teams makes last season's usage less predictive of next season's, so
# those players are pulled harder toward the positional mean. Backtest confirms
# they are otherwise over-projected by ~20 points.
# Left at 8 deliberately. Raising it does reduce the confirmed +19 pt
# over-projection of these players (to ~+12 at k=28), but costs both MAE
# (56.3 -> 57.3) and rank correlation (0.631 -> 0.626). That tradeoff says the
# positional mean is the wrong correction: players who change teams don't
# regress toward average, they land in genuinely different roles. Trading
# overall accuracy for a cosmetically better subgroup number isn't worth it, so
# this stays a documented known bias, flagged as "new tm" on the draft board for
# the user's own judgment, rather than papered over.
SHRINK_GAMES_TEAM_CHANGE = 8.0
# A short season is a DIFFERENT problem from a team change and needs the
# opposite treatment. The per-game rate of someone who played 8 games is still
# reliable — it's their availability that's in question, and project_games
# already handles that separately. Shrinking their rate as well double-counts
# it, which is why the backtest shows partial-season players UNDER-projected by
# ~17 points. Lumping both conditions under one prior weight made tuning one
# actively worsen the other.
SHRINK_GAMES_PARTIAL_SEASON = 4.0

# Availability is itself shrunk: a player who missed time once shouldn't be
# projected for 17 games, but neither should one bad year define them.
#
# The prior weight was raised from 6 to 10 on backtest evidence. Prior-year
# games played predicts next-year games played only weakly (rank correlation
# ~0.17), so regressing harder toward the league average is the correct
# treatment. This alone removed the partial-season under-projection the
# backtest found (-17 pts -> +1 pt) while slightly IMPROVING both MAE (56.5 ->
# 56.3) and rank correlation (0.625 -> 0.631) — no tradeoff, which is why it
# was preferred over distorting those players' per-game rates to compensate.
FULL_SEASON_GAMES = 17
# 15.0 was an assumption and it was too high: across the backtest population the
# actual mean is 13.6 games, so the model projected ~1.3 games too many for
# everyone. Swept against the backtest — 14.0 gives the smallest point bias
# (-1.3 vs +2.7) with the best MAE and rank correlation. Pushing lower to 13.0
# keeps shrinking the games error but overshoots points to -5.1, and points are
# what the board is built on.
LEAGUE_AVG_GAMES = 14.0
AVAILABILITY_PRIOR_WEIGHT = 10.0

# Age adjustment, MEASURED not assumed. Derived 2026-08-03 by regressing
# log(actual / projected) on age across 7 backtest folds (2018->2025, top 200 by
# model rank per fold), then refitting with each fold held out to test stability:
#
#   RB  slope -0.046/yr   (leave-one-out range -0.034 .. -0.056)  STABLE
#   WR  slope -0.024/yr   (leave-one-out range -0.017 .. -0.029)  STABLE
#   QB  slope +0.007/yr   (range -0.003 .. +0.020, crosses zero)  NOT APPLIED
#   TE  slope +0.000/yr   (range -0.017 .. +0.009, crosses zero)  NOT APPLIED
#
# QB and TE are deliberately absent: their slopes flip sign depending on which
# fold is held out, so an adjustment there would be fitting noise. That RBs
# decline steeply while QBs don't is also what football knowledge predicts,
# which is mild independent support that the RB/WR effects are real.
#
# Applied RELATIVE to a reference age (the position's mean), so a typical-aged
# player is unchanged and only the age *differential* moves. The raw fitted
# intercepts sat near 0.65, but that reflects the model's overall +9pt
# over-projection, not aging — anchoring keeps those two corrections separate.
#
# Refit periodically; these are empirical constants, not laws.
AGE_SLOPES = {"RB": -0.046, "WR": -0.024}
AGE_REFERENCE = {"QB": 28.0, "RB": 26.0, "WR": 26.0, "TE": 26.0}


def age_multiplier(position: pd.Series, age: pd.Series) -> pd.Series:
    """Multiplicative age adjustment, 1.0 where no stable effect was measured."""
    slope = position.map(AGE_SLOPES)
    ref = position.map(AGE_REFERENCE)
    years = pd.to_numeric(age, errors="coerce") - ref
    mult = np.exp(slope.astype(float) * years)
    # No measured slope, or unknown age -> no adjustment.
    return mult.where(slope.notna() & years.notna(), 1.0)


# Depth-chart (role) adjustment, MEASURED not assumed. Derived 2026-08-03 as
# sum(actual) / sum(projected) by position and depth rank, across 7 backtest
# folds (2018->2025), using each target season's SEASON-OPENING depth chart.
#
# The statistic matters. These were first fit as the MEDIAN ratio, which
# under-projected badly: outcomes are right-skewed (a few players hugely
# outperform), so the median of a ratio sits well below the ratio that actually
# balances totals — 0.913 vs 0.997 for TE1, 0.268 vs 0.439 for TE3. That alone
# produced a 12% tight-end shortfall. sum/sum is the ratio that makes aggregate
# projections unbiased and weights by projection size, which is what a draft
# board cares about. Out-of-sample it beat the median on both MAE (55.0 vs 55.2)
# and rank correlation (0.649 vs 0.642).
#
# This is the model's single largest correction, and it addresses its biggest
# blind spot: projections are built from last season's usage, so a player who is
# now a backup still carries a starter's workload forward. A backup quarterback
# delivers about 14% of what the naive projection says.
#
# Every cell has n >= 21 and a tight leave-one-out range (all spreads < 0.25),
# so unlike the age slopes none of these flip direction depending on the fold
# held out:
#
#   QB1 1.046 (n=193)   QB2 0.312 (n=107)   QB3 0.158 (n=21)
#   RB1 1.015 (n=244)   RB2 0.859 (n=172)   RB3 0.561 (n=108)
#   TE1 0.997 (n=242)   TE2 0.730 (n=178)   TE3 0.437 (n=120)
#   WR1 0.989 (n=522)   WR2 0.750 (n=231)   WR3 0.512 (n=124)
#   ...rank 3 covers 3-and-deeper.
#
# Fitted on the full population rather than only top-ranked projections: the
# model rarely ranks a backup QB highly, so a top-250 cut left QB2 with n=9 and
# fell back to a pooled 0.649 — wildly wrong for a player who does not take
# snaps. Refit periodically; these are empirical constants, not laws.
DEPTH_MULTIPLIERS = {
    ("QB", 1): 1.046, ("QB", 2): 0.312, ("QB", 3): 0.158,
    ("RB", 1): 1.015, ("RB", 2): 0.859, ("RB", 3): 0.561,
    ("TE", 1): 0.997, ("TE", 2): 0.730, ("TE", 3): 0.437,
    ("WR", 1): 0.989, ("WR", 2): 0.750, ("WR", 3): 0.512,
}
DEPTH_RANK_CAP = 3


def depth_multiplier(position: pd.Series, depth_rank: pd.Series) -> pd.Series:
    """Role adjustment. 1.0 where depth is unknown — never penalize on absence."""
    rank = pd.to_numeric(depth_rank, errors="coerce").clip(upper=DEPTH_RANK_CAP)
    pairs = zip(position.fillna(""), rank)
    mult = pd.Series(
        [DEPTH_MULTIPLIERS.get((p, int(r))) if pd.notna(r) else None
         for p, r in pairs],
        index=position.index, dtype="float64")
    return mult.fillna(1.0)


# Value over replacement. Raw projected points are NOT comparable across
# positions: you start one QB but three WRs, so a QB's points are measured
# against a readily available replacement QB, not against a WR. Without this,
# every startable QB outranks every skill player — which is why consensus looks
# "wrong" about quarterbacks when it isn't.
#
# Ranks below are the last starter at each position for Underdog's lineup in a
# 12-team draft: 1 QB / 2 RB / 3 WR / 1 TE / 1 FLEX. The 12 flex spots are
# apportioned to RB and WR (where they are almost always spent) rather than
# dropped. Override via build_projections(replacement_ranks=...).
REPLACEMENT_RANKS = {"QB": 12, "RB": 29, "WR": 42, "TE": 13}

# Underdog best-ball scoring, taken from the platform's own rules rather than
# derived from nflverse's fantasy_points column. That column uses generic
# standard scoring, which differs from Underdog in two ways that matter:
# passing TDs are 4 (not 6) and interceptions are -1 (not -2). Computing from
# components keeps the projection on the same scale as the actual contest.
BASE_SCORING = {
    "passing_yards": 0.04,
    "passing_tds": 4.0,
    "passing_interceptions": -1.0,
    "rushing_yards": 0.1,
    "rushing_tds": 6.0,
    "receiving_yards": 0.1,
    "receiving_tds": 6.0,
    "receptions": 0.5,
    "passing_2pt_conversions": 2.0,
    "rushing_2pt_conversions": 2.0,
    "receiving_2pt_conversions": 2.0,
    "rushing_fumbles_lost": -2.0,
    "receiving_fumbles_lost": -2.0,
    "sack_fumbles_lost": -2.0,
}

# Only the reception value changes between formats; everything else follows
# Underdog. "underdog" and "half" are the same thing, kept as separate names
# because that is how each gets talked about.
SCORING_FORMATS = {"underdog": 0.5, "half": 0.5, "ppr": 1.0, "standard": 0.0}
DEFAULT_SCORING = "underdog"


def scoring_weights(scoring: str = DEFAULT_SCORING) -> dict:
    """Underdog weights with the reception value swapped for the given format."""
    weights = dict(BASE_SCORING)
    weights["receptions"] = SCORING_FORMATS.get(scoring, BASE_SCORING["receptions"])
    return weights


def compute_fantasy_points(df: pd.DataFrame, scoring: str = DEFAULT_SCORING) -> pd.Series:
    """Score a stat frame from components using the chosen format."""
    weights = scoring_weights(scoring)
    total = pd.Series(0.0, index=df.index)
    missing = []
    for col, weight in weights.items():
        if col in df.columns:
            total = total + pd.to_numeric(df[col], errors="coerce").fillna(0) * weight
        else:
            missing.append(col)
    if missing:
        print(f"   ⚠️  scoring columns absent, treated as zero: {missing}")
    return total

RATE_COLS = [
    "targets", "receptions", "receiving_yards", "receiving_tds",
    "carries", "rushing_yards", "rushing_tds",
    "attempts", "completions", "passing_yards", "passing_tds",
    "passing_interceptions", "fantasy_points", "fantasy_points_ppr",
]


def _norm_name(value) -> str:
    v = str(value or "").lower()
    v = re.sub(r"[^a-z ]", "", v)
    return re.sub(r"\s+", " ", v).strip()


def _season_type_order(values: pd.Series) -> pd.Series:
    """Chronological ordering for season phases when resolving latest team."""
    order = {"PRE": 0, "REG": 1, "POST": 2}
    cleaned = values.astype("string").str.upper().str.strip()
    return cleaned.map(order).fillna(1).astype(int)


def latest_team_by_player(played: pd.DataFrame) -> pd.Series:
    """Most recent team from true chronological order, not week number alone."""
    if played.empty or "team" not in played.columns:
        return pd.Series(dtype="object", name="team_prior")

    ordered = played.copy()
    sort_cols = []
    ascending = []

    if "season" in ordered.columns:
        ordered["__season_order"] = pd.to_numeric(ordered["season"], errors="coerce")
        sort_cols.append("__season_order")
        ascending.append(True)
    if "season_type" in ordered.columns:
        ordered["__season_type_order"] = _season_type_order(ordered["season_type"])
        sort_cols.append("__season_type_order")
        ascending.append(True)
    if "week" in ordered.columns:
        ordered["__week_order"] = pd.to_numeric(ordered["week"], errors="coerce")
        sort_cols.append("__week_order")
        ascending.append(True)
    if "game_id" in ordered.columns:
        ordered["__game_id_order"] = ordered["game_id"].astype("string")
        sort_cols.append("__game_id_order")
        ascending.append(True)

    if sort_cols:
        ordered = ordered.sort_values(sort_cols, ascending=ascending, na_position="last")

    return (ordered.groupby("player_id", dropna=False)["team"]
                  .last()
                  .rename("team_prior"))


# ---------------------------------------------------------------------------
# per-game rates
# ---------------------------------------------------------------------------

def per_game_rates(stats: pd.DataFrame, scoring: str = "ppr") -> pd.DataFrame:
    """Collapse weekly stats to games played and per-game rates."""
    if stats.empty:
        return pd.DataFrame()

    pool = stats[stats["position"].isin(POSITION_GROUPS)].copy()
    if pool.empty:
        return pd.DataFrame()

    pool["fantasy_pts"] = compute_fantasy_points(pool, scoring)

    # Only count games the player actually appeared in. Counting a bye or an
    # inactive as a zero would understate the rate rather than the availability,
    # which is a separate term below.
    present = [c for c in RATE_COLS if c in pool.columns] + ["fantasy_pts"]
    played = pool[pool[present].abs().sum(axis=1) > 0].copy()
    if played.empty:
        return pd.DataFrame()

    grouped = played.groupby(["player_id", "player_display_name", "position"], dropna=False)
    totals = grouped[present].sum()
    out = totals.div(grouped.size(), axis=0).add_suffix("_pg")
    out["games_played"] = grouped.size()

    for col in ("target_share", "air_yards_share", "wopr"):
        if col in played.columns:
            out[col] = grouped[col].mean()

    last_team = latest_team_by_player(played)
    return out.reset_index().merge(last_team.reset_index(), how="left", on="player_id")


def position_means(rates: pd.DataFrame) -> pd.DataFrame:
    """Positional mean rate, computed over players with a real sample.

    Restricting the prior to 4+ game players keeps one-game cameos from
    dragging the mean down and making the prior itself the outlier.
    """
    if rates.empty:
        return pd.DataFrame()
    qualified = rates[rates["games_played"] >= 4]
    if qualified.empty:
        qualified = rates
    cols = [c for c in rates.columns if c.endswith("_pg")]
    return qualified.groupby("position")[cols].mean().add_suffix("_prior").reset_index()


def shrink_rates(rates: pd.DataFrame, priors: pd.DataFrame) -> pd.DataFrame:
    """Empirical-Bayes style shrinkage toward the positional mean.

        rate_hat = (rate * games + prior * k) / (games + k)

    Small samples land near the positional mean; full seasons keep their own
    rate almost intact.
    """
    if rates.empty or priors.empty:
        return rates

    out = rates.merge(priors, how="left", on="position")
    g = out["games_played"].astype(float)
    # Team change and short season are distinct failure modes pulling in
    # opposite directions, so they get separate prior weights.
    moved = out["changed_team"].fillna(False).astype(bool)
    partial = (g < 12) & ~moved
    k = np.select(
        [moved, partial],
        [SHRINK_GAMES_TEAM_CHANGE, SHRINK_GAMES_PARTIAL_SEASON],
        default=SHRINK_GAMES,
    )

    for col in [c for c in rates.columns if c.endswith("_pg")]:
        prior = out.get(f"{col}_prior")
        if prior is None:
            continue
        prior = prior.fillna(out[col])
        out[f"{col}_hat"] = (out[col] * g + prior * k) / (g + k)

    out["shrink_k"] = k
    return out.drop(columns=[c for c in out.columns if c.endswith("_prior")])


def fit_ecr_curves(df: pd.DataFrame, min_games: int = 12, min_fit: int = 8):
    """Fit season PPR against consensus rank, SEPARATELY PER POSITION.

    A single global curve is wrong because ECR is an *overall* rank while points
    are position-specific: pick 56 is roughly QB6 (≈300 pts) but WR30 (far
    fewer). Fitting one curve across both maps every mid-round QB to a skill
    player's point total and buries them — which is exactly what happened to
    Burrow and Daniels.

    Fits in log-log space since points decay roughly geometrically in rank, and
    uses only clean full seasons so injury-shortened years don't flatten a curve
    meant to describe healthy output.

    Returns {position: callable}, plus a global fallback under None.
    """
    usable = df[(pd.to_numeric(df["games_played"], errors="coerce") >= min_games)
                & df["ecr"].notna() & df["proj_raw_ppr"].notna()
                & (df["proj_raw_ppr"] > 0)]
    if len(usable) < 25:
        return {}

    def make(subset):
        coeffs = np.polyfit(np.log(subset["ecr"].clip(lower=1)),
                            np.log(subset["proj_raw_ppr"]), 1)

        def curve(ecr_value):
            if pd.isna(ecr_value):
                return np.nan
            return float(np.exp(np.polyval(coeffs, np.log(max(float(ecr_value), 1.0)))))
        return curve

    curves = {None: make(usable)}
    for pos, group in usable.groupby("position"):
        # Too few points to fit a position means the global curve is the safer
        # estimate than an overfit line through a handful of players.
        if len(group) >= min_fit:
            curves[pos] = make(group)
    fitted = [p for p in curves if p is not None]
    print(f"   📈 consensus curves fitted per position: {sorted(fitted)}"
          f"{' (others fall back to global)' if len(fitted) < 4 else ''}")
    return curves


def apply_consensus_prior(df: pd.DataFrame) -> pd.DataFrame:
    """Shrink per-game scoring toward a consensus-implied level, not a flat
    positional average.

    This fixes the worst failure of the positional-mean prior: a player who
    missed time still has a *reliable* per-game rate, but shrinking it toward
    "average QB (including third-stringers)" buries him. Consensus already
    encodes that Burrow and Daniels are elite despite short 2025 seasons, so it
    is a far better prior than the position mean when the sample is thin.

    Note the weighting keeps this from becoming circular: full-season players
    are dominated by their own measured rate and barely move, so the model stays
    independent where it has real evidence. Consensus only fills the gap where
    we genuinely have no information of our own.
    """
    if df.empty or "ecr" not in df.columns:
        return df

    curves = fit_ecr_curves(df)
    if not curves:
        print("   ⚠️  could not fit consensus curves — positional prior only")
        return df

    out = df.copy()
    g = pd.to_numeric(out["games_played"], errors="coerce").fillna(0)
    k = out["shrink_k"].astype(float) if "shrink_k" in out.columns else SHRINK_GAMES

    def implied(row):
        curve = curves.get(row["position"]) or curves.get(None)
        return curve(row["ecr"]) if curve else np.nan

    ecr_season = out.apply(implied, axis=1)

    # Blend SEASON TOTALS, not per-game rates.
    #
    # Own season total already carries this model's availability view
    # (rate x proj_games). The consensus number is a full-season expectation
    # that prices in its own injury risk. Blending rates and *then* applying
    # proj_games would discount availability twice — once in my games estimate
    # and again by way of a rate pulled toward a number that already assumed a
    # shorter season. Burrow at 8 games was losing roughly half his projection
    # to that double count.
    own_season = pd.to_numeric(out.get("proj_raw_ppr"), errors="coerce")
    blended = ((own_season * g).fillna(0) + (ecr_season * k).fillna(0)) / (g + k)

    # No consensus rank means no market opinion to lean on — keep the
    # positional-mean-shrunk projection, which correctly regresses thin samples.
    blended = blended.where(ecr_season.notna(), own_season)

    out["ppr_season_hat"] = blended
    out["ecr_implied_ppr"] = ecr_season.round(1)
    out["consensus_weight"] = np.where(ecr_season.notna(), (k / (g + k)).round(3), np.nan)
    return out


def project_games(games_played: pd.Series) -> pd.Series:
    """Shrink last season's availability toward the league average."""
    g = games_played.astype(float).clip(upper=FULL_SEASON_GAMES)
    w = AVAILABILITY_PRIOR_WEIGHT
    blended = (g * g + LEAGUE_AVG_GAMES * w) / (g + w)
    return blended.clip(upper=FULL_SEASON_GAMES).round(1)


# ---------------------------------------------------------------------------
# consensus (ECR)
# ---------------------------------------------------------------------------

def attach_ecr(df: pd.DataFrame, ecr: pd.DataFrame,
               playerids: pd.DataFrame) -> pd.DataFrame:
    """Join best-ball consensus by FantasyPros id, falling back to merge name.

    ID alone matches ~83%; adding the pre-normalized merge-name fallback takes
    it to ~94%, and every remaining miss is a team defense (no player id
    exists). Report coverage so a silent regression in the join is visible.
    """
    if df.empty or ecr.empty:
        df = df.copy()
        for c in ("ecr", "ecr_sd", "ecr_best", "ecr_worst", "bye"):
            df[c] = np.nan
        return df

    board = ecr.copy()
    board["fpid"] = board["id"].astype(str).str.replace(r"\.0$", "", regex=True)
    board["mk"] = board.get("mergename", board.get("player")).map(_norm_name)

    if not playerids.empty:
        ids = playerids.dropna(subset=["gsis_id"]).copy()
        ids["fpid"] = ids["fantasypros_id"].astype(str).str.replace(r"\.0$", "", regex=True)
        ids["mk"] = ids["merge_name"].map(_norm_name)
        by_id = ids.drop_duplicates("fpid").set_index("fpid")["gsis_id"]
        by_name = ids.drop_duplicates("mk").set_index("mk")["gsis_id"]
        board["gsis_id"] = board["fpid"].map(by_id)
        miss = board["gsis_id"].isna()
        board.loc[miss, "gsis_id"] = board.loc[miss, "mk"].map(by_name)
    else:
        board["gsis_id"] = np.nan

    non_dst = board[board["pos"] != "DST"]
    if len(non_dst):
        rate = non_dst["gsis_id"].notna().mean()
        flag = "✅" if rate >= 0.90 else "⚠️ "
        print(f"   {flag} ECR crosswalk matched {rate:.1%} of non-DST players")

    cols = {"gsis_id": "gsis_id", "ecr": "ecr", "sd": "ecr_sd",
            "best": "ecr_best", "worst": "ecr_worst", "bye": "bye"}
    have = {k: v for k, v in cols.items() if k in board.columns}
    slim = (board.dropna(subset=["gsis_id"])[list(have)]
                 .rename(columns=have)
                 .drop_duplicates(subset=["gsis_id"]))
    return df.merge(slim, how="left", left_on="player_id", right_on="gsis_id") \
             .drop(columns=["gsis_id"], errors="ignore")


def impute_rookies(df: pd.DataFrame, rookies: pd.DataFrame) -> pd.DataFrame:
    """Place rookies on the model's scale using only consensus rank.

    nflverse has no college data, so a rookie has no usage history to project.
    Rather than omit them (they'd vanish from the draft board) or invent a
    number, fit projected-points against ECR on the veterans we DID model, then
    read rookies off that curve. Flagged as ecr_imputed so it's never mistaken
    for a usage-based projection.
    """
    if df.empty or rookies.empty:
        return df

    fit = df[df["ecr"].notna() & df["proj_ppr"].notna() & (df["proj_ppr"] > 0)]
    if len(fit) < 20:
        print("   ⚠️  too few matched veterans to fit the ECR curve — rookies omitted")
        return df

    # Points decay roughly geometrically in rank, so fit in log space.
    coeffs = np.polyfit(np.log(fit["ecr"].clip(lower=1)), np.log(fit["proj_ppr"]), 1)

    def from_ecr(ecr_value):
        if pd.isna(ecr_value):
            return np.nan
        return float(np.exp(np.polyval(coeffs, np.log(max(float(ecr_value), 1.0)))))

    add = rookies.copy()
    add["proj_ppr"] = add["ecr"].map(from_ecr)
    add = add[add["proj_ppr"].notna()]
    if add.empty:
        return df

    add["proj_games"] = LEAGUE_AVG_GAMES
    for col in ("age_mult", "depth_mult"):
        if col not in add.columns:
            add[col] = 1.0
    add["proj_ppg"] = (add["proj_ppr"] / add["proj_games"]).round(2)
    add["proj_source"] = "ecr_imputed"
    add["games_played"] = 0

    print(f"   ℹ️  {len(add)} rookies/newcomers imputed from consensus rank")
    return pd.concat([df, add], ignore_index=True)


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------

def build_projections(stats: pd.DataFrame, rosters: pd.DataFrame,
                      ecr: pd.DataFrame, playerids: pd.DataFrame,
                      replacement_ranks: dict | None = None,
                      scoring: str = DEFAULT_SCORING,
                      depth: pd.DataFrame | None = None) -> pd.DataFrame:
    """Season-long projections for QB/RB/WR/TE, with consensus alongside."""
    rates = per_game_rates(stats, scoring=scoring)
    if rates.empty:
        print("   ⚠️  no usable stats — projections skipped")
        return pd.DataFrame()

    # Current-season roster decides team, and whether a player moved.
    active = pd.DataFrame()
    if not rosters.empty:
        active = rosters.copy()
        if "status" in active.columns:
            active = active[active["status"].isin(["ACT", "RES", "DEV"])]
        # Age as of Sept 1 of the projected season — the football-relevant age,
        # not age at the time the roster file was published.
        if "birth_date" in active.columns and "season" in active.columns:
            born = pd.to_datetime(active["birth_date"], errors="coerce")
            season_start = pd.to_datetime(
                active["season"].astype("Int64").astype(str) + "-09-01",
                errors="coerce")
            active["age"] = ((season_start - born).dt.days / 365.25).round(1)
        keep = [c for c in ["gsis_id", "team", "position", "full_name", "age",
                            "years_exp", "rookie_year", "depth_chart_position"]
                if c in active.columns]
        active = (active[keep]
                  .dropna(subset=["gsis_id"])
                  .drop_duplicates(subset=["gsis_id"])
                  .rename(columns={"gsis_id": "player_id", "team": "team_now"}))

    df = rates.copy()
    if not active.empty:
        merge_cols = [c for c in ["player_id", "team_now", "years_exp", "age"]
                      if c in active.columns]
        df = df.merge(active[merge_cols], how="left", on="player_id")
        # No current roster row means not on a 2026 roster — drop rather than
        # project someone who isn't in the league.
        before = len(df)
        df = df[df["team_now"].notna()]
        if before - len(df):
            print(f"   ℹ️  dropped {before - len(df)} players not on a current roster")
    else:
        df["team_now"] = df["team_prior"]
        df["years_exp"] = np.nan
        df["age"] = np.nan

    df["changed_team"] = (df["team_now"] != df["team_prior"]) & df["team_prior"].notna()

    shrunk = shrink_rates(df, position_means(df))
    shrunk["proj_games"] = project_games(shrunk["games_played"])

    # Component season totals from positional-mean-shrunk per-game rates.
    for col in [c for c in shrunk.columns if c.endswith("_pg_hat")]:
        base = col[:-len("_pg_hat")]
        shrunk[f"proj_{base}"] = (shrunk[col] * shrunk["proj_games"]).round(1)

    # Scoring gets the consensus-anchored treatment rather than the positional
    # mean, so it needs ECR joined before the final projection is computed.
    if "proj_fantasy_pts" in shrunk.columns:
        shrunk = shrunk.rename(columns={"proj_fantasy_pts": "proj_raw_ppr"})
    else:
        shrunk["proj_raw_ppr"] = np.nan

    out = attach_ecr(shrunk, ecr, playerids)
    out = apply_consensus_prior(out)

    # ppr_season_hat is already a season total (see apply_consensus_prior) — do
    # not multiply by proj_games again.
    if "ppr_season_hat" in out.columns:
        out["proj_ppr"] = out["ppr_season_hat"].round(1)
    else:
        out["proj_ppr"] = out["proj_raw_ppr"]
    out["age_mult"] = age_multiplier(out["position"], out.get("age")).round(3)
    if depth is not None and not depth.empty:
        out = out.merge(depth[["player_id", "depth_rank"]], how="left",
                        on="player_id")
        covered = out["depth_rank"].notna().mean()
        print(f"   🪜 depth chart covered {covered:.1%} of projected players")
    else:
        out["depth_rank"] = np.nan
    out["depth_mult"] = depth_multiplier(out["position"], out["depth_rank"]).round(3)
    out["proj_ppr"] = (out["proj_ppr"] * out["age_mult"] * out["depth_mult"]).round(1)
    out["proj_ppg"] = (out["proj_ppr"] / out["proj_games"]).round(2)
    out["proj_source"] = "model"

    # Rookies: on a roster, no 2025 usage, but consensus has an opinion.
    if not active.empty and not ecr.empty:
        known = set(out["player_id"])
        newcomers = active[~active["player_id"].isin(known)].copy()
        if "position" in newcomers.columns:
            newcomers = newcomers[newcomers["position"].isin(POSITION_GROUPS)]
        newcomers = newcomers.rename(columns={"full_name": "player_display_name"})
        newcomers = attach_ecr(newcomers, ecr, playerids)
        newcomers = newcomers[newcomers["ecr"].notna()]
        out = impute_rookies(out, newcomers)

    # Positional rank first — replacement level is defined within a position.
    out["model_pos_rank"] = out.groupby("position")["proj_ppr"].rank(ascending=False,
                                                                    method="min")

    # Points of the last startable player at each position become that
    # position's baseline; everything is then measured as points above it.
    ranks = replacement_ranks or REPLACEMENT_RANKS
    baselines = {}
    for pos, cutoff in ranks.items():
        group = out[out["position"].eq(pos)].sort_values("proj_ppr", ascending=False)
        if group.empty:
            continue
        idx = min(int(cutoff), len(group)) - 1
        baselines[pos] = float(group["proj_ppr"].iloc[idx])
    out["replacement_ppr"] = out["position"].map(baselines)
    out["vorp"] = (out["proj_ppr"] - out["replacement_ppr"]).round(1)

    # Overall rank is by VORP, not raw points — this is the draft-relevant order.
    out["model_rank"] = out["vorp"].rank(ascending=False, method="min")
    out["ecr_vs_model"] = (out["ecr"] - out["model_rank"]).round(1)

    # Concatenating the imputed rookies leaves these columns as object dtype
    # (rookies have no changed_team / games_played), and np.select rejects
    # anything that isn't a real boolean array. Coerce before branching.
    games = pd.to_numeric(out["games_played"], errors="coerce").fillna(0)
    moved = out["changed_team"].fillna(False).astype(bool)

    out["confidence"] = np.select(
        [
            out["proj_source"].eq("ecr_imputed").to_numpy(dtype=bool),
            (games < 4).to_numpy(dtype=bool),
            moved.to_numpy(dtype=bool),
            (games >= 12).to_numpy(dtype=bool),
        ],
        ["no prior-season data", "small sample", "changed teams", "full season"],
        default="partial season",
    )

    cols = [c for c in [
        "player_id", "player_display_name", "position", "team_now", "team_prior",
        "changed_team", "years_exp", "age", "games_played", "proj_games",
        "proj_ppr", "proj_ppg", "proj_raw_ppr", "ecr_implied_ppr",
        "consensus_weight", "age_mult", "depth_rank", "depth_mult",
        "vorp", "replacement_ppr",
        "model_rank", "model_pos_rank",
        "ecr", "ecr_sd", "ecr_best", "ecr_worst", "ecr_vs_model", "bye",
        "proj_source", "confidence", "target_share", "wopr",
        "proj_targets", "proj_receptions", "proj_receiving_yards",
        "proj_receiving_tds", "proj_carries", "proj_rushing_yards",
        "proj_rushing_tds", "proj_attempts", "proj_passing_yards",
        "proj_passing_tds", "proj_passing_interceptions",
    ] if c in out.columns]

    return (out[cols]
            .sort_values("vorp", ascending=False)
            .reset_index(drop=True))
