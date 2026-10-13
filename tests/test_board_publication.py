import unittest
import pandas as pd
from board_publication import publication_rows, public_recommendations
from NFLGrader1 import build_pick_performance


class PublicationTests(unittest.TestCase):
    def test_records_each_surface_price_and_repeat(self):
        board=pd.DataFrame([dict(player='Test',player_id='p',line=2.5,PICK_ODDS=-110,
            PICK_BOOK='one',RECOMMENDATION_STATUS='PLAYABLE',MODEL_VERSION='v7')])
        a=publication_rows({'Picks_Weekly':board,'Picks_Current':board},'2026-10-10 10:00:00 EDT')
        b=publication_rows({'Picks_Weekly':board},'2026-10-10 11:00:00 EDT')
        self.assertEqual(len(set(a.PUBLICATION_ID)|set(b.PUBLICATION_ID)),3)
        self.assertEqual(a.PICK_ODDS.tolist(),[-110,-110])
        self.assertEqual(a.HIT.tolist(),['',''])
        self.assertEqual(len(public_recommendations(a)),2)
        self.assertTrue(public_recommendations(board).empty)

    def test_public_only_and_first_price(self):
        row=dict(player='Test',player_id='p',line=2.5,PICK_ODDS=-110,PICK_BOOK='one',
            RECOMMENDATION_STATUS='PLAYABLE',MODEL_VERSION='v7',MODEL_ERA='v7',
            SELECTION_METHOD='VALIDATED_MODEL',SEASON=2026,WEEK=5,DATE='2026-10-10',
            GAME_DATE='2026-10-11',GAME_TIME='13:00',prop_type='REC',lean='OVER',
            RUN_NUMBER=1,confidence='VALIDATED')
        a=publication_rows({'Picks_Weekly':pd.DataFrame([row])},'2026-10-10 10:00:00 EDT')
        b=publication_rows({'Picks_Current':pd.DataFrame([{**row,'line':3.5,'PICK_ODDS':150}])},'2026-10-10 11:00:00 EDT')
        ledger=pd.concat([a,b],ignore_index=True)
        ledger['HIT']='YES'
        legacy=ledger.iloc[[0]].copy(); legacy['PUBLICATION_STATUS']=''
        research=ledger.iloc[[0]].copy(); research['RECOMMENDATION_STATUS']='RESEARCH'
        perf=build_pick_performance(pd.concat([ledger,legacy,research],ignore_index=True))
        overall=perf[(perf.DIMENSION_TYPE=='overall') & (perf.TIME_WINDOW=='all_time')].iloc[0]
        self.assertEqual(overall.N_PICKS,1)
        self.assertAlmostEqual(overall.ACTUAL_PROFIT_UNITS,.909,places=3)
        empty=build_pick_performance(legacy)
        self.assertTrue(empty.N_PICKS.eq(0).all())
        ledger.loc[0,'HIT']=''
        unresolved=build_pick_performance(ledger)
        self.assertTrue(unresolved.N_PICKS.eq(0).all())

if __name__=='__main__': unittest.main()
