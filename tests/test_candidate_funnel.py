"""End-to-end regressions for the October 12 cross-sport audit findings."""
import unittest
import pandas as pd

from picks import (_active_injury_reports, build_player_context,
                   build_calibrated_model_picks, assemble_pick_tabs,
                   build_weekly_pick_board, recommendation_status)


VERSION = "nfl-2026-regular-season-v7"


def candidate(**changes):
    stamp = pd.Timestamp.now(tz="UTC").isoformat()
    row = dict(player="Audit Player", player_id="p1", team="A", opponent="B",
               metric="REC", line=4.5, injury_status="", injury_data_status="CURRENT_WEEK",
               role_status="STABLE", best_over_odds=-110, best_under_odds=-110,
               best_over_book="one", best_under_book="two", over_ev_pct=-10,
               under_ev_pct=10, over_hit_rate=.4, under_hit_rate=.6,
               over_evidence_games=24, under_evidence_games=24,
               over_market_probability=.5, under_market_probability=.5,
               current_games=4, books_quoting=2, best_over_last_update=stamp,
               best_under_last_update=stamp, support_last_update=stamp)
    return {**row, **changes}


class CandidateFunnelTests(unittest.TestCase):
    def test_injuries_never_fall_back_to_wrong_week_or_season(self):
        reports = pd.DataFrame([dict(season=2025, week=5, gsis_id="old", report_status="OUT"),
                                dict(season=2026, week=4, gsis_id="prior", report_status="OUT")])
        self.assertTrue(_active_injury_reports(reports, 5, 2026).empty)
        self.assertTrue(_active_injury_reports(reports.drop(columns="week"), 5, 2026).empty)
        row = dict(MODEL_VERSION=VERSION, ROLE_STATUS="STABLE", INJURY_DATA_STATUS="UNKNOWN",
                   confidence="VALIDATED", SELECTION_METHOD="VALIDATED_MODEL",
                   PICK_ODDS=-110, prop_type="REC", lean="UNDER")
        self.assertEqual(recommendation_status(row), "RESEARCH")
        self.assertEqual(recommendation_status({**row,"INJURY_DATA_STATUS":"CURRENT_WEEK"}), "PLAYABLE")

    def test_latest_report_wins_regardless_of_input_order(self):
        reports = pd.DataFrame([
            dict(week=5, gsis_id="p1", report_status="OUT", date_modified="2026-10-08T12:00:00Z"),
            dict(week=5, gsis_id="p1", report_status="", date_modified="2026-10-09T12:00:00Z")])
        for rows in (reports, reports.iloc[::-1]):
            self.assertEqual(_active_injury_reports(rows,5).iloc[0]._injury_status, "")

    def test_undated_or_tied_conflicting_reports_are_unknown(self):
        reports = pd.DataFrame([dict(week=5, gsis_id="p1", report_status="OUT"),
                                dict(week=5, gsis_id="p1", report_status="")])
        for rows in (reports, reports.assign(date_modified="2026-10-09T12:00:00Z")):
            self.assertEqual(_active_injury_reports(rows,5).iloc[0]._injury_status, "UNKNOWN")

    def test_ledger_keeps_alternative_before_board_curation(self):
        rows = pd.DataFrame([candidate(role_status="UNCERTAIN",under_ev_pct=12),
                             candidate(metric="REC_YDS",under_ev_pct=10)])
        picks = build_calibrated_model_picks(rows)
        self.assertEqual(len(picks),2)
        now = pd.Timestamp.now(tz="US/Eastern")
        picks["GAME_DATE"] = (now + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        picks["GAME_TIME"] = "13:00"
        picks["MODEL_VERSION"] = VERSION
        snapshot, ledger = assemble_pick_tabs(picks,pd.DataFrame(),5,2026,model_version=VERSION,now=now)
        board = build_weekly_pick_board(snapshot,pd.DataFrame(),week=5,season=2026)
        self.assertEqual(len(ledger),2)
        self.assertEqual(board.prop_type.tolist(),["REC_YDS"])
        self.assertEqual(board.RECOMMENDATION_STATUS.tolist(),["PLAYABLE"])
        self.assertEqual(ledger.BOARD_SELECTED.sum(),1)
        self.assertTrue(ledger.loc[ledger.prop_type.eq("REC_YDS"),"BOARD_SELECTED"].iloc[0])

    def test_selector_has_no_legacy_14_pick_limit(self):
        rows = pd.DataFrame([candidate(player=f"Player {i}",player_id=f"p{i}") for i in range(20)])
        self.assertEqual(len(build_calibrated_model_picks(rows)),20)

    def test_full_context_survives_80_stale_rows_and_retains_metadata(self):
        history, current, projections, props = [], [], [], []
        now = pd.Timestamp.now(tz="UTC")
        for i in range(81):
            name, pid = f"Player {chr(65+i//26)}{chr(65+i%26)}", f"p{i}"
            for week in range(1,4):
                log = dict(player_display_name=name,player_id=pid,team="A",position="RB",
                           week=week,rushing_yards=40,carries=10)
                history.append({**log,"season":2025})
                current.append({**log,"season":2026})
            projections.append(dict(player_id=pid,team_now="A",position="RB",proj_ppr=100-i))
            stamp = now.isoformat() if i==80 else "2000-01-01T00:00:00Z"
            props.append(dict(player=name,metric="RUSH_YDS",line=25.5,best_over_odds=-110,
                best_under_odds=-110,market_over_probability=.5,market_under_probability=.5,
                best_over_book="one",best_under_book="two",event_away_abbr="A",event_home_abbr="B",
                commence_time=(now+pd.Timedelta(days=1)).isoformat(),books_quoting=2,
                best_over_last_update=stamp,best_under_last_update=stamp,support_last_update=stamp))
        ctx = build_player_context(pd.DataFrame(props),pd.DataFrame(history),pd.DataFrame(projections),
            pd.DataFrame([dict(season=2026,week=5,gsis_id="p0",report_status="",team="A")]),
            active_week=5,active_season=2026,current_game_logs=pd.DataFrame(current))
        self.assertEqual(len(ctx),81)
        self.assertEqual(set(ctx.injury_data_status),{"CURRENT_WEEK"})
        selected = build_calibrated_model_picks(ctx)
        self.assertEqual(selected.player.tolist(),["Player DC"])


if __name__ == "__main__":
    unittest.main()
