import unittest
import pandas as pd
from pick_quality import assess_role, quote_is_fresh
from odds_client import best_price_board
from picks import recommendation_status, build_weekly_pick_board


class QualityTests(unittest.TestCase):
    def test_freshness_boundaries(self):
        now = pd.Timestamp("2026-10-08T17:00:00Z")
        for value, expected in [("2026-10-08T15:00:00Z", True),
                                ("2026-10-08T14:59:59Z", False),
                                ("2026-10-08T17:00:01Z", False),
                                ("2026-10-08 16:00:00", False), ("", False)]:
            self.assertEqual(quote_is_fresh(value, now), expected)

    def test_stale_best_book_cannot_win_or_support_consensus(self):
        base = dict(player="Back", metric="REC", line=4.5, event_away="A",
                    event_home="B", commence_time="2026-10-09T00:15:00Z",
                    over_odds=-120, under_odds=-110, fair_over_prob=.49, fair_under_prob=.51)
        rows = pd.DataFrame([
            {**base, "book": "stale", "over_odds": -101, "last_update": "2026-10-08T12:00:00Z"},
            {**base, "book": "fresh", "last_update": "2026-10-08T16:00:00Z"},
            {**base, "book": "different-line", "line": 5.5, "last_update": "2026-10-08T16:00:00Z"}])
        result = best_price_board(rows, now=pd.Timestamp("2026-10-08T17:00:00Z"))
        line = result[result.line.eq(4.5)].iloc[0]
        self.assertEqual(line.best_over_book, "fresh")
        self.assertEqual(line.books_quoting, 1)

    def test_role_changes_and_missing_evidence(self):
        history = pd.DataFrame({"targets": [2]*10})
        current = pd.DataFrame({"week": [3, 1, 2], "targets": [8, 7, 9], "team": ["A"]*3})
        role = assess_role(history, current, "REC_YDS", "A")
        self.assertEqual(role["role_status"], "UNCERTAIN")
        self.assertEqual(role["recent_usage"], 8)
        self.assertEqual(assess_role(history, current.head(2), "REC", "A")["role_status"], "UNKNOWN")
        stable = current.assign(targets=2)
        self.assertEqual(assess_role(history, stable, "REC", "A")["role_status"], "STABLE")
        self.assertEqual(assess_role(history, stable, "REC", "A", "teammate OUT")["role_status"], "UNCERTAIN")

    def test_uncertain_role_cannot_be_promoted_by_high_ev_label(self):
        row = dict(MODEL_VERSION="nfl-2026-regular-season-v5", ROLE_STATUS="UNKNOWN",
                   SELECTION_METHOD="VALIDATED_MODEL", confidence="VALIDATED",
                   PICK_ODDS=-110, prop_type="REC", lean="UNDER")
        self.assertEqual(recommendation_status(row), "RESEARCH")
        self.assertEqual(recommendation_status({**row, "ROLE_STATUS": "STABLE"}), "PLAYABLE")

    def test_v5_prior_board_is_not_an_unverified_fallback(self):
        prior = pd.DataFrame([{"MODEL_VERSION": "nfl-2026-regular-season-v5"}])
        self.assertTrue(build_weekly_pick_board(pd.DataFrame(), prior, week=5, season=2026).empty)
