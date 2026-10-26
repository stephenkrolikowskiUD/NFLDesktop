"""Offline margin benchmark. Not wired to live picks or a win-probability claim."""
import numpy as np
import pandas as pd


def forecast_margin(schedule, home, away, as_of, ridge=10.0):
    """Fit shrunk team strengths using completed games strictly before target day.

    Date-only input deliberately excludes every same-day game. This prevents
    final scores from the target day entering training; it is not a substitute
    for archived injury, odds or efficiency snapshots.
    """
    cutoff = pd.Timestamp(as_of).date()
    dates = pd.to_datetime(schedule['gameday'], errors='coerce').dt.date
    games = schedule.loc[dates.notna() & (dates < cutoff)].copy()
    games['home_score'] = pd.to_numeric(games.home_score, errors='coerce')
    games['away_score'] = pd.to_numeric(games.away_score, errors='coerce')
    games = games.dropna(subset=['home_score','away_score'])
    teams = sorted(set(games.home_team) | set(games.away_team))
    if home not in teams or away not in teams or len(games) < 32:
        return {'status':'INSUFFICIENT_HISTORY','training_games':len(games)}
    index = {t:i for i,t in enumerate(teams)}
    x = np.zeros((len(games),len(teams)+1))
    for i,(_,g) in enumerate(games.iterrows()):
        x[i,index[g.home_team]]=1
        x[i,index[g.away_team]]=-1
        x[i,-1]=1
    y = (games.home_score-games.away_score).to_numpy(float)
    beta = np.linalg.solve(x.T@x + ridge*np.eye(x.shape[1]),x.T@y)
    return {'status':'OFFLINE_BENCHMARK', 'training_games':len(games),
            'home_margin':float(beta[index[home]]-beta[index[away]]+beta[-1]),
            'training_through':str(max(games.gameday))}
