# 🎯 Weekly picks generation (v1)
#
# Ported from MLBDesktop's generate_gemini_picks() (MLBEnginev5-4.py), adapted
# for a weekly rather than nightly sport. The mechanics that made MLB's version
# reliable are kept close to verbatim on purpose:
#   - 3-pass consensus at different temperatures, merged and deduped
#   - one recovery pass only if the consensus underperforms
#   - a deterministic, Gemini-free fallback built from real market lines that
#     is the actual guarantee of a non-empty board, not the AI
#   - never trust Gemini's stated line — snap every pick to a real market line
#   - confidence tiers are Gemini's own labeled output, only ever DOWNGRADED
#     afterward, never upgraded (an MLB audit finding: cross-run repetition
#     isn't a reliable upgrade signal, so this deliberately doesn't try)
#
# What's genuinely different from MLB, not just renamed:
#   - NFL already has a backtested season model (projections.py). Rather than
#     inventing MLB-style ad-hoc per-stat edge heuristics, the "form" signal fed
#     to Gemini is a single, uniform hit-rate/EV computation against the real
#     market line, usable across every prop type including binary ones.
#   - Anytime-TD and similar binary props need NO separate grading path: they
#     already carry an implicit 0.5 line from odds_client.BINARY_MARKETS, so
#     scoring "did they get a TD" as 1/0 against line=0.5 reuses the exact same
#     over/under/push logic as a numeric prop. Same idea is reused at grading
#     time in NFLGrader1.py.
#   - Picks carry player_id (gsis_id) end to end, not just a name. MLB grades
#     by name alone and has to detect+skip ambiguous name collisions after the
#     fact; NFL's data is gsis_id-keyed throughout the rest of this pipeline, so
#     grading can match on identity directly and only fall back to name
#     matching for legacy/ungraded edge cases.
#   - PICK_BOOK/PICK_ODDS snap to the best price across books (best_price_board
#     already computes this), not a single reference book.

import json
import re
from datetime import datetime

import numpy as np
import pandas as pd
import pytz

from sports_common import normalize_confidence

eastern = pytz.timezone("US/Eastern")

# ============================================================================
# CONFIG — tier thresholds and pick volume carried over from MLB verbatim.
# ============================================================================

GEMINI_TARGET_PICKS = 14
MIN_WEEKLY_PICKS = 9
CONSENSUS_TEMPS = [0.35, 0.55, 0.75]
RECOVERY_TEMP = 0.45
MAX_OUTPUT_TOKENS = 8192

# Confidence tier bars, stated to Gemini in the prompt exactly as MLB states
# them: SMASH needs season hit rate >65%, EV% >10%, and 2+ independent
# confirming signals; STRONG needs >55%/>5%/supportive context; LEAN is
# everything else and should be the most common tier, used liberally.
TIER_RULES_TEXT = (
    "Confidence tiers: SMASH = top 3-4 highest conviction, and must ALSO clear "
    "a higher bar than STRONG on ALL of (a) season hit rate >65% on this prop "
    "type for this player, (b) EV% >10%, (c) 2+ independent confirming signals "
    "(e.g. matchup edge AND recent form — not just one). A pick that would only "
    "qualify for STRONG under these numbers must be labeled STRONG, never "
    "SMASH, even if it is your top-ranked pick. STRONG = next 4-5, requires ALL "
    "of (a) season hit rate >55% on this prop type for this player, (b) EV% "
    ">5%, (c) supportive matchup/split context. LEAN = everything else with 1-2 "
    "positive signals — use it liberally; it should be the most common tier."
)

# Maps the odds_client/PropsBoard metric vocabulary to the actual column in
# Skill_Game_Logs / QB_Game_Logs. ANY_TD has no direct column — it's computed
# from receiving_tds + rushing_tds at both prompt-context time (here) and
# grading time (NFLGrader1.py imports this same map, single source of truth).
# KICK_PTS is deliberately absent: no kicker stats exist anywhere in this
# pipeline yet, so kicking props are out of scope for v1 rather than silently
# ungradeable.
METRIC_TO_LOG_COL = {
    "REC": "receptions",
    "REC_YDS": "receiving_yards",
    "REC_TDS": "receiving_tds",
    "RUSH_YDS": "rushing_yards",
    "CARRIES": "carries",
    "RUSH_TDS": "rushing_tds",
    "PASS_YDS": "passing_yards",
    "PASS_TDS": "passing_tds",
    "COMP": "completions",
    "ATT": "attempts",
    "INT": "passing_interceptions",
}
BINARY_METRICS = {"ANY_TD"}
SUPPORTED_METRICS = set(METRIC_TO_LOG_COL) | BINARY_METRICS


def actual_value_for_metric(log_row: pd.Series, metric: str):
    """The real outcome for one game log row, on the METRIC vocabulary.

    Shared between picks.py (building historical hit-rate context) and
    NFLGrader1.py (reading the completed week's actual result) so the two
    can't silently drift apart on what a metric means.
    """
    if metric in BINARY_METRICS:
        rec_td = pd.to_numeric(log_row.get("receiving_tds"), errors="coerce") or 0
        rush_td = pd.to_numeric(log_row.get("rushing_tds"), errors="coerce") or 0
        return 1.0 if (rec_td + rush_td) > 0 else 0.0
    col = METRIC_TO_LOG_COL.get(metric)
    if col is None:
        return None
    val = pd.to_numeric(log_row.get(col), errors="coerce")
    return None if pd.isna(val) else float(val)


def _norm_name(value) -> str:
    """Shared identity-matching key — used here AND by NFLGrader1.py, which
    imports this function rather than reimplementing it, so the two can't
    silently drift apart on what counts as "the same player."

    Diacritics are stripped via decomposition BEFORE the a-z filter, not
    dropped by it — this matters for real names: filtering "é" straight
    through a plain a-z regex removes the character entirely ("andré" ->
    "andr"), rather than normalizing it to plain "e". Ported from MLB's
    normalize_person_name, which hit this exact case in production.
    """
    import unicodedata
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_gemini_json_array(raw: str):
    """Parse Gemini's JSON output, salvaging a truncated array if needed.

    Ported verbatim from MLB's parse_gemini_json_array — a response cut off by
    max_output_tokens still has a usable prefix; this recovers it instead of
    discarding the whole pass.
    """
    cleaned = str(raw or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        cleaned = cleaned.rsplit("```", 1)[0].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        last_complete = cleaned.rfind("}")
        if last_complete > 0:
            return json.loads(cleaned[: last_complete + 1] + "]")
        raise


# ============================================================================
# CONTEXT BUILDING — the player pool and hit-rate/EV signal fed to the prompt.
# ============================================================================

def _implied_prob(american_odds) -> float:
    try:
        odds = float(american_odds)
    except (TypeError, ValueError):
        return np.nan
    if odds == 0 or pd.isna(odds):
        return np.nan
    return (-odds / (-odds + 100)) if odds < 0 else (100 / (odds + 100))


def _line_matches(pick_line, real_line, tol: float = 1e-9) -> bool:
    """Numeric exact-match with float tolerance for sportsbook half-lines."""
    try:
        pick_num = float(pick_line)
        real_num = float(real_line)
    except (TypeError, ValueError):
        return False
    return abs(pick_num - real_num) <= tol


def build_player_context(props_board: pd.DataFrame, game_logs: pd.DataFrame,
                         projections: pd.DataFrame, injuries: pd.DataFrame,
                         max_players: int = 80) -> pd.DataFrame:
    """One row per real prop line, with a hit-rate/EV signal and model context.

    Mirrors MLB's approach of only presenting players who have a REAL prop
    today — Gemini never gets to invent a market that doesn't exist. Unlike
    MLB's separate per-stat heuristics, one hit-rate/EV formula covers every
    metric here (including binary ones), because actual_value_for_metric()
    already normalizes numeric and binary outcomes to the same scale.
    """
    if props_board.empty or game_logs.empty:
        return pd.DataFrame()

    board = props_board[props_board["metric"].isin(SUPPORTED_METRICS)].copy()
    if board.empty:
        return pd.DataFrame()

    logs = game_logs.copy()
    logs["_name_norm"] = logs["player_display_name"].map(_norm_name)
    board["_name_norm"] = board["player"].map(_norm_name)

    rows = []
    for _, prop in board.iterrows():
        player_logs = logs[logs["_name_norm"] == prop["_name_norm"]]
        if player_logs.empty:
            continue

        actuals = player_logs.apply(
            lambda r: actual_value_for_metric(r, prop["metric"]), axis=1
        ).dropna()
        if len(actuals) < 3:
            # Same floor MLB uses before trusting a hit-rate signal at all.
            continue

        line = pd.to_numeric(prop.get("line"), errors="coerce")
        if pd.isna(line):
            continue

        over_hits = (actuals > line).mean()
        under_hits = (actuals < line).mean()
        over_odds = prop.get("best_over_odds")
        under_odds = prop.get("best_under_odds")
        over_ev = over_hits - _implied_prob(over_odds) if pd.notna(over_odds) else np.nan
        under_ev = under_hits - _implied_prob(under_odds) if pd.notna(under_odds) else np.nan

        latest = player_logs.sort_values("week").iloc[-1]
        proj_row = None
        if not projections.empty and "player_id" in projections.columns:
            match = projections[projections["player_id"].astype(str) == str(latest.get("player_id"))]
            proj_row = match.iloc[0] if not match.empty else None

        inj_row = pd.DataFrame()
        if not injuries.empty and "gsis_id" in injuries.columns:
            inj_row = injuries[injuries["gsis_id"].astype(str) == str(latest.get("player_id"))]

        rows.append({
            "player": prop["player"],
            "player_id": latest.get("player_id"),
            "team": latest.get("team"),
            "opponent": latest.get("opponent_team"),
            "position": latest.get("position"),
            "metric": prop["metric"],
            "line": line,
            "best_over_odds": over_odds,
            "best_over_book": prop.get("best_over_book"),
            "best_under_odds": under_odds,
            "best_under_book": prop.get("best_under_book"),
            "games_sampled": len(actuals),
            "over_hit_rate": round(float(over_hits), 3),
            "under_hit_rate": round(float(under_hits), 3),
            "over_ev_pct": round(float(over_ev) * 100, 1) if pd.notna(over_ev) else np.nan,
            "under_ev_pct": round(float(under_ev) * 100, 1) if pd.notna(under_ev) else np.nan,
            "proj_ppr": proj_row.get("proj_ppr") if proj_row is not None else np.nan,
            "vorp": proj_row.get("vorp") if proj_row is not None else np.nan,
            "model_confidence": proj_row.get("confidence") if proj_row is not None else "",
            "ecr": proj_row.get("ecr") if proj_row is not None else np.nan,
            # report_status can be a real NaN within a matched row (not just a
            # missing row) — str(nan) would otherwise become the literal text
            # "nan" in injury_context downstream, so sanitize at the source.
            "injury_status": (lambda v: "" if pd.isna(v) else v)(
                inj_row.iloc[0].get("report_status") if not inj_row.empty else ""),
        })

    if not rows:
        return pd.DataFrame()

    ctx = pd.DataFrame(rows)
    # Guarantee at least some star coverage the same way MLB does — top 20 by
    # projected points are flagged so the prompt can request a minimum STAR mix
    # instead of only surfacing the biggest raw EV numbers on thin markets.
    star_ids = set(
        ctx.dropna(subset=["proj_ppr"]).sort_values("proj_ppr", ascending=False)
           ["player_id"].head(20)
    )
    ctx["is_star"] = ctx["player_id"].isin(star_ids)

    best_ev = ctx[["over_ev_pct", "under_ev_pct"]].abs().max(axis=1).fillna(0)
    ctx = ctx.assign(_best_ev=best_ev).sort_values("_best_ev", ascending=False)

    guaranteed = ctx[ctx["is_star"]].head(15)
    rest = ctx[~ctx.index.isin(guaranteed.index)]
    pool = pd.concat([guaranteed, rest]).head(max_players)
    return pool.drop(columns=["_best_ev"], errors="ignore").reset_index(drop=True)


# ============================================================================
# PROMPT
# ============================================================================

def build_prompt(week: int, season: int, games_str: str, player_ctx: str,
                 allowed_metrics: list[str]) -> str:
    allowed = ", ".join(allowed_metrics)
    return f"""You are an expert NFL props analyst. This is Week {week} of the {season} NFL season.

THIS WEEK'S GAMES:
{games_str}

PLAYER DATA (with season hit-rate/EV signals against REAL sportsbook lines, and season-long model context):
{player_ctx}

RULES:
- CRITICAL: ONLY pick players from the PLAYER DATA list above, and every pick must match one of that player's listed REAL props exactly (same prop type and line). Do NOT invent lines. NEVER return null for line.
- Return EXACTLY {GEMINI_TARGET_PICKS + 6} ranked candidate picks. These are draft candidates for the engine to validate, not final bets — breadth matters more than certainty. If you're unsure whether a pick clears STRONG, mark it LEAN and include it rather than leaving it out. Do not stop early because you've run out of high-confidence picks.
- Allowed prop types for this slate: {allowed}.
- {TIER_RULES_TEXT}
- STAR players are the top 20 by projected season points in this week's valid prop pool (flagged is_star=true). Prefer at least 4 of your {GEMINI_TARGET_PICKS} final picks from STARs; non-stars fill remaining slots only with exceptional edges.
- The model_confidence field (from a backtested season-long projection model) and vorp/ecr context are informative but not decisive on their own — weigh them alongside the hit-rate/EV signal and matchup, the same way you'd weigh any other input.
- Treat injury_status other than blank/"" as a real signal: "Questionable" or worse should generally cap confidence at STRONG; do not use SMASH on a player with any non-blank injury_status unless the signal is overwhelming.
ANALYSIS FACTORS:
- Season hit rate and EV% against the real line, recent usage trend, target share / snap share where relevant, opponent context, and injury status.
- Prefer props where the model's own projection context (vorp, model_confidence) agrees with the market signal over ones where they conflict, but don't discard a strong market signal just because the model disagrees — note the disagreement in the rationale instead.
For each pick provide:
- rank (1-{GEMINI_TARGET_PICKS + 6})
- player (exact name from data)
- team (abbreviation)
- game (e.g. "NE @ SEA")
- opponent (abbreviation)
- prop_type (real prop metric, e.g. REC_YDS)
- line (real sportsbook line)
- lean (OVER or UNDER)
- confidence (SMASH, STRONG, or LEAN)
- rationale (1 sentence, under 15 words)
- injury_context (under 10 words)
OUTPUT FORMAT — Return ONLY a valid JSON array. No markdown, no backticks, no explanation:
[{{"rank":1,"player":"Ja'Marr Chase","team":"CIN","game":"CIN @ CLE","opponent":"CLE","prop_type":"REC_YDS","line":78.5,"lean":"OVER","confidence":"STRONG","rationale":"High target share, favorable secondary matchup.","injury_context":""}}]"""


def build_recovery_prompt(base_prompt: str, projected_survivors: int) -> str:
    return base_prompt + f"""

RECOVERY REQUIREMENT:
The previous responses yielded only {projected_survivors} candidates that survived validation.
Return at least {MIN_WEEKLY_PICKS} distinct picks that satisfy the allowed markets.
Use only exact real props listed in PLAYER DATA. Include LEAN picks when the evidence is merely adequate.
Do not explain anything outside the JSON array.
"""


# ============================================================================
# CONSENSUS MERGE — ported from MLB's build_consensus_pick_pool, unchanged.
# ============================================================================

def build_consensus_pick_pool(pick_lists: list[list[dict]]) -> list[dict]:
    grouped = {}
    for run_idx, picks in enumerate(pick_lists, start=1):
        for pick in picks or []:
            player_key = _norm_name(pick.get("player", ""))
            prop_key = str(pick.get("prop_type", "")).strip().upper()
            lean_key = str(pick.get("lean", "") or "").strip().upper()
            if not player_key or not prop_key or not lean_key:
                continue
            key = (player_key, prop_key, lean_key)
            entry = grouped.setdefault(
                key, {"pick": dict(pick), "count": 0, "runs": [], "best_rank": 999}
            )
            if run_idx not in entry["runs"]:
                entry["runs"].append(run_idx)
                entry["count"] += 1
            try:
                rank_val = int(float(pick.get("rank", 999)))
            except (TypeError, ValueError):
                rank_val = 999
            if rank_val < entry["best_rank"]:
                entry["pick"] = dict(pick)
                entry["best_rank"] = rank_val

    merged = []
    for entry in grouped.values():
        pick = dict(entry["pick"])
        pick["CONSENSUS_COUNT"] = entry["count"]
        pick["CONSENSUS_RUNS"] = ",".join(str(r) for r in entry["runs"])
        pick["CONSENSUS_TAG"] = (
            f"CONSENSUS {entry['count']}/{len(pick_lists)}" if entry["count"] >= 2 else ""
        )
        pick["SELECTION_METHOD"] = "GEMINI"
        # MLB's audit finding: cross-run repetition doesn't reliably justify an
        # upgrade, so this normalizes rather than promotes on consensus count.
        pick["confidence"] = normalize_confidence(pick.get("confidence"))
        merged.append(pick)
    merged.sort(key=lambda pk: (-int(pk.get("CONSENSUS_COUNT", 1)), float(pk.get("rank", 999) or 999)))
    return merged


# ============================================================================
# VALIDATION — snap every pick to a real market line; never trust Gemini's.
# ============================================================================

def validate_and_price_picks(raw_picks: list[dict], player_ctx: pd.DataFrame) -> pd.DataFrame:
    """Drop anything not backed by a real line; attach player_id and pricing.

    This is the step that makes "never invent a line" actually enforced rather
    than just requested in the prompt. A pick surviving this function is
    guaranteed to correspond to a real row in player_ctx.
    """
    if not raw_picks or player_ctx.empty:
        return pd.DataFrame()

    ctx = player_ctx.copy()
    ctx["_name_norm"] = ctx["player"].map(_norm_name)
    ctx["_metric_norm"] = ctx["metric"].astype(str).str.upper()

    rows = []
    for pick in raw_picks:
        name_norm = _norm_name(pick.get("player", ""))
        metric = str(pick.get("prop_type", "")).strip().upper()
        lean = str(pick.get("lean", "")).strip().upper()
        pick_team = str(pick.get("team", "") or "").strip().upper()
        pick_line = pd.to_numeric(pick.get("line"), errors="coerce")
        if lean not in {"OVER", "UNDER"}:
            continue
        if pd.isna(pick_line):
            continue

        match = ctx[(ctx["_name_norm"] == name_norm) & (ctx["_metric_norm"] == metric)]
        if match.empty:
            continue
        match = match[match["line"].map(lambda line: _line_matches(pick_line, line))]
        if match.empty:
            continue
        if pick_team and "team" in match.columns:
            team_match = match[match["team"].astype(str).str.upper() == pick_team]
            if not team_match.empty:
                match = team_match
        real = match.iloc[0]

        odds_col = "best_over_odds" if lean == "OVER" else "best_under_odds"
        book_col = "best_over_book" if lean == "OVER" else "best_under_book"
        ev_col = "over_ev_pct" if lean == "OVER" else "under_ev_pct"
        hit_col = "over_hit_rate" if lean == "OVER" else "under_hit_rate"
        pick_odds = real.get(odds_col)
        if pd.isna(pick_odds):
            continue

        rows.append({
            "rank": pick.get("rank", 999),
            "player": real["player"],
            "player_id": real.get("player_id"),
            "team": real.get("team"),
            "opponent": real.get("opponent"),
            "game": pick.get("game", ""),
            "prop_type": metric,
            "line": real["line"],  # exact real line match, never Gemini's
            "lean": lean,
            "confidence": normalize_confidence(pick.get("confidence")),
            "rationale": str(pick.get("rationale", ""))[:200],
            "injury_context": str(pick.get("injury_context", real.get("injury_status", "")))[:120],
            "PICK_BOOK": real.get(book_col),
            "PICK_ODDS": pick_odds,
            "IMPLIED_PROBABILITY": round(_implied_prob(pick_odds), 4) if pd.notna(pick_odds) else np.nan,
            "MODEL_HIT_RATE": real.get(hit_col),
            "MODEL_EV_PCT": real.get(ev_col),
            "MODEL_EDGE_SCORE": real.get(ev_col),
            "CONSENSUS_COUNT": pick.get("CONSENSUS_COUNT", 1),
            "CONSENSUS_RUNS": pick.get("CONSENSUS_RUNS", ""),
            "CONSENSUS_TAG": pick.get("CONSENSUS_TAG", ""),
            "SELECTION_METHOD": pick.get("SELECTION_METHOD", "GEMINI"),
        })

    return pd.DataFrame(rows)


def apply_smash_cap(df: pd.DataFrame) -> pd.DataFrame:
    """At most a handful of SMASH per run — same formula as MLB, verbatim."""
    if df.empty:
        return df
    out = df.copy()
    smash_idx = out.index[out["confidence"] == "SMASH"].tolist()
    max_smash = min(3, max(1, len(out) // 4 + (1 if len(out) >= 8 else 0)))
    for idx in smash_idx[max_smash:]:
        out.at[idx, "confidence"] = "STRONG"
    return out


# ============================================================================
# DETERMINISTIC FALLBACK — the real guarantee, no Gemini involved.
# ============================================================================

def build_deterministic_fallback(player_ctx: pd.DataFrame, exclude_keys: set,
                                 need: int) -> pd.DataFrame:
    """Fill the weekly board from real market edges alone when Gemini
    underdelivers. Tagged VALIDATED_MODEL to match the SELECTION_METHOD value
    app.js's calibratedConfidenceForPick() already special-cases as the
    'VALIDATED' confidence tier — no dashboard change needed for this to work.
    """
    if player_ctx.empty or need <= 0:
        return pd.DataFrame()

    ctx = player_ctx.copy()
    candidates = []
    for lean, ev_col, hit_col, odds_col, book_col in [
        ("OVER", "over_ev_pct", "over_hit_rate", "best_over_odds", "best_over_book"),
        ("UNDER", "under_ev_pct", "under_hit_rate", "best_under_odds", "best_under_book"),
    ]:
        rows = ctx[ctx[ev_col].notna() & (ctx[ev_col] > 3)].copy()
        rows["_lean"] = lean
        rows["_ev"] = rows[ev_col]
        rows["_hit"] = rows[hit_col]
        rows["_odds"] = rows[odds_col]
        rows["_book"] = rows[book_col]
        candidates.append(rows)

    if not candidates:
        return pd.DataFrame()
    pool = pd.concat(candidates, ignore_index=True).sort_values("_ev", ascending=False)

    rows = []
    for _, r in pool.iterrows():
        key = (_norm_name(r["player"]), r["metric"], r["_lean"])
        if key in exclude_keys:
            continue
        exclude_keys.add(key)
        rows.append({
            "rank": len(rows) + 1,
            "player": r["player"],
            "player_id": r.get("player_id"),
            "team": r.get("team"),
            "opponent": r.get("opponent"),
            "game": "",
            "prop_type": r["metric"],
            "line": r["line"],
            "lean": r["_lean"],
            # >8% EV maps to STRONG-equivalent evidence, matching MLB's fallback
            # convention of never labeling deterministic picks SMASH.
            "confidence": "STRONG" if r["_ev"] > 8 else "LEAN",
            "rationale": f"{r['_hit']:.0%} season hit rate vs. line, {r['_ev']:+.1f}% EV.",
            "injury_context": str(r.get("injury_status", ""))[:120],
            "PICK_BOOK": r.get("_book"),
            "PICK_ODDS": r.get("_odds"),
            "IMPLIED_PROBABILITY": round(_implied_prob(r.get("_odds")), 4) if pd.notna(r.get("_odds")) else np.nan,
            "MODEL_HIT_RATE": r["_hit"],
            "MODEL_EV_PCT": r["_ev"],
            "MODEL_EDGE_SCORE": r["_ev"],
            "CONSENSUS_COUNT": 1,
            "CONSENSUS_RUNS": "",
            "CONSENSUS_TAG": "VALIDATED FALLBACK",
            "SELECTION_METHOD": "VALIDATED_MODEL",
        })
        if len(rows) >= need:
            break

    return pd.DataFrame(rows)


# ============================================================================
# GEMINI CALLS
# ============================================================================

def call_gemini(client, model: str, prompt: str, temperature: float) -> list[dict] | None:
    """One Gemini call. Failures are logged and the pass is dropped — same
    no-retry-with-backoff behavior as MLB, which relies on the 3-pass
    consensus plus the deterministic fallback rather than retrying a flaky call.
    """
    from google.genai import types
    try:
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            response_mime_type="application/json",
        )
        raw = client.models.generate_content(model=model, contents=prompt, config=config).text.strip()
        picks = parse_gemini_json_array(raw)
        print(f"   ↳ {len(picks)} picks returned")
        return picks
    except json.JSONDecodeError:
        print("   ⚠️  malformed JSON — ignoring that pass")
        return None
    except Exception as e:
        print(f"   ⚠️  Gemini call failed: {type(e).__name__}: {str(e)[:180]}")
        return None


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def generate_weekly_picks(gemini_api_key: str, gemini_model: str,
                          player_ctx: pd.DataFrame, games_str: str,
                          week: int, season: int) -> pd.DataFrame:
    """Fresh candidate picks for this week. Returns an empty frame (not an
    exception) if there's simply no usable player context — the caller
    decides what an empty result means for the tabs it writes.
    """
    if player_ctx.empty:
        print("   ⚠️  no player context available — skipping pick generation")
        return pd.DataFrame()

    allowed_metrics = sorted(player_ctx["metric"].unique().tolist())
    prompt = build_prompt(week, season, games_str,
                          player_ctx.to_string(index=False), allowed_metrics)

    consensus_lists = []
    if gemini_api_key:
        from google import genai
        client = genai.Client(api_key=gemini_api_key)
        for i, temp in enumerate(CONSENSUS_TEMPS, start=1):
            print(f"🤖 Calling Gemini ({gemini_model}) run {i}/{len(CONSENSUS_TEMPS)} (temp={temp:.2f})...")
            picks = call_gemini(client, gemini_model, prompt, temp)
            if picks:
                consensus_lists.append(picks)
    else:
        print("   ⚠️  no Gemini API key — skipping AI passes, deterministic fallback only")

    merged = build_consensus_pick_pool(consensus_lists) if consensus_lists else []
    validated = validate_and_price_picks(merged, player_ctx)
    print(f"🤝 Consensus + validation: {len(validated)} usable pick(s) from {len(merged)} candidate(s)")

    if gemini_api_key and len(validated) < MIN_WEEKLY_PICKS:
        print(f"⚠️  only {len(validated)} validated pick(s); requesting one recovery pass...")
        recovery_prompt = build_recovery_prompt(prompt, len(validated))
        recovery_picks = call_gemini(client, gemini_model, recovery_prompt, RECOVERY_TEMP)
        if recovery_picks:
            consensus_lists.append(recovery_picks)
            merged = build_consensus_pick_pool(consensus_lists)
            validated = validate_and_price_picks(merged, player_ctx)
            print(f"   ↳ recovery merge: {len(validated)} usable pick(s)")

    validated = apply_smash_cap(validated).head(GEMINI_TARGET_PICKS)

    exclude_keys = {
        (_norm_name(p), t, l) for p, t, l in
        zip(validated.get("player", []), validated.get("prop_type", []), validated.get("lean", []))
    }
    still_needed = MIN_WEEKLY_PICKS - len(validated)
    if still_needed > 0:
        fallback = build_deterministic_fallback(player_ctx, exclude_keys, still_needed)
        if not fallback.empty:
            print(f"   ➕ {len(fallback)} deterministic fallback pick(s) added to reach the floor")
            validated = pd.concat([validated, fallback], ignore_index=True)

    if validated.empty:
        return validated

    validated["rank"] = range(1, len(validated) + 1)
    validated["game"] = validated["game"].fillna("")
    return validated.reset_index(drop=True)


# ============================================================================
# RUN_NUMBER + Picks_Current / Daily_Picks ASSEMBLY
# ============================================================================

PICK_OUTPUT_COLUMNS = [
    "DATE", "SEASON", "WEEK", "RUN_NUMBER", "RUN_TIME", "rank", "game",
    "player", "player_id", "team", "opponent", "prop_type", "line", "lean",
    "confidence", "rationale", "injury_context", "SELECTION_METHOD",
    "PICK_BOOK", "PICK_ODDS", "IMPLIED_PROBABILITY", "MODEL_HIT_RATE",
    "MODEL_EV_PCT", "MODEL_EDGE_SCORE", "CONSENSUS_COUNT", "CONSENSUS_RUNS",
    "CONSENSUS_TAG", "CLV_OPEN_LINE", "CLV_LATEST_LINE", "CLV_DELTA",
    "CLV_LAST_UPDATE", "RESULT", "ACTUAL_STAT", "HIT", "REALIZED_PROFIT",
    "ACTUAL_ROI_PER_PICK", "LAST_UPDATED",
]


def _pick_key(row) -> tuple:
    return (_norm_name(row.get("player")), str(row.get("prop_type", "")).upper(),
            str(row.get("lean", "")).upper())


def assemble_pick_tabs(fresh_picks: pd.DataFrame, prior_daily: pd.DataFrame,
                       week: int, season: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Stamp DATE/RUN_NUMBER, dedup against today's existing Daily_Picks rows,
    and return (Picks_Current, Daily_Picks-rows-to-append).

    RUN_NUMBER logic is unchanged from MLB: max existing RUN_NUMBER for
    today's DATE + 1. This works for NFL's Thu/Sun/Mon cadence without
    modification because each gameday is still its own distinct calendar date
    — the only thing that changes vs. MLB is how many days per week this
    fires, not the per-day numbering itself.
    """
    now = datetime.now(eastern)
    date_str = now.strftime("%Y-%m-%d")
    run_time = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    if fresh_picks.empty:
        return pd.DataFrame(), pd.DataFrame()

    out = fresh_picks.copy()
    out["DATE"] = date_str
    out["SEASON"] = season
    out["WEEK"] = week
    out["RUN_TIME"] = run_time
    out["RESULT"] = ""
    out["ACTUAL_STAT"] = ""
    out["HIT"] = ""
    out["REALIZED_PROFIT"] = ""
    out["ACTUAL_ROI_PER_PICK"] = ""
    out["CLV_OPEN_LINE"] = out["line"]
    out["CLV_LATEST_LINE"] = out["line"]
    out["CLV_DELTA"] = 0
    out["CLV_LAST_UPDATE"] = run_time
    out["LAST_UPDATED"] = run_time

    run_number = 1
    today_prior = pd.DataFrame()
    if not prior_daily.empty and "DATE" in prior_daily.columns:
        today_prior = prior_daily[prior_daily["DATE"].astype(str) == date_str]
        if not today_prior.empty and "RUN_NUMBER" in today_prior.columns:
            existing = pd.to_numeric(today_prior["RUN_NUMBER"], errors="coerce")
            if existing.notna().any():
                run_number = int(existing.max()) + 1
    out["RUN_NUMBER"] = run_number

    # Same-day dedup: if this exact (player, prop, lean) was already picked
    # earlier today, don't append a duplicate row to Daily_Picks history.
    seen_today = set()
    if not today_prior.empty:
        seen_today = {_pick_key(r) for _, r in today_prior.iterrows()}
    to_append = out[~out.apply(_pick_key, axis=1).isin(seen_today)].copy()

    cols = [c for c in PICK_OUTPUT_COLUMNS if c in out.columns]
    picks_current = out[cols].copy()
    daily_rows = to_append[cols].copy()
    return picks_current, daily_rows
