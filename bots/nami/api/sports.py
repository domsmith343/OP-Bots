import requests

BASE_URL = "https://www.thesportsdb.com/api/v1/json/1/"

def get_upcoming_games(league_name, days=3):
    # For demo: map league_name to TheSportsDB league ID (expand as needed)
    league_ids = {
        'nba': '4387',  # NBA Basketball
        'epl': '4328',  # English Premier League
        'nfl': '4391',  # NFL
        'mlb': '4424',  # Major League Baseball
    }
    league_id = league_ids.get(league_name.lower())
    if not league_id:
        return None, f"Unknown league: {league_name}. Supported: {', '.join(league_ids.keys())}"
    url = f"{BASE_URL}eventsnextleague.php?id={league_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None, "Failed to fetch games."
    data = resp.json()
    return data.get('events', []), None

import logging

def get_live_scores(league_name):
    # TheSportsDB does not have true live scores in free tier, so fetch latest results
    league_ids = {
        'nba': '4387',
        'epl': '4328',
        'nfl': '4391',
    }
    league_id = league_ids.get(league_name.lower())
    if not league_id:
        return None, f"Unknown league: {league_name}. Supported: {', '.join(league_ids.keys())}"
    url = f"{BASE_URL}eventspastleague.php?id={league_id}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            logging.warning(f"Failed to fetch scores: status {resp.status_code}, url={url}")
            raise Exception(f"Status {resp.status_code}")
        data = resp.json()
        return data.get('events', []), None
    except Exception as e:
        logging.error(f"Error fetching scores for {league_name}: {e}")
        # Fallback demo data
        demo_events = [
            {
                'strHomeTeam': 'Demo Home',
                'strAwayTeam': 'Demo Away',
                'intHomeScore': '100',
                'intAwayScore': '98',
                'dateEvent': '2025-05-28',
            },
            {
                'strHomeTeam': 'Sample Team A',
                'strAwayTeam': 'Sample Team B',
                'intHomeScore': '110',
                'intAwayScore': '105',
                'dateEvent': '2025-05-27',
            },
        ]
        return demo_events, None

