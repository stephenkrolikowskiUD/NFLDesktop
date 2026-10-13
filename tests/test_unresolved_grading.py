import unittest
from unittest.mock import Mock, patch
import pandas as pd
import NFLGrader1 as grader
from NFLGrader1 import unresolved_stat_updates, pick_perf_prepare_df


class UnresolvedGradingTests(unittest.TestCase):
    def test_real_grader_missing_log_retries_then_resolves(self):
        row = dict(HIT='', RESULT='', player='Example', player_id='p1', team='NE',
                   SEASON='2026', WEEK='5', prop_type='REC', line='2.5', lean='OVER',
                   ACTUAL_STAT='', REALIZED_PROFIT='', ACTUAL_ROI_PER_PICK='', PICK_ODDS='-110',
                   **{c:'' for c in grader.GRADE_AUDIT_COLUMNS})
        ws=Mock()
        client=Mock()
        sheet=Mock()
        sheet.worksheet.return_value=ws
        with patch.object(grader,'open_sheet_with_retry',return_value=sheet), \
             patch.object(grader,'load_sheet_grid',side_effect=lambda _: (list(row),[list(row.values())])), \
             patch('nflverse_loader.load_schedules',return_value=pd.DataFrame()), \
             patch('nflverse_loader.load_player_stats',return_value=pd.DataFrame()), \
             patch.object(grader,'build_kickoff_lookup',return_value={}), \
             patch.object(grader,'build_schedule_result_lookup',return_value={}), \
             patch.object(grader,'validate_pick_schedule_context',return_value=(True,'')), \
             patch.object(grader,'pick_is_ready',return_value=True), \
             patch.object(grader,'build_box_lookup',return_value=({}, {}, set(), {('NE',2026.,5.)})), \
             patch.object(grader,'find_actual',return_value=(None,'missing')) as find:
            grader.grade_daily_picks(client)
            cells=ws.batch_update.call_args.args[0]
            def value(field):
                address=f'{grader.col_letter(list(row).index(field))}2'
                return next(c['values'][0][0] for c in cells if c['range']==address)
            self.assertEqual(value('RESULT'),'UNRESOLVED_DATA')
            self.assertEqual(value('HIT'),'')
            row['RESULT']='UNRESOLVED_DATA'
            find.return_value=(pd.Series({'receptions':3}), 'ok')
            grader.grade_daily_picks(client)
            cells=ws.batch_update.call_args.args[0]
            self.assertEqual(value('HIT'),'YES')
            self.assertEqual(value('GRADE_AUDIT_STATUS'),'RESOLVED_FROM_GAME_LOG')

    def test_missing_evidence_never_settles_or_invents_profit(self):
        for reason in ('MISSING_PLAYER_LOG_PARTICIPATION_UNVERIFIED',
                       'TEAM_STATS_NOT_AVAILABLE', 'AMBIGUOUS_PLAYER_IDENTITY',
                       'MISSING_STAT_OR_LINE'):
            updates = unresolved_stat_updates(7, reason, '2026-10-13T10:17:00-04:00')
            self.assertTrue(all(row == 7 for row, _, _ in updates))
            row = {key: value for _, key, value in updates}
            self.assertEqual(row['HIT'], '')  # Existing pending selector retries it.
            self.assertEqual(row['RESULT'], 'UNRESOLVED_DATA')
            self.assertEqual(row['ACTUAL_STAT'], '')
            self.assertEqual(row['REALIZED_PROFIT'], '')
            self.assertEqual(row['GRADE_AUDIT_STATUS'], reason)
            self.assertTrue(pick_perf_prepare_df(pd.DataFrame([row])).empty)


if __name__ == '__main__':
    unittest.main()
