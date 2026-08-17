# 🎲 The Odds API client — NFL featured markets + player props
#
# Cost model (verified against the-odds-api.com docs):
#   /v4/sports/{sport}/events            → FREE, 0 credits
#   /v4/sports/{sport}/odds              → markets × regions
#   /v4/sports/{sport}/events/{id}/odds  → markets × regions, PER EVENT
#
# Two details that shape this whole module:
#
#  1. Cost counts markets *returned*, not requested, and empty responses are
#     free. So over-requesting markets on a game whose books haven't opened yet
#     costs nothing. That's why we request a generous market list rather than
#     probing first.
#
#  2. `bookmakers=` replaces `regions=` for costing — every 10 books counts as
#     1 region. Passing regions=us instead would BOTH cost the same AND silently
#     drop espnbet, which lives in region us2. So we always pass books, never
#     regions.

import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import requests

BASE = "https://api.the-odds-api.com/v4"
DEFAULT_SPORT = "americanfootball_nfl"

# Verified bookmaker keys. Note williamhill_us IS Caesars — a `caesars` key
# does not exist and returns INVALID_BOOKMAKERS. espnbet is region us2, which
# is precisely why this is a books list and not a regions param.
US_BOOKS = ["draftkings", "fanduel", "betmgm", "espnbet", "williamhill_us"]

# Market keys verified verbatim from the docs. Spelling traps: always `yds`
# never `yards`; and the "longest" markets are inconsistently ordered
# (player_pass_longest_completion vs player_rush_longest).
MARKET_BATCHES = [
    # passing
    ["player_pass_yds", "player_pass_tds", "player_pass_completions",
     "player_pass_attempts", "player_pass_interceptions"],
    # rushing + receiving — the core DFS surface
    ["player_rush_yds", "player_rush_attempts", "player_receptions",
     "player_reception_yds"],
    # touchdowns + kicking
    ["player_anytime_td", "player_rush_tds", "player_reception_tds",
     "player_kicking_points"],
]

# Short labels for display and for joining to projections.
MARKET_LABELS = {
    "player_pass_yds": "PASS_YDS",
    "player_pass_tds": "PASS_TDS",
    "player_pass_completions": "COMP",
    "player_pass_attempts": "ATT",
    "player_pass_interceptions": "INT",
    "player_rush_yds": "RUSH_YDS",
    "player_rush_attempts": "CARRIES",
    "player_rush_tds": "RUSH_TDS",
    "player_receptions": "REC",
    "player_reception_yds": "REC_YDS",
    "player_reception_tds": "REC_TDS",
    "player_anytime_td": "ANY_TD",
    "player_kicking_points": "KICK_PTS",
}

# Yes/No markets carry no `point`. Treat them as an implicit 0.5 line so they
# share a schema with over/under markets.
BINARY_MARKETS = {"player_anytime_td": 0.5, "player_1st_td": 0.5, "player_last_td": 0.5}


class QuotaExhausted(RuntimeError):
    pass


class OddsClient:
    def __init__(self, api_key: str, quota_floor: int = 100, *,
                 sport: str = DEFAULT_SPORT):
        self.api_key = api_key
        self.quota_floor = quota_floor
        self.sport = sport
        self.remaining: int | None = None
        self.spent = 0

    # -- plumbing ----------------------------------------------------------

    def _get(self, path: str, params: dict, context: str, free: bool = False):
        params = {"apiKey": self.api_key, **params}
        for attempt in range(3):
            resp = requests.get(f"{BASE}{path}", params=params, timeout=25)

            # 429 can fire slightly under the documented 30 req/s because of
            # network jitter, so a short backoff is expected, not exceptional.
            if resp.status_code == 429:
                wait = 2 * (attempt + 1)
                print(f"   ⏳ 429 on {context} — retrying in {wait}s")
                time.sleep(wait)
                continue

            self._track(resp, free)
            return resp
        print(f"   ⚠️  {context}: gave up after repeated 429s")
        return None

    def _track(self, resp, free: bool) -> None:
        """Record quota from response headers.

        x-requests-last is the *actual* charge for the call just made. Trusting
        it rather than predicting cost means silently-unavailable markets show
        up as real savings instead of phantom spend.
        """
        try:
            self.remaining = int(resp.headers["x-requests-remaining"])
        except (KeyError, ValueError, TypeError):
            pass
        try:
            self.spent += int(resp.headers.get("x-requests-last", 0))
        except (ValueError, TypeError):
            pass

        if not free and self.remaining is not None and self.remaining < self.quota_floor:
            raise QuotaExhausted(
                f"🛑 QUOTA GUARD: {self.remaining} credits remaining < floor "
                f"{self.quota_floor}. Aborting before spending more."
            )

    # -- endpoints ---------------------------------------------------------

    def fetch_events(self, within_days: int | None = None) -> list[dict]:
        """List upcoming events. Free — costs 0 credits.

        Used to decide which events are worth paying for, so props are never
        requested for all 272 games of a season.
        """
        resp = self._get(f"/sports/{self.sport}/events", {}, "events", free=True)
        if resp is None or resp.status_code != 200:
            code = resp.status_code if resp is not None else "no response"
            print(f"   ⚠️  events fetch failed ({code})")
            return []
        events = resp.json()

        if within_days is not None:
            cutoff = datetime.now(timezone.utc) + timedelta(days=within_days)
            events = [
                e for e in events
                if _parse_iso(e.get("commence_time")) is not None
                and _parse_iso(e["commence_time"]) <= cutoff
            ]
        return events

    def fetch_featured(self, markets: str = "h2h,spreads,totals") -> list[dict]:
        """Featured markets for every upcoming game in one call."""
        resp = self._get(
            f"/sports/{self.sport}/odds",
            {"markets": markets, "bookmakers": ",".join(US_BOOKS),
             "oddsFormat": "american"},
            "featured odds",
        )
        if resp is None or resp.status_code != 200:
            code = resp.status_code if resp is not None else "no response"
            print(f"   ⚠️  featured odds failed ({code})")
            return []
        return resp.json()

    def fetch_props(self, events: list[dict],
                    batches: list[list[str]] | None = None) -> pd.DataFrame:
        """Player props, one request per event per market batch.

        There is no bulk props endpoint — the API explicitly serves one event at
        a time. Empty responses are free, so this is cheap before books open.
        """
        batches = batches or MARKET_BATCHES
        rows, errors = [], 0

        for event in events:
            eid = event.get("id")
            if not eid:
                continue
            for batch in batches:
                resp = self._get(
                    f"/sports/{self.sport}/events/{eid}/odds",
                    {"markets": ",".join(batch),
                     "bookmakers": ",".join(US_BOOKS),
                     "oddsFormat": "american"},
                    f"props {eid}",
                )
                if resp is None:
                    continue
                if resp.status_code == 422:
                    # A misspelled key aborts the whole request, and the message
                    # names the offender — surface it rather than silently
                    # returning fewer props than expected.
                    print(f"   ⚠️  422 invalid market in batch {batch}: {resp.text[:160]}")
                    continue
                if resp.status_code != 200:
                    errors += 1
                    if errors <= 3:
                        print(f"   ⚠️  props {resp.status_code} for {eid}: {resp.text[:120]}")
                    if errors > 10:
                        print("   ⚠️  too many prop errors — stopping props pull")
                        return _finalize(rows)
                    continue
                rows.extend(parse_props_payload(resp.json()))

        return _finalize(rows)


# ---------------------------------------------------------------------------
# parsing
# ---------------------------------------------------------------------------

def parse_props_payload(payload: dict) -> list[dict]:
    """Flatten one per-event props response into long-format rows.

    Shape differs from the featured /odds endpoint in one way that matters:
    last_update lives on the *market*, not the bookmaker. Don't reuse a
    featured-market parser here.
    """
    home = payload.get("home_team", "")
    away = payload.get("away_team", "")
    commence = payload.get("commence_time", "")
    rows = []

    for book in payload.get("bookmakers", []):
        book_key = book.get("key", "")
        for market in book.get("markets", []):
            mkey = market.get("key", "")
            last_update = market.get("last_update", "")
            for oc in market.get("outcomes", []):
                player = oc.get("description") or ""
                side = str(oc.get("name", "")).strip()
                price = oc.get("price")
                point = oc.get("point")

                if not player or price is None:
                    continue
                if point is None:
                    point = BINARY_MARKETS.get(mkey)
                if point is None:
                    continue

                rows.append({
                    "event_home": home,
                    "event_away": away,
                    "commence_time": commence,
                    "book": book_key,
                    "market": mkey,
                    "metric": MARKET_LABELS.get(mkey, mkey),
                    "player": player,
                    "line": float(point),
                    "side": side,
                    "price": price,
                    "last_update": last_update,
                })
    return rows


def _finalize(rows: list[dict]) -> pd.DataFrame:
    """Pivot Over/Under (or Yes/No) onto one row per player-market-line-book."""
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Yes/No naming isn't documented with a sample payload, so accept both
    # conventions rather than assuming one and silently dropping the other.
    over_side = df["side"].isin(["Over", "Yes"])
    under_side = df["side"].isin(["Under", "No"])

    keys = ["event_home", "event_away", "commence_time", "book", "market",
            "metric", "player", "line", "last_update"]

    over = (df[over_side].rename(columns={"price": "over_odds"})
            .drop(columns=["side"]).drop_duplicates(subset=keys))
    under = (df[under_side].rename(columns={"price": "under_odds"})
             .drop(columns=["side"]).drop_duplicates(subset=keys))

    merged = over.merge(under, how="outer", on=keys)

    unknown = df.loc[~over_side & ~under_side, "side"].unique()
    if len(unknown):
        print(f"   ⚠️  unrecognized outcome side(s), dropped: {list(unknown)[:5]}")

    return merged.reset_index(drop=True)


# ---------------------------------------------------------------------------
# pricing
# ---------------------------------------------------------------------------

def american_to_implied(odds) -> float:
    try:
        odds = float(odds)
    except (TypeError, ValueError):
        return np.nan
    if odds == 0 or pd.isna(odds):
        return np.nan
    return (-odds / (-odds + 100)) if odds < 0 else (100 / (odds + 100))


def implied_to_american(prob) -> int | None:
    try:
        prob = float(prob)
    except (TypeError, ValueError):
        return None
    if not 0 < prob < 1:
        return None
    return (int(round(-100 * prob / (1 - prob))) if prob >= 0.5
            else int(round(100 * (1 - prob) / prob)))


def add_fair_prices(props: pd.DataFrame) -> pd.DataFrame:
    """Add no-vig fair probabilities per book quote.

    Removing the book's hold is what makes prices comparable across books, and
    is the baseline any projection edge gets measured against.
    """
    if props.empty:
        return props
    out = props.copy()
    over_p = out["over_odds"].map(american_to_implied)
    under_p = out["under_odds"].map(american_to_implied)
    total = over_p + under_p

    out["hold"] = (total - 1).round(4)
    out["fair_over_prob"] = (over_p / total).round(4)
    out["fair_under_prob"] = (under_p / total).round(4)
    return out


def best_price_board(props: pd.DataFrame) -> pd.DataFrame:
    """Collapse to the best available price per player-metric-line.

    Books post different lines for the same player, so (player, metric, line)
    is the join key — never (player, metric) alone.
    """
    if props.empty:
        return pd.DataFrame()

    keys = ["player", "metric", "line", "event_away", "event_home", "commence_time"]
    out = []

    for key_vals, group in props.groupby(keys, dropna=False):
        record = dict(zip(keys, key_vals))

        for side in ("over", "under"):
            col = f"{side}_odds"
            valid = group[group[col].notna()]
            if valid.empty:
                record[f"best_{side}_odds"] = None
                record[f"best_{side}_book"] = None
                record[f"best_{side}_last_update"] = None
                continue
            # Highest American number is the best price for the bettor, whether
            # the range is positive or negative (+150 > +120, -105 > -120).
            best = valid.loc[valid[col].idxmax()]
            record[f"best_{side}_odds"] = best[col]
            record[f"best_{side}_book"] = best["book"]
            record[f"best_{side}_last_update"] = best.get("last_update")

        record["books_quoting"] = group["book"].nunique()
        out.append(record)

    board = pd.DataFrame(out)
    if not board.empty:
        board = board.sort_values(["commence_time", "player", "metric"])
    return board.reset_index(drop=True)


def _parse_iso(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
