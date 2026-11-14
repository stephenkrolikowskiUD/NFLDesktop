"""Publication evidence, independent of prediction rules and user impressions."""
import hashlib
import pandas as pd


def publication_rows(boards, published_at):
    rows = []
    for surface, frame in boards.items():
        for _, source in frame.iterrows():
            row = source.to_dict()
            identity = '|'.join(str(row.get(k, '')) for k in
                                ('SEASON', 'WEEK', 'GAME_DATE', 'player_id', 'player',
                                 'prop_type', 'lean', 'line', 'MODEL_VERSION', 'CALCULATION_POLICY'))
            row.update(PUBLICATION_STATUS='PUBLISHED', PUBLICATION_SURFACE=surface,
                       PUBLICATION_AT=published_at, RUN_TIME=published_at,
                       PUBLICATION_ID=hashlib.sha256(
                           f'{surface}|{published_at}|{identity}'.encode()).hexdigest(),
                       PUBLICATION_POLICY='first-public-thesis-v1')
            # A carried board row must be graded at this publication's price.
            for field in ('HIT', 'RESULT', 'ACTUAL_STAT', 'REALIZED_PROFIT', 'ACTUAL_ROI_PER_PICK'):
                row[field] = ''
            rows.append(row)
    return pd.DataFrame(rows)


def public_recommendations(frame):
    """Unknown old exposure and research are never inferred to be public picks."""
    get = lambda col: frame.get(col, pd.Series('', index=frame.index)).fillna('').astype(str)
    return frame.loc[get('PUBLICATION_STATUS').eq('PUBLISHED') &
                     get('RECOMMENDATION_STATUS').eq('PLAYABLE') &
                     get('PUBLICATION_AT').ne('')].copy()


def comparison_report(frame):
    from comparison_reporting import report
    from picks import _parse_pick_kickoffs
    rows = []
    starts = _parse_pick_kickoffs(
        frame.get("GAME_DATE", pd.Series("", index=frame.index)),
        frame.get("GAME_TIME", pd.Series("", index=frame.index)))
    for (_, source), start in zip(frame.iterrows(), starts):
        row = source.to_dict()
        row["_report_evidence"] = ("RECORDED_PUBLICATION"
            if row.get("PUBLICATION_STATUS") == "PUBLISHED"
            and row.get("RECOMMENDATION_STATUS") == "PLAYABLE" else "")
        row["_report_at"] = row.get("PUBLICATION_AT", "")
        row["_report_start"] = start.isoformat() if pd.notna(start) else ""
        row["_report_game"] = row["_report_start"]
        row["_report_player"] = str(row.get("player", "")).strip().casefold()
        row["_report_surface"] = "PUBLIC_BOARD"
        row["_report_odds"] = row.get("PICK_ODDS")
        row["_report_book"] = row.get("PICK_BOOK")
        rows.append(row)
    return report(pd.DataFrame(rows), "NFL")
