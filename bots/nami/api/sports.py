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
    resp = requests.get(url)
    if resp.status_code != 200:
        return None, "Failed to fetch scores."
    data = resp.json()
    return data.get('events', []), None
