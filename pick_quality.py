"""Conservative opportunity and quote checks, not fitted win-probability models."""
import pandas as pd

MAX_QUOTE_AGE_MINUTES = 120


def quote_is_fresh(value, now=None):
    try:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp) or timestamp.tzinfo is None:
            return False
        clock = pd.Timestamp(now) if now is not None else pd.Timestamp.now(tz="UTC")
        age = (clock - timestamp).total_seconds() / 60
        return 0 <= age <= MAX_QUOTE_AGE_MINUTES
    except (TypeError, ValueError):
        return False


def assess_role(history, current, metric, team, teammate_absences=""):
    opportunity = ("targets" if metric in {"REC", "REC_YDS", "REC_TDS"}
                   else "carries" if metric in {"CARRIES", "RUSH_YDS", "RUSH_TDS"}
                   else "attempts" if metric in {"ATT", "COMP", "PASS_YDS", "PASS_TDS", "INT"}
                   else None)
    result = {"role_status": "UNKNOWN", "role_reason": "Insufficient recent usage",
              "usage_metric": opportunity or "", "recent_usage": None, "historical_usage": None}
    if opportunity is None or opportunity not in current or opportunity not in history:
        return result
    if "week" not in current:
        return result
    recent = current.sort_values([c for c in ("season", "week") if c in current]).tail(3)
    values = pd.to_numeric(recent[opportunity], errors="coerce").dropna()
    baseline = pd.to_numeric(history[opportunity], errors="coerce").dropna()
    if len(values) < 3 or len(baseline) < 3:
        return result
    old, new = float(baseline.median()), float(values.mean())
    result.update(recent_usage=round(new, 2), historical_usage=round(old, 2))
    reasons = []
    if abs(new - old) >= max(2.0, abs(old) * 0.5):
        reasons.append("Recent opportunity differs materially from historical role")
    if "team" in recent and not recent["team"].fillna("").eq(team).all():
        reasons.append("Recent team change or unknown team")
    if teammate_absences:
        reasons.append("Teammate absence creates unresolved workload uncertainty")
    result.update(role_status="UNCERTAIN" if reasons else "STABLE",
                  role_reason="; ".join(reasons) or "Recent opportunity consistent with historical role")
    return result
