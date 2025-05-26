import aiohttp
from typing import List, Dict

class NewsAPI:
    def __init__(self):
        self.api_key = None  # Set this from environment variable
        self.base_url = "https://newsapi.org/v2"
    
    async def get_headlines(self) -> List[Dict]:
        """Get latest news headlines"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/top-headlines"
            params = {
                "country": "us",
                "apiKey": self.api_key
            }
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data.get("articles", []) 