import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import os

load_dotenv()

class CryptoAPIError(Exception):
    """Custom exception for crypto API errors"""
    pass

class CryptoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        
    async def get_price(self, symbol: str) -> Dict:
        """Get current price for a cryptocurrency"""
        # Map common symbols to CoinGecko IDs
        symbol_map = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "doge": "dogecoin",
            "ada": "cardano",
            "dot": "polkadot",
            "ltc": "litecoin"
        }
        
        if symbol.lower() not in symbol_map:
            raise CryptoAPIError(f"Unsupported cryptocurrency symbol: {symbol}")
            
        id = symbol_map[symbol.lower()]
        url = f"{self.base_url}/simple/price"
        params = {
            "ids": id,
            "vs_currencies": "usd",
            "include_market_cap": "true",
            "include_24hr_vol": "true",
            "include_24hr_change": "true"
        }
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise CryptoAPIError("No data returned from API")
                
            return {
                "price": data[id]["usd"],
                "market_cap": data[id]["usd_market_cap"],
                "volume_24h": data[id]["usd_24h_vol"],
                "change_24h": data[id]["usd_24h_change"]
            }
            
        except requests.RequestException as e:
            raise CryptoAPIError(f"Request failed: {str(e)}")
            
    async def get_top_cryptos(self, limit: int = 10) -> List[Dict]:
        """Get top cryptocurrencies by market cap"""
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False
        }
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                raise CryptoAPIError("Invalid data format from API")
                
            return [{
                "name": item["name"],
                "symbol": item["symbol"].upper(),
                "price": item["current_price"],
                "market_cap": item["market_cap"],
                "volume_24h": item["total_volume"],
                "change_24h": item["price_change_percentage_24h"]
            } for item in data]
            
        except requests.RequestException as e:
            raise CryptoAPIError(f"Request failed: {str(e)}")
