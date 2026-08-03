# 🏈 nflverse data adapter
#
# Every loader here tries nflreadpy first, then falls back to reading the
# parquet release asset directly from GitHub.
#
# The fallback is not paranoia. nflreadpy 0.1.5 hardcodes season bounds
# (e.g. load_pbp() raises ValueError: "Season must be between 1999 and 2025"),
# and the repo has had no commits since 2025-11-23. If no release ships before
# the 2026 season, every stats loader will reject 2026 *even once the data is
# published*. The direct path has no such bound, so a wrapper outage becomes a
# no-op instead of a Week 1 blackout.
#
# nflverse release assets are public — no auth, no rate limit, no API key.

import io
import os
import time

import pandas as pd
import requests

RELEASE_BASE = "https://github.com/nflverse/nflverse-data/releases/download"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache", "nflverse")
CACHE_TTL_SECONDS = 6 * 3600  # in-season the upstream refreshes after each slate

# dataset key -> (release_tag, asset_template)
# {season} marks per-season assets; templates without it are single-file datasets.
_ASSETS = {
    "player_stats_week": ("stats_player", "stats_player_week_{season}.parquet"),
    "player_stats_reg":  ("stats_player", "stats_player_reg_{season}.parquet"),
    "snap_counts":       ("snap_counts", "snap_counts_{season}.parquet"),
    "injuries":          ("injuries", "injuries_{season}.parquet"),
    "rosters":           ("rosters", "roster_{season}.parquet"),
    "rosters_weekly":    ("weekly_rosters", "roster_weekly_{season}.parquet"),
    "depth_charts":      ("depth_charts", "depth_charts_{season}.parquet"),
    "pbp":               ("pbp", "play_by_play_{season}.parquet"),
    "schedules":         ("schedules", "games.parquet"),
    "players":           ("players", "players.parquet"),
    "teams":             ("teams", "teams_colors_logos.parquet"),
    "ngs_receiving":     ("nextgen_stats", "ngs_receiving.parquet"),
    "ngs_passing":       ("nextgen_stats", "ngs_passing.parquet"),
    "ngs_rushing":       ("nextgen_stats", "ngs_rushing.parquet"),
}

os.makedirs(CACHE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# direct parquet path
# ---------------------------------------------------------------------------

def _asset_url(dataset: str, season: int | None) -> str:
    tag, template = _ASSETS[dataset]
    return f"{RELEASE_BASE}/{tag}/{template.format(season=season)}"


def _read_parquet_url(url: str) -> pd.DataFrame:
    """Fetch via requests, not pandas' urllib path.

    pandas reads remote parquet through urllib, which uses the system cert
    store and fails with CERTIFICATE_VERIFY_FAILED in some environments.
    requests uses certifi, so it works where the urllib path doesn't.
    """
    cache_path = os.path.join(CACHE_DIR, url.rsplit("/", 1)[-1])
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < CACHE_TTL_SECONDS:
            print(f"   💾 cache hit ({int(age)}s): {os.path.basename(cache_path)}")
            return pd.read_parquet(cache_path)

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    # Write atomically so an interrupted download can't leave a truncated file
    # that later reads as a corrupt parquet.
    tmp_path = f"{cache_path}.tmp"
    try:
        with open(tmp_path, "wb") as f:
            f.write(resp.content)
        os.replace(tmp_path, cache_path)
    except Exception as e:
        print(f"   ⚠️  could not cache {os.path.basename(cache_path)}: {e}")
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    return pd.read_parquet(io.BytesIO(resp.content))


def _load_direct(dataset: str, seasons) -> pd.DataFrame:
    """Read one or more seasons straight from the release assets."""
    tag, template = _ASSETS[dataset]
    if "{season}" not in template:
        return _read_parquet_url(_asset_url(dataset, None))

    frames = []
    for season in _as_list(seasons):
        try:
            frames.append(_read_parquet_url(_asset_url(dataset, season)))
        except Exception as e:
            # A 404 here is expected and benign pre-season: the asset for the
            # upcoming year simply doesn't exist yet. Skip rather than abort so
            # one missing year can't take down the whole run.
            print(f"   ⚠️  {dataset} {season} unavailable ({type(e).__name__}) — skipping")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _as_list(seasons) -> list[int]:
    if seasons is None:
        return [current_season()]
    if isinstance(seasons, int):
        return [seasons]
    return list(seasons)


# ---------------------------------------------------------------------------
# nflreadpy path, with fallback
# ---------------------------------------------------------------------------

_nflreadpy = None
_nflreadpy_checked = False


def _get_nflreadpy():
    """Import nflreadpy lazily and switch it to a filesystem cache.

    Default cache_mode is "memory", which is useless for a cron-driven engine:
    every scheduled run is a fresh process, so nothing is ever reused.
    """
    global _nflreadpy, _nflreadpy_checked
    if _nflreadpy_checked:
        return _nflreadpy
    _nflreadpy_checked = True
    try:
        import nflreadpy
        from nflreadpy.config import update_config

        update_config(cache_mode="filesystem", verbose=False)
        _nflreadpy = nflreadpy
    except Exception as e:
        print(f"⚠️  nflreadpy unavailable ({e}) — using direct parquet only")
        _nflreadpy = None
    return _nflreadpy


def _load(dataset: str, seasons=None, fn_name: str | None = None, **kwargs) -> pd.DataFrame:
    """Try nflreadpy, fall back to direct parquet on any failure."""
    nfl = _get_nflreadpy()
    if nfl is not None and fn_name:
        fn = getattr(nfl, fn_name, None)
        if fn is not None:
            try:
                result = fn(seasons=seasons, **kwargs) if seasons is not None else fn(**kwargs)
                # Loaders return Polars; the rest of the engine and
                # gspread_dataframe both speak pandas.
                return result.to_pandas() if hasattr(result, "to_pandas") else result
            except Exception as e:
                print(f"   ↪ nflreadpy.{fn_name} failed ({type(e).__name__}: {e}) — direct parquet")
    return _load_direct(dataset, seasons)


# ---------------------------------------------------------------------------
# public loaders
# ---------------------------------------------------------------------------

def current_season() -> int:
    """Season whose *stats* are current. Distinct from the roster year."""
    nfl = _get_nflreadpy()
    if nfl is not None:
        try:
            return int(nfl.get_current_season())
        except Exception:
            pass
    # Fallback: NFL seasons are labelled by their September start, so
    # Jan-Aug belongs to the previous season's label.
    from datetime import datetime
    now = datetime.now()
    return now.year if now.month >= 9 else now.year - 1


def load_schedules(seasons=None) -> pd.DataFrame:
    """Full game list. Includes spread_line and total_line — baseline market
    numbers without spending an Odds API credit."""
    df = _load("schedules", seasons=seasons, fn_name="load_schedules")
    if seasons is not None and not df.empty and "season" in df.columns:
        df = df[df["season"].isin(_as_list(seasons))]
    return df.reset_index(drop=True)


def load_player_stats(seasons=None, summary_level="week") -> pd.DataFrame:
    """Weekly or season-aggregated player stats.

    Already carries target_share, air_yards_share, wopr, racr, pacr — no need
    to derive share metrics from play-by-play.
    """
    key = "player_stats_week" if summary_level == "week" else "player_stats_reg"
    return _load(key, seasons=seasons, fn_name="load_player_stats",
                 summary_level=summary_level)


def load_snap_counts(seasons=None) -> pd.DataFrame:
    """Snap counts (offense_pct is the usable snap share).

    Warning: keyed on pfr_player_id, with no gsis_id. Join through
    attach_gsis_id() before merging with player stats.
    """
    return _load("snap_counts", seasons=seasons, fn_name="load_snap_counts")


def load_injuries(seasons=None) -> pd.DataFrame:
    """Injury reports, joinable on gsis_id. Status values are sanitized."""
    df = _load("injuries", seasons=seasons, fn_name="load_injuries")
    # Upstream practice_status contains a literal whitespace value ('\n    ')
    # that would otherwise show up as its own category in any grouping.
    for col in ("report_status", "practice_status"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().replace({"": pd.NA})
    return df


def load_rosters(seasons=None) -> pd.DataFrame:
    return _load("rosters", seasons=seasons, fn_name="load_rosters")


def load_players() -> pd.DataFrame:
    """The ID crosswalk: gsis_id, pfr_id, espn_id, esb_id, and friends."""
    return _load("players", fn_name="load_players")


def load_teams() -> pd.DataFrame:
    """Team metadata. ~36 rows, not 32 — includes relocated franchises
    (OAK, SD, STL, LA), so don't assume a 32-row join."""
    return _load("teams", fn_name="load_teams")


def load_pbp(seasons=None) -> pd.DataFrame:
    """Play-by-play. ~20 MB per season — only load when a metric genuinely
    needs play-level detail (e.g. red zone splits)."""
    return _load("pbp", seasons=seasons, fn_name="load_pbp")


def load_ngs(seasons=None, stat_type="receiving") -> pd.DataFrame:
    """Next Gen Stats. Single file per stat_type covering all seasons;
    keyed on player_gsis_id, and team is team_abbr rather than team."""
    df = _load(f"ngs_{stat_type}", fn_name="load_nextgen_stats",
               stat_type=stat_type)
    if seasons is not None and not df.empty and "season" in df.columns:
        df = df[df["season"].isin(_as_list(seasons))]
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# joins
# ---------------------------------------------------------------------------

def attach_gsis_id(snaps: pd.DataFrame, players: pd.DataFrame | None = None,
                   warn_threshold: float = 0.95) -> pd.DataFrame:
    """Add gsis_id to snap counts by routing pfr_player_id through load_players().

    Snap counts are the only projection input keyed solely on pfr_player_id.
    Without this join, players silently vanish from the model rather than
    erroring — so match coverage is reported explicitly.
    """
    if snaps.empty or "pfr_player_id" not in snaps.columns:
        return snaps

    if players is None:
        players = load_players()
    if players.empty or not {"pfr_id", "gsis_id"} <= set(players.columns):
        print("   ⚠️  crosswalk unavailable — snap counts left without gsis_id")
        return snaps

    crosswalk = (players[["pfr_id", "gsis_id"]]
                 .dropna(subset=["pfr_id"])
                 .drop_duplicates(subset=["pfr_id"]))

    out = snaps.merge(crosswalk, how="left",
                      left_on="pfr_player_id", right_on="pfr_id")
    out = out.drop(columns=["pfr_id"])

    matched = out["gsis_id"].notna().mean()
    if matched < warn_threshold:
        unmatched = out.loc[out["gsis_id"].isna(), "player"].nunique()
        print(f"   ⚠️  snap-count crosswalk matched only {matched:.1%} "
              f"({unmatched} players unmatched)")
    else:
        print(f"   ✅ snap-count crosswalk matched {matched:.1%}")
    return out


def dataset_last_updated(dataset: str) -> str | None:
    """Read a release's timestamp.json (~40 bytes) to check upstream freshness.

    Useful in-season: the nflverse update crons are manually re-enabled each
    September, so data can be stale even when every request succeeds.
    """
    tag, _ = _ASSETS.get(dataset, (None, None))
    if tag is None:
        return None
    try:
        resp = requests.get(f"{RELEASE_BASE}/{tag}/timestamp.json", timeout=15)
        resp.raise_for_status()
        return resp.text.strip().strip('"')
    except Exception:
        return None
