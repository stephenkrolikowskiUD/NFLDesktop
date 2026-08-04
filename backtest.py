# 🔬 Backtest for the season-long projection model
#
# Trains on season N, predicts season N+1, scores against what actually
# happened. Answers three questions the live model can't answer about itself:
#
#   1. Does it beat a naive carry-forward of last season's points?
#   2. Are the per-position biases (WR low, TE high) real, or artifacts of
#      comparing against a single 2026 consensus snapshot?
#   3. Is the availability projection calibrated, or systematically off?
#
# IMPORTANT LIMITATION — read before trusting any of this:
# nflverse's ff_rankings carries a SINGLE scrape date (2026-07-31), so no
# historical expert consensus exists. The consensus-anchored prior that the
# live model relies on therefore CANNOT be validated directly. As a stand-in,
# `--proxy-consensus` substitutes each player's prior-season finish rank, which
# is information the market would plainly have had. That tests the *mechanism*
# of anchoring, not the quality of real expert rankings.
#
# Survivorship note: only players who appear in season N+1 are scored. A player
# who retired or never played isn't a projection error you could have acted on,
# but it does mean these numbers describe accuracy among players who played.

import argparse

import numpy as np
import pandas as pd

import nflverse_loader as nv
import projections as pj


def actual_season_points(stats: pd.DataFrame, scoring: str) -> pd.DataFrame:
    """Season totals for the outcome year, on the same scoring as the model."""
    if stats.empty:
        return pd.DataFrame()
    pool = stats[stats["position"].isin(pj.POSITION_GROUPS)].copy()
    if pool.empty:
        return pd.DataFrame()
    pool["pts"] = pj.compute_fantasy_points(pool, scoring)
    played = pool[pool["pts"].notna()]
    grouped = played.groupby(["player_id", "position"], dropna=False)
    out = grouped["pts"].sum().reset_index().rename(columns={"pts": "actual_pts"})
    out["actual_games"] = grouped.size().values
    return out


def build_proxy_consensus(prior_stats: pd.DataFrame, playerids: pd.DataFrame,
                          scoring: str) -> pd.DataFrame:
    """Fake an ECR table from prior-season finish, shaped like ff_rankings.

    Ranks by prior-season VORP so the proxy is an OVERALL value rank, matching
    what ECR actually is, rather than a within-position rank.
    """
    if prior_stats.empty or playerids.empty:
        return pd.DataFrame()

    totals = actual_season_points(prior_stats, scoring)
    if totals.empty:
        return pd.DataFrame()

    # Same replacement logic as the model, so the proxy is on a comparable scale.
    baselines = {}
    for pos, cutoff in pj.REPLACEMENT_RANKS.items():
        grp = totals[totals["position"].eq(pos)].sort_values("actual_pts",
                                                             ascending=False)
        if grp.empty:
            continue
        baselines[pos] = float(grp["actual_pts"].iloc[min(cutoff, len(grp)) - 1])
    totals["vorp"] = totals["actual_pts"] - totals["position"].map(baselines)
    totals = totals.dropna(subset=["vorp"])
    totals["ecr"] = totals["vorp"].rank(ascending=False, method="min")

    ids = playerids.dropna(subset=["gsis_id", "fantasypros_id"]).drop_duplicates("gsis_id")
    merged = totals.merge(
        ids[["gsis_id", "fantasypros_id", "merge_name"]],
        how="inner", left_on="player_id", right_on="gsis_id")
    if merged.empty:
        return pd.DataFrame()

    return pd.DataFrame({
        "id": merged["fantasypros_id"],
        "pos": merged["position"],
        "ecr": merged["ecr"],
        "sd": np.nan,
        "best": np.nan,
        "worst": np.nan,
        "bye": np.nan,
        "mergename": merged["merge_name"],
        "page_type": "proxy",
    })


def run_fold(train_season: int, scoring: str, playerids: pd.DataFrame,
             use_proxy: bool) -> pd.DataFrame:
    """Project from train_season, score against train_season + 1."""
    target = train_season + 1

    train_stats = nv.load_player_stats(seasons=[train_season])
    target_stats = nv.load_player_stats(seasons=[target])
    rosters = nv.load_rosters(seasons=[target])
    if train_stats.empty or target_stats.empty:
        return pd.DataFrame()

    ecr = (build_proxy_consensus(train_stats, playerids, scoring)
           if use_proxy else pd.DataFrame())

    proj = pj.build_projections(train_stats, rosters, ecr, playerids,
                               scoring=scoring)
    if proj.empty:
        return pd.DataFrame()

    actual = actual_season_points(target_stats, scoring)
    merged = proj.merge(actual.drop(columns=["position"]), how="inner",
                        on="player_id")

    # Naive baseline: carry last season's total forward unchanged. Any model
    # that can't beat this is not earning its complexity.
    naive = actual_season_points(train_stats, scoring)[["player_id", "actual_pts"]]
    merged = merged.merge(naive.rename(columns={"actual_pts": "naive_pts"}),
                          how="left", on="player_id")

    merged["train_season"] = train_season
    merged["target_season"] = target
    return merged


def spearman(a: pd.Series, b: pd.Series) -> float:
    valid = a.notna() & b.notna()
    if valid.sum() < 5:
        return np.nan
    return float(a[valid].corr(b[valid], method="spearman"))


def evaluate(df: pd.DataFrame, label: str, top_n: int | None = None) -> dict:
    """Accuracy of projection vs actual, alongside the naive baseline."""
    if df.empty:
        return {}
    d = df.copy()
    if top_n:
        # Judge on the players you'd actually draft, not the deep bench where
        # everyone projects near zero and correlations look flattering.
        d = d.nsmallest(top_n, "model_rank")

    err = d["proj_ppr"] - d["actual_pts"]
    naive_err = d["naive_pts"] - d["actual_pts"]

    return {
        "label": label,
        "n": len(d),
        "spearman": round(spearman(d["proj_ppr"], d["actual_pts"]), 3),
        "naive_spearman": round(spearman(d["naive_pts"], d["actual_pts"]), 3),
        "MAE": round(err.abs().mean(), 1),
        "naive_MAE": round(naive_err.abs().mean(), 1),
        "bias": round(err.mean(), 1),
        "games_bias": round((d["proj_games"] - d["actual_games"]).mean(), 2),
    }


def position_bias(df: pd.DataFrame, top_n: int | None = None) -> pd.DataFrame:
    """Signed error by position — the direct test of the WR-low / TE-high claim."""
    if df.empty:
        return pd.DataFrame()
    d = df.copy()
    if top_n:
        d = d.nsmallest(top_n, "model_rank")
    d["err"] = d["proj_ppr"] - d["actual_pts"]
    out = d.groupby("position").agg(
        n=("err", "size"),
        mean_err=("err", "mean"),
        median_err=("err", "median"),
        mean_actual=("actual_pts", "mean"),
    ).round(1)
    # Percentage error makes positions comparable despite different point scales.
    out["pct_err"] = (out["mean_err"] / out["mean_actual"] * 100).round(1)
    return out


def main():
    ap = argparse.ArgumentParser(description="Backtest the projection model.")
    ap.add_argument("--start", type=int, default=2018)
    ap.add_argument("--end", type=int, default=2024,
                    help="last TRAIN season (predicts end+1)")
    ap.add_argument("--scoring", default=pj.DEFAULT_SCORING)
    ap.add_argument("--top", type=int, default=150,
                    help="evaluate on the top N by model rank")
    ap.add_argument("--proxy-consensus", action="store_true",
                    help="substitute prior-season finish for missing historical ECR")
    args = ap.parse_args()

    print(f"🔬 Backtest — scoring={args.scoring}, folds "
          f"{args.start}->{args.start+1} .. {args.end}->{args.end+1}")
    if args.proxy_consensus:
        print("   using PROXY consensus (prior-season finish). Real historical")
        print("   ECR does not exist — nflverse ships one scrape date only.")
    else:
        print("   no consensus anchor — testing the base rate model alone.")
    print()

    playerids = nv.load_ff_playerids()
    folds = []
    for train in range(args.start, args.end + 1):
        fold = run_fold(train, args.scoring, playerids, args.proxy_consensus)
        if fold.empty:
            print(f"   ⚠️  fold {train} produced nothing — skipped")
            continue
        m = evaluate(fold, str(train), top_n=args.top)
        print(f"   {train}->{train+1}: n={m['n']:4d} "
              f"spearman={m['spearman']:.3f} (naive {m['naive_spearman']:.3f}) "
              f"MAE={m['MAE']:6.1f} (naive {m['naive_MAE']:6.1f}) "
              f"bias={m['bias']:+7.1f} games_bias={m['games_bias']:+.2f}")
        folds.append(fold)

    if not folds:
        print("\n❌ no usable folds")
        return

    allf = pd.concat(folds, ignore_index=True)

    print(f"\n{'='*74}\nPOOLED — top {args.top} by model rank per fold\n{'='*74}")
    pooled = evaluate(allf, "pooled", top_n=None)
    top_only = pd.concat([f.nsmallest(args.top, "model_rank") for f in folds],
                         ignore_index=True)
    m = evaluate(top_only, "pooled-top")
    print(f"   rank correlation : {m['spearman']:.3f}   vs naive {m['naive_spearman']:.3f}")
    print(f"   MAE (points)     : {m['MAE']:.1f}     vs naive {m['naive_MAE']:.1f}")
    print(f"   mean bias        : {m['bias']:+.1f} points "
          f"({'over' if m['bias']>0 else 'under'}-projecting)")
    print(f"   games bias       : {m['games_bias']:+.2f} games")
    verdict = ("BEATS naive" if m["MAE"] < m["naive_MAE"] else "LOSES to naive")
    print(f"   verdict on MAE   : {verdict}")

    print(f"\n{'='*74}\nBIAS BY POSITION — top {args.top} per fold\n{'='*74}")
    print(position_bias(top_only).to_string())

    print(f"\n{'='*74}\nBIAS BY CONFIDENCE TIER\n{'='*74}")
    t = top_only.copy()
    t["err"] = t["proj_ppr"] - t["actual_pts"]
    print(t.groupby("confidence").agg(
        n=("err", "size"), mean_err=("err", "mean"),
        mean_actual=("actual_pts", "mean")).round(1).to_string())

    print(f"\n{'='*74}\nAVAILABILITY CALIBRATION\n{'='*74}")
    a = top_only.dropna(subset=["proj_games", "actual_games"])
    print(f"   mean projected games: {a['proj_games'].mean():.1f}")
    print(f"   mean actual games   : {a['actual_games'].mean():.1f}")
    print(f"   correlation         : {spearman(a['proj_games'], a['actual_games']):.3f}")


if __name__ == "__main__":
    main()
