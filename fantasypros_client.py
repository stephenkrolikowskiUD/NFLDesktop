"""Small adapter for the optional FantasyPros public API.

The nflverse FantasyPros snapshot remains the no-key fallback.  This client
only provides a fresher consensus ranking when the owner supplies a personal
API key; it never makes the engine depend on a paid data source.
"""

import os

import pandas as pd
import requests


# Free personal API keys use the documented public API namespace. Production
# access is a separate FantasyPros entitlement and returns 403 for these keys.
BASE_URL = "https://api.fantasypros.com/public/v2/json"


def fantasypros_scoring(scoring: str) -> str:
    """Map the dashboard scoring labels to FantasyPros API scoring values."""
    return {
        "ppr": "PPR",
        "half": "HALF",
        "underdog": "HALF",
        "standard": "STD",
    }.get(str(scoring).lower(), "HALF")


def load_nfl_consensus(season: int, scoring: str, api_key: str | None = None) -> pd.DataFrame:
    """Return current FantasyPros consensus rankings in the nflverse ECR shape.

    The API ranks redraft formats, not best ball specifically.  Callers must
    preserve that source label in the published projection rows so the draft
    board never presents it as an interchangeable best-ball ranking.
    """
    # FP_PRO_API_KEY is the repository secret. Keep the older name as a
    # local-development fallback so existing local setups do not break.
    key = (api_key or os.getenv("FP_PRO_API_KEY", "")
           or os.getenv("FANTASYPROS_API_KEY", "")).strip()
    if not key:
        return pd.DataFrame()

    url = f"{BASE_URL}/nfl/{int(season)}/consensus-rankings"
    try:
        response = requests.get(
            url,
            params={"position": "ALL", "scoring": fantasypros_scoring(scoring)},
            headers={"x-api-key": key},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        body = ""
        if exc.response is not None:
            try:
                body = str(exc.response.json().get("message") or exc.response.text or "").strip()
            except ValueError:
                body = str(exc.response.text or "").strip()
        body = " ".join(body.split())[:180]
        hint = {
            401: "key rejected — confirm the full API key, not the request/activation code",
            403: "key is not authorized for this FantasyPros API endpoint",
            404: "endpoint or requested season was not found",
            429: "rate limit reached — wait before retrying",
            400: "request rejected — inspect the API response detail below",
        }.get(status, "request failed")
        detail = f" ({body})" if body else ""
        print(f"   ⚠️  FantasyPros API consensus unavailable (HTTP {status}: {hint}){detail} — using nflverse snapshot")
        return pd.DataFrame()
    except (requests.RequestException, ValueError) as exc:
        print(f"   ⚠️  FantasyPros API consensus unavailable ({type(exc).__name__}) — using nflverse snapshot")
        return pd.DataFrame()

    players = payload.get("players", []) if isinstance(payload, dict) else []
    if not players:
        print("   ⚠️  FantasyPros API returned no consensus players — using nflverse snapshot")
        return pd.DataFrame()

    rows = []
    for player in players:
        rank = pd.to_numeric(player.get("rank_ecr"), errors="coerce")
        if pd.isna(rank):
            continue
        name = str(player.get("player_name") or "").strip()
        if not name:
            continue
        rows.append({
            "id": player.get("player_id"),
            "player": name,
            "mergename": name,
            "pos": player.get("player_position_id"),
            "ecr": rank,
            "sd": pd.to_numeric(player.get("rank_std"), errors="coerce"),
            "best": pd.to_numeric(player.get("rank_min"), errors="coerce"),
            "worst": pd.to_numeric(player.get("rank_max"), errors="coerce"),
            "bye": player.get("player_bye_week"),
            "ecr_adp": pd.to_numeric(player.get("rank_adp"), errors="coerce"),
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result.attrs["source"] = "FantasyPros API consensus"
        result.attrs["updated"] = str(payload.get("last_updated") or "")
        result.attrs["format"] = f"{fantasypros_scoring(scoring)} redraft"
    return result
