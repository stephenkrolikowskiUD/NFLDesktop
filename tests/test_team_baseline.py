import unittest
import pandas as pd
from team_baseline import forecast_margin


class TeamBaselineTests(unittest.TestCase):
    def test_target_and_future_results_cannot_change_forecast(self):
        history=[dict(gameday=str(d.date()),home_team='A',away_team='B',home_score=21,away_score=17)
                 for d in pd.date_range('2025-01-01',periods=40)]
        future=dict(gameday='2026-10-25',home_team='A',away_team='B',home_score=100,away_score=0)
        a=forecast_margin(pd.DataFrame(history),'A','B','2026-10-25')
        b=forecast_margin(pd.DataFrame(history+[future]),'A','B','2026-10-25')
        self.assertEqual(a,b)
        self.assertGreater(a['home_margin'],0)
        self.assertEqual(forecast_margin(pd.DataFrame(history),'C','B','2026-10-25')['status'],'INSUFFICIENT_HISTORY')

if __name__=='__main__': unittest.main()
