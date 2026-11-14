import unittest
from datetime import date
import pandas as pd
from comparison_reporting import report

class ComparisonTests(unittest.TestCase):
    def row(self, **changes):
        row = dict(_report_at="2026-11-13T14:00:00Z", _report_start="2026-11-13T23:00:00Z",
                   _report_game="game1", _report_player="player1", prop_type="PTS", lean="OVER",
                   line=20.5, HIT="YES", _report_odds=-110, _report_book="book",
                   _report_evidence="RECONSTRUCTED", _report_surface="RESEARCH_FEED")
        return dict(row, **changes)

    def metrics(self, rows):
        result, audit = report(pd.DataFrame(rows), "TEST", date(2026,11,13))
        return result[(result.TIME_WINDOW=="last_30d") & (result.EVIDENCE=="ALL")], audit

    def test_first_before_outcome_and_price_changes(self):
        first = self.row(HIT="")
        later = self.row(_report_at="2026-11-13T15:00:00Z", line=18.5, MODEL_VERSION="new")
        result, audit = self.metrics([later, first])
        self.assertEqual(result.iloc[0].N_PENDING, 1)
        self.assertEqual(result.iloc[0].N_HITS, 0)
        self.assertEqual(audit.STATUS.tolist(), ["repeat selection", "selected"])

    def test_returns_push_dnp_unpriced(self):
        rows = [self.row(), self.row(_report_player="2", HIT="NO"),
                self.row(_report_player="3", HIT="PUSH"), self.row(_report_player="4", HIT="DNP"),
                self.row(_report_player="5", _report_odds="")]
        result, _ = self.metrics(rows)
        row = result.iloc[0]
        self.assertEqual(row.N_PRICED, 3)
        self.assertAlmostEqual(row.HIT_RATE, 2/3)
        self.assertAlmostEqual(row.ROI_PCT, (100/110-1)/3*100)

    def test_window_and_pregame_boundaries(self):
        rows = [self.row(_report_at="2026-10-14T14:00:00Z", _report_start="2026-10-14T23:00:00Z"),
                self.row(_report_game="2", _report_at="2026-10-15T14:00:00Z", _report_start="2026-10-15T23:00:00Z"),
                self.row(_report_game="3", _report_at="2026-11-13T23:00:00Z"),
                self.row(_report_game="4", _report_evidence="")]
        result, audit = self.metrics(rows)
        self.assertEqual(result.iloc[0].N_SELECTED, 1)
        self.assertIn("missing or late publication timing", audit.STATUS.tolist())
        self.assertIn("unverified publication", audit.STATUS.tolist())

    def test_evidence_does_not_duplicate_first_selection(self):
        result, _ = self.metrics([self.row(), self.row(_report_evidence="DIRECT", _report_at="2026-11-13T15:00:00Z")])
        self.assertEqual(result.iloc[0].N_SELECTED, 1)

    def test_empty(self):
        result, audit = report(pd.DataFrame(), "TEST", date(2026,11,13))
        self.assertIn("POLICY", result.columns)
        self.assertIn("STATUS", audit.columns)

if __name__ == "__main__":
    unittest.main()

