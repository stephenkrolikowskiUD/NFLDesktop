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
