"""Regression guards for the NFL pick identity and grading audit."""

import unittest
from unittest.mock import Mock, patch

import pandas as pd

from NFLGrader1 import (
    actual_value_for_team_market,
    build_schedule_result_lookup,
    pick_perf_prepare_df,
    validate_pick_schedule_context,
)
from fantasypros_client import load_nfl_consensus
from NFLEnginev1 import restore_player_prop_board
from nfl_matchups import build_team_matchup_ratings, matchup_probability_adjustment
from picks import (
    _expected_return,
    _market_anchored_probability,
    build_calibrated_model_picks,
    build_player_context,
    build_weekly_pick_board,
    assemble_pick_tabs,
    filter_picks_to_active_players,
    recommendation_status,
    pregame_publication_status,
)


class PickAuditGuardTests(unittest.TestCase):
    def test_player_prop_sheet_can_restore_no_credit_picker_board(self):
        tab = pd.DataFrame([{
            "PLAYER_NAME": "Test Back", "METRIC": "RUSH_YDS", "DK_LINE": 42.5,
            "BEST_OVER_ODDS": -110, "BEST_UNDER_ODDS": -110,
            "BEST_OVER_BOOK": "draftkings", "BEST_UNDER_BOOK": "fanduel",
            "GAME": "New England Patriots @ Seattle Seahawks",
        }])
        teams = pd.DataFrame([
            {"team_name": "New England Patriots", "team_abbr": "NE"},
            {"team_name": "Seattle Seahawks", "team_abbr": "SEA"},
        ])
        board = restore_player_prop_board(tab, teams)
        self.assertEqual(len(board), 1)
        self.assertEqual(board.iloc[0]["event_away_abbr"], "NE")
        self.assertEqual(board.iloc[0]["event_home_abbr"], "SEA")
        self.assertEqual(board.iloc[0]["best_under_book"], "fanduel")

    def test_matchup_ratings_reward_good_offense_against_weak_defense(self):
        plays = []
        for _ in range(30):
            plays.extend([
                {"posteam": "A", "defteam": "B", "rush_attempt": 1, "pass_attempt": 0,
                 "epa": 0.35, "success": 1, "season_type": "REG"},
                {"posteam": "C", "defteam": "D", "rush_attempt": 1, "pass_attempt": 0,
                 "epa": -0.35, "success": 0, "season_type": "REG"},
                {"posteam": "A", "defteam": "B", "rush_attempt": 0, "pass_attempt": 1,
                 "epa": 0.25, "success": 1, "season_type": "REG"},
                {"posteam": "C", "defteam": "D", "rush_attempt": 0, "pass_attempt": 1,
                 "epa": -0.25, "success": 0, "season_type": "REG"},
            ])
        pbp = pd.DataFrame(plays)
        ratings = build_team_matchup_ratings(pbp, pbp)
        a = ratings.set_index("team_abbr").loc["A"]
        c = ratings.set_index("team_abbr").loc["C"]
        self.assertLess(a["off_rush_rank"], c["off_rush_rank"])
        score, adjustment = matchup_probability_adjustment(
            ratings, "A", "B", "RUSH_YDS"
        )
        self.assertGreater(score, 0)
        self.assertGreater(adjustment, 0)
        self.assertLessEqual(abs(adjustment), 0.025)
        interception_score, interception_adjustment = matchup_probability_adjustment(
            ratings, "A", "B", "INT"
        )
        self.assertLess(interception_score, 0)
        self.assertLess(interception_adjustment, 0)

    def test_market_prior_shrinks_extreme_history_and_weights_current_role(self):
        historical = pd.Series([30, 30, 30])
        current = pd.Series([0, 0])
        probability, evidence = _market_anchored_probability(
            historical, current, 20, "OVER", 0.5
        )
        # Five actual observations, not nine pseudo-observations.
        self.assertAlmostEqual(probability, 15 / 29, places=4)
        self.assertEqual(evidence, 5.0)
        self.assertAlmostEqual(_expected_return(0.55, -110), 0.05, places=4)

    def test_calibrated_model_uses_real_ev_without_padding_or_high_variance_markets(self):
        context = pd.DataFrame([
            {
                "player": "Model Under", "player_id": "p1", "team": "A", "opponent": "B",
                "metric": "REC_YDS", "line": 50.5, "injury_status": "",
                "best_over_odds": -110, "best_under_odds": -110,
                "best_over_book": "book", "best_under_book": "book",
                "over_ev_pct": 0.0, "under_ev_pct": 5.0,
                "over_hit_rate": 0.5, "under_hit_rate": 0.58,
                "over_evidence_games": 24, "under_evidence_games": 24,
                "over_market_probability": 0.5, "under_market_probability": 0.5,
                "current_games": 2,
            },
            {
                "player": "Plus Price", "player_id": "p2", "team": "A", "opponent": "B",
                "metric": "RUSH_YDS", "line": 50.5, "injury_status": "",
                "best_over_odds": 120, "best_under_odds": -110,
                "best_over_book": "book", "best_under_book": "book",
                "over_ev_pct": 12.0, "under_ev_pct": 0.0,
                "over_hit_rate": 0.58, "under_hit_rate": 0.5,
                "over_evidence_games": 24, "under_evidence_games": 24,
                "over_market_probability": 0.5, "under_market_probability": 0.5,
                "current_games": 2,
            },
            {
                "player": "TD Candidate", "player_id": "p3", "team": "A", "opponent": "B",
                "metric": "ANY_TD", "line": 0.5, "injury_status": "",
                "best_over_odds": -110, "best_under_odds": -110,
                "best_over_book": "book", "best_under_book": "book",
                "over_ev_pct": 12.0, "under_ev_pct": 0.0,
                "over_hit_rate": 0.58, "under_hit_rate": 0.5,
                "over_evidence_games": 24, "under_evidence_games": 24,
                "over_market_probability": 0.5, "under_market_probability": 0.5,
                "current_games": 2,
            },
        ])
        picks = build_calibrated_model_picks(context, max_picks=10)
        self.assertEqual(picks["player"].tolist(), ["Model Under"])
        self.assertEqual(picks.iloc[0]["confidence"], "STRONG")
        self.assertEqual(picks.iloc[0]["SELECTION_METHOD"], "VALIDATED_MODEL")

    def test_week3_publication_guardrails(self):
        base = {
            "SELECTION_METHOD": "GEMINI", "confidence": "STRONG",
            "CONSENSUS_COUNT": 3, "PICK_ODDS": -110, "prop_type": "REC_YDS",
            "lean": "UNDER",
        }
        self.assertEqual(recommendation_status(base), "PLAYABLE")

        two_of_three = {**base, "CONSENSUS_COUNT": 2}
        self.assertEqual(recommendation_status(two_of_three), "RESEARCH")

        plus_money = {**base, "PICK_ODDS": 105}
        self.assertEqual(recommendation_status(plus_money), "RESEARCH")

        anytime_td = {**base, "prop_type": "ANY_TD"}
        self.assertEqual(recommendation_status(anytime_td), "RESEARCH")

        strong_over = {**base, "lean": "OVER"}
        self.assertEqual(recommendation_status(strong_over), "RESEARCH")
        self.assertEqual(recommendation_status({**strong_over, "confidence": "SMASH"}), "PLAYABLE")

    def test_validated_model_still_obeys_price_market_and_over_gates(self):
        validated = {
            "SELECTION_METHOD": "VALIDATED_MODEL", "confidence": "VALIDATED",
            "CONSENSUS_COUNT": 1, "PICK_ODDS": -125, "prop_type": "RUSH_YDS",
            "lean": "OVER",
        }
        self.assertEqual(recommendation_status(validated), "PLAYABLE")
        self.assertEqual(recommendation_status({**validated, "PICK_ODDS": 110}), "RESEARCH")
        self.assertEqual(recommendation_status({**validated, "prop_type": "ANY_TD"}), "RESEARCH")
        self.assertEqual(recommendation_status({**validated, "injury_context": "QUESTIONABLE"}), "RESEARCH")

    def test_weekly_board_reclassifies_prior_rows_under_current_policy(self):
        prior = pd.DataFrame([{
            "SEASON": 2026, "WEEK": 3, "GAME_DATE": "2026-09-27",
            "game": "A @ B", "player": "Prior Pick", "player_id": "p1",
            "prop_type": "REC_YDS", "line": 50.5, "lean": "OVER",
            "SELECTION_METHOD": "GEMINI", "confidence": "STRONG",
            "CONSENSUS_COUNT": 2, "PICK_ODDS": 105, "rank": 1,
            "RECOMMENDATION_STATUS": "PLAYABLE", "CALIBRATION_SCORE": 999,
        }])
        board = build_weekly_pick_board(pd.DataFrame(), prior, week=3, season=2026)
        self.assertEqual(board.iloc[0]["RECOMMENDATION_STATUS"], "RESEARCH")
        self.assertLess(board.iloc[0]["CALIBRATION_SCORE"], 100)

    def test_new_model_version_is_a_new_auditable_decision(self):
        pick = pd.DataFrame([{
            "rank": 1, "player": "Versioned Pick", "player_id": "p1",
            "team": "A", "opponent": "B", "game": "A @ B",
            "GAME_DATE": "2026-09-27", "GAME_TIME": "13:00",
            "prop_type": "REC_YDS", "line": 50.5, "lean": "UNDER",
            "confidence": "VALIDATED", "PICK_ODDS": -110,
            "MODEL_VERSION": "nfl-2026-regular-season-v2",
        }])
        legacy = pick.copy()
        legacy["MODEL_VERSION"] = "nfl-2026-regular-season-v1"
        legacy["DATE"] = "2026-09-20"
        legacy["RUN_NUMBER"] = 1
        _, appended = assemble_pick_tabs(
            pick, legacy, week=3, season=2026,
            model_version="nfl-2026-regular-season-v2",
            now=pd.Timestamp("2026-09-26 12:00", tz="US/Eastern"),
        )
        self.assertEqual(len(appended), 1)

    def test_live_event_requires_current_team_and_derives_opponent(self):
        logs = pd.DataFrame([
            {"player_display_name": "Test Back", "player_id": "p1", "week": 1,
             "team": "OLD", "opponent_team": "A", "position": "RB", "rushing_yards": 20},
            {"player_display_name": "Test Back", "player_id": "p1", "week": 2,
             "team": "OLD", "opponent_team": "B", "position": "RB", "rushing_yards": 30},
            {"player_display_name": "Test Back", "player_id": "p1", "week": 3,
             "team": "OLD", "opponent_team": "C", "position": "RB", "rushing_yards": 40},
        ])
        props = pd.DataFrame([{
            "player": "Test Back", "metric": "RUSH_YDS", "line": 25,
            "best_over_odds": -110, "best_under_odds": -110,
            "event_away_abbr": "NEW", "event_home_abbr": "OPP",
            "commence_time": "2026-09-20T17:00:00Z",
        }])
        projections = pd.DataFrame([{
            "player_id": "p1", "team_now": "NEW", "position": "RB",
            "proj_ppr": 10, "vorp": 1, "confidence": "", "ecr": 1,
        }])
        base_context = build_player_context(
            props, logs, projections, pd.DataFrame(), eligible_player_ids={"p1"}
        )
        matchup_ratings = pd.DataFrame([
            {"team_abbr": "NEW", "off_rush_score": 1.0, "def_rush_ease_score": 0.0},
            {"team_abbr": "OPP", "off_rush_score": 0.0, "def_rush_ease_score": 1.5},
        ])
        context = build_player_context(
            props, logs, projections, pd.DataFrame(), eligible_player_ids={"p1"},
            current_game_logs=logs.head(2), team_matchups=matchup_ratings,
        )
        self.assertEqual(len(context), 1)
        self.assertEqual(context.iloc[0]["team"], "NEW")
        self.assertEqual(context.iloc[0]["opponent"], "OPP")
        self.assertEqual(context.iloc[0]["current_games"], 2)
        self.assertGreater(context.iloc[0]["matchup_score"], 0)
        self.assertEqual(context.iloc[0]["matchup_probability_adjustment"], 0)

        projections.loc[0, "team_now"] = "NOPE"
        rejected = build_player_context(props, logs, projections, pd.DataFrame(), eligible_player_ids={"p1"})
        self.assertTrue(rejected.empty)

    def test_context_reports_when_live_season_history_is_below_floor(self):
        logs = pd.DataFrame([
            {"player_display_name": "Two Game Player", "player_id": "p1", "week": 1,
             "position": "RB", "rushing_yards": 20},
            {"player_display_name": "Two Game Player", "player_id": "p1", "week": 2,
             "position": "RB", "rushing_yards": 30},
        ])
        props = pd.DataFrame([{
            "player": "Two Game Player", "metric": "RUSH_YDS", "line": 25,
            "best_over_odds": -110, "best_under_odds": -110,
        }])
        context = build_player_context(
            props, logs, pd.DataFrame(), pd.DataFrame(), eligible_player_ids={"p1"}
        )
        self.assertTrue(context.empty)
        self.assertEqual(context.attrs["excluded_insufficient_history_props"], 1)

    def test_persistent_board_rejects_active_player_with_stale_team(self):
        board = pd.DataFrame([
            {"player": "Old Team", "player_id": "p1", "team": "OLD", "prop_type": "REC"},
            {"player": "New Team", "player_id": "p2", "team": "NEW", "prop_type": "REC"},
        ])
        filtered = filter_picks_to_active_players(
            board, {"p1", "p2"}, {"old team", "new team"}, {"p1": "NEW", "p2": "NEW"}
        )
        self.assertEqual(filtered["player"].tolist(), ["New Team"])

    def test_legacy_team_market_and_tied_moneyline_are_safe(self):
        schedule = pd.DataFrame([{
            "season": 2026, "week": 1, "away_team": "DAL", "home_team": "PHI",
            "gameday": "2026-09-09", "away_score": 10, "home_score": 10,
        }])
        lookup = build_schedule_result_lookup(schedule)
        legacy = pd.Series({
            "SEASON": 2026, "WEEK": 1, "team": "DAL", "opponent": "NYG",
            "game": "DAL @ NYG", "GAME_DATE": "2026-09-01", "prop_type": "MONEYLINE",
        })
        self.assertEqual(validate_pick_schedule_context(legacy, lookup), (True, ""))
        result = actual_value_for_team_market(pd.Series({"prop_type": "MONEYLINE", "team": "DAL"}), schedule.iloc[0])
        self.assertEqual(result, 0.5)

    def test_performance_keeps_repriced_or_reclassified_decisions(self):
        rows = pd.DataFrame([
            {"HIT": "YES", "SEASON": 2026, "WEEK": 1, "GAME_DATE": "2026-09-09",
             "player_id": "p1", "prop_type": "REC", "lean": "OVER", "line": 4.5,
             "SELECTION_METHOD": "GEMINI", "DATE": "2026-09-08", "RUN_TIME": "2026-09-08 09:00:00", "RUN_NUMBER": 1},
            {"HIT": "NO", "SEASON": 2026, "WEEK": 1, "GAME_DATE": "2026-09-09",
             "player_id": "p1", "prop_type": "REC", "lean": "OVER", "line": 5.5,
             "SELECTION_METHOD": "GEMINI", "DATE": "2026-09-08", "RUN_TIME": "2026-09-08 10:00:00", "RUN_NUMBER": 2},
            {"HIT": "NO", "SEASON": 2026, "WEEK": 1, "GAME_DATE": "2026-09-09",
             "player_id": "p1", "prop_type": "REC", "lean": "OVER", "line": 5.5,
             "SELECTION_METHOD": "VALIDATED_MODEL", "DATE": "2026-09-08", "RUN_TIME": "2026-09-08 11:00:00", "RUN_NUMBER": 3},
        ])
        rows["GAME_TIME"] = "20:20"
        result = pick_perf_prepare_df(rows)
        self.assertEqual(len(result), 3)
        self.assertEqual(int(result["first_decision"].sum()), 2)

    def test_publication_fails_closed_at_kickoff_and_unknown_time(self):
        base = {"player": "Test", "player_id": "p1", "rank": 1,
                "prop_type": "REC", "line": 4.5, "lean": "UNDER",
                "PICK_ODDS": -110, "confidence": "VALIDATED",
                "GAME_DATE": "2026-10-08", "GAME_TIME": "20:15"}
        for moment, expected in [("20:14:59", 1), ("20:15:00", 0), ("20:16:00", 0)]:
            snapshot, ledger = assemble_pick_tabs(
                pd.DataFrame([base]), pd.DataFrame(), 5, 2026,
                now=pd.Timestamp(f"2026-10-08 {moment}", tz="US/Eastern"))
            self.assertEqual(len(snapshot), expected)
            self.assertEqual(len(ledger), expected)
        snapshot, ledger = assemble_pick_tabs(
            pd.DataFrame([{**base, "GAME_TIME": ""}]), pd.DataFrame(), 5, 2026,
            now=pd.Timestamp("2026-10-08 12:00", tz="US/Eastern"))
        self.assertTrue(snapshot.empty and ledger.empty)

    def test_performance_excludes_late_and_unknown_without_mutation(self):
        base = {"HIT": "YES", "SEASON": 2026, "WEEK": 4,
                "GAME_DATE": "2026-10-04", "GAME_TIME": "1:00 PM",
                "DATE": "2026-10-04", "player_id": "p1", "prop_type": "REC",
                "line": 4.5, "lean": "UNDER", "RUN_NUMBER": 1}
        rows = pd.DataFrame([
            {**base, "RUN_TIME": "2026-10-04 12:59:59 EDT"},
            {**base, "RUN_TIME": "2026-10-04 13:00:00 EDT", "line": 5.5},
            {**base, "RUN_TIME": "2026-10-04 12:00:00 EDT", "GAME_TIME": ""},
            {**base, "RUN_TIME": ""},
        ])
        original = rows.copy(deep=True)
        self.assertEqual(pregame_publication_status(rows).tolist(),
                         ["PREGAME", "POST_KICKOFF", "UNKNOWN_KICKOFF", "UNKNOWN_PUBLICATION"])
        self.assertEqual(len(pick_perf_prepare_df(rows)), 1)
        pd.testing.assert_frame_equal(rows, original)

    def test_fantasypros_fetches_each_supported_position_from_public_endpoint(self):
        def response_for(position):
            response = Mock()
            response.raise_for_status.return_value = None
            response.json.return_value = {
                "last_updated": "2026-09-16",
                "players": [{
                    "player_id": position, "player_name": f"Test {position}",
                    "player_position_id": position, "rank_ecr": 4, "rank_std": 1.2,
                    "rank_min": 2, "rank_max": 7,
                }],
            }
            return response

        with patch("fantasypros_client.requests.get", side_effect=[
            response_for("QB"), response_for("RB"), response_for("WR"), response_for("TE"),
        ]) as get:
            result = load_nfl_consensus(2026, "underdog", "test-key")
        self.assertEqual(len(result), 4)
        self.assertEqual(result["pos"].tolist(), ["QB", "RB", "WR", "TE"])
        self.assertEqual(get.call_count, 4)
        for call, position in zip(get.call_args_list, ["QB", "RB", "WR", "TE"]):
            self.assertEqual(call.args[0],
                             "https://api.fantasypros.com/public/v2/json/nfl/2026/consensus-rankings")
            self.assertEqual(call.kwargs["params"], {"position": position, "scoring": "HALF"})
            self.assertEqual(call.kwargs["headers"], {"x-api-key": "test-key"})


if __name__ == "__main__":
    unittest.main()
