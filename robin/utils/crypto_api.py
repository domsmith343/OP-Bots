import aiohttp
from typing import Dict

class CryptoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
    
    async def get_price(self, symbol: str) -> Dict:
        """Get current price for a cryptocurrency"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            async with session.get(url, params=params) as response:
                data = await response.json()
                return {
                    "price": data[symbol.lower()]["usd"],
                    "change_24h": data[symbol.lower()]["usd_24h_change"]
                } 