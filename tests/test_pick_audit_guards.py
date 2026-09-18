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
from picks import build_player_context, filter_picks_to_active_players


class PickAuditGuardTests(unittest.TestCase):
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
        context = build_player_context(props, logs, projections, pd.DataFrame(), eligible_player_ids={"p1"})
        self.assertEqual(len(context), 1)
        self.assertEqual(context.iloc[0]["team"], "NEW")
        self.assertEqual(context.iloc[0]["opponent"], "OPP")

        projections.loc[0, "team_now"] = "NOPE"
        rejected = build_player_context(props, logs, projections, pd.DataFrame(), eligible_player_ids={"p1"})
        self.assertTrue(rejected.empty)

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
        self.assertEqual(len(pick_perf_prepare_df(rows)), 3)

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
