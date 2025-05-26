import aiohttp
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pytz
import discord

class SportsTracker:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.the-odds-api.com/v4/sports"
        self.leagues = {
            'nba': 'basketball_nba',
            'nfl': 'americanfootball_nfl',
            'mlb': 'baseball_mlb',
            'nhl': 'icehockey_nhl'
        }
        self.subscriptions = {}  # {channel_id: {'league': str, 'teams': List[str]}}
    
    def set_api_key(self, api_key: str):
        """Set the API key for sports data"""
        self.api_key = api_key
    
    async def get_upcoming_games(self, league: str, days: int = 1) -> List[Dict]:
        """Get upcoming games for a specific league"""
        if not self.api_key:
            raise ValueError("API key not set")
        
        if league not in self.leagues:
            raise ValueError(f"Unsupported league: {league}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{self.leagues[league]}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h,spreads',
                'oddsFormat': 'american'
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed: {response.status}")
                
                data = await response.json()
                return self._filter_upcoming_games(data, days)
    
    def _filter_upcoming_games(self, games: List[Dict], days: int) -> List[Dict]:
        """Filter games to only include those in the next X days"""
        now = datetime.now(pytz.UTC)
        cutoff = now + timedelta(days=days)
        
        return [
            game for game in games
            if datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')) <= cutoff
        ]
    
    async def get_live_scores(self, league: str) -> List[Dict]:
        """Get live scores for a specific league"""
        if not self.api_key:
            raise ValueError("API key not set")
        
        if league not in self.leagues:
            raise ValueError(f"Unsupported league: {league}")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{self.leagues[league]}/scores"
            params = {
                'apiKey': self.api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed: {response.status}")
                
                return await response.json()
    
    def format_game_alert(self, game: Dict) -> str:
        """Format a game alert message"""
        if game.get('scores'):
            # Live game
            home_team = game['home_team']
            away_team = game['away_team']
            home_score = game['scores'][0]['score']
            away_score = game['scores'][1]['score']
            return f"🏀 **{away_team} {away_score}** @ **{home_team} {home_score}**"
        else:
            # Upcoming game
            home_team = game['home_team']
            away_team = game['away_team']
            start_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
            return f"⏰ **{away_team}** @ **{home_team}** - {start_time.strftime('%I:%M %p ET')}"
    
    def format_odds(self, game: Dict) -> str:
        """Format betting odds for a game"""
        if 'bookmakers' not in game:
            return "No odds available"
        
        odds_text = []
        for bookmaker in game['bookmakers']:
            if bookmaker['key'] == 'draftkings':
                for market in bookmaker['markets']:
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            odds_text.append(f"{outcome['name']}: {outcome['price']}")
        
        return " | ".join(odds_text) if odds_text else "No odds available"
    
    def add_subscription(self, channel_id: int, league: str, team: Optional[str] = None):
        """Add a subscription for a channel"""
        if channel_id not in self.subscriptions:
            self.subscriptions[channel_id] = {'league': league, 'teams': []}
        
        if team and team not in self.subscriptions[channel_id]['teams']:
            self.subscriptions[channel_id]['teams'].append(team)
    
    def remove_subscription(self, channel_id: int, team: Optional[str] = None):
        """Remove a subscription for a channel"""
        if channel_id in self.subscriptions:
            if team:
                if team in self.subscriptions[channel_id]['teams']:
                    self.subscriptions[channel_id]['teams'].remove(team)
                if not self.subscriptions[channel_id]['teams']:
                    del self.subscriptions[channel_id]
            else:
                del self.subscriptions[channel_id]
    
    def get_subscriptions(self, channel_id: Optional[int] = None) -> Dict:
        """Get subscriptions for a channel or all subscriptions"""
        if channel_id:
            return self.subscriptions.get(channel_id, {})
        return self.subscriptions
    
    def is_subscribed(self, channel_id: int, team: str) -> bool:
        """Check if a channel is subscribed to a team"""
        if channel_id in self.subscriptions:
            return team in self.subscriptions[channel_id]['teams']
        return False
    
    def get_subscribed_channels(self, team: str) -> List[int]:
        """Get all channels subscribed to a team"""
        return [
            channel_id for channel_id, sub in self.subscriptions.items()
            if team in sub['teams']
        ]
    
    def get_team_games(self, team: str, games: List[Dict]) -> List[Dict]:
        """Filter games to only include those for a specific team"""
        return [
            game for game in games
            if team.lower() in [game['home_team'].lower(), game['away_team'].lower()]
        ]
    
    async def check_upcoming_games(self, channel: discord.TextChannel):
        """Check for upcoming games for subscribed teams"""
        if channel.id not in self.subscriptions:
            return
        
        sub = self.subscriptions[channel.id]
        try:
            games = await self.get_upcoming_games(sub['league'], days=1)
            team_games = self.get_team_games(sub['teams'], games)
            
            if team_games:
                for game in team_games:
                    alert = self.format_game_alert(game)
                    odds = self.format_odds(game)
                    await channel.send(embed=discord.Embed(
                        title="Upcoming Game Alert",
                        description=f"{alert}\n{odds}",
                        color=discord.Color.blue()
                    ))
        except Exception as e:
            print(f"Error checking upcoming games: {str(e)}")
    
    async def check_live_scores(self, channel: discord.TextChannel):
        """Check live scores for subscribed teams"""
        if channel.id not in self.subscriptions:
            return
        
        sub = self.subscriptions[channel.id]
        try:
            games = await self.get_live_scores(sub['league'])
            team_games = self.get_team_games(sub['teams'], games)
            
            if team_games:
                for game in team_games:
                    alert = self.format_game_alert(game)
                    await channel.send(embed=discord.Embed(
                        title="Live Score Update",
                        description=alert,
                        color=discord.Color.green()
                    ))
        except Exception as e:
            print(f"Error checking live scores: {str(e)}") 