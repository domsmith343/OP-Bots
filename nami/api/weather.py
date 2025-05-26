import requests
import asyncio
from typing import Dict, Optional, List
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY environment variable is not set")

class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""
    pass

class WeatherAPI:
    def __init__(self, api_key: str = WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.session = requests.Session()
        self.session.params = {"appid": self.api_key, "units": "imperial"}

    async def get_current_weather(self, city: str) -> Dict:
        """Get current weather for a city"""
        url = f"{self.base_url}/weather"
        params = {"q": city}
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("cod") != 200:
                raise WeatherAPIError(f"API Error: {data.get('message', 'Unknown error')}")
                
            return {
                "name": data["name"],
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"].capitalize(),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "icon": data["weather"][0]["icon"]
            }
            
        except requests.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
            
    async def get_forecast(self, city: str) -> List[Dict]:
        """Get weather forecast for a city"""
        url = f"{self.base_url}/forecast"
        params = {"q": city}
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("cod") != "200":
                raise WeatherAPIError(f"API Error: {data.get('message', 'Unknown error')}")
                
            return [{
                "date": datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d %H:%M"),
                "temperature": item["main"]["temp"],
                "description": item["weather"][0]["description"].capitalize(),
                "icon": item["weather"][0]["icon"]
            } for item in data["list"][:5]]  # Return next 5 hours
            
        except requests.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
