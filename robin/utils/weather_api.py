import aiohttp
from typing import Dict
import os
from dotenv import load_dotenv

class WeatherAPI:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable not set")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    async def get_weather(self, location: str) -> Dict:
        """Get current weather for a location"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "imperial"
            }
            async with session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "temp": round(data["main"]["temp"]),
                    "description": data["weather"][0]["description"]
                } 