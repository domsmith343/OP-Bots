import requests
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from functools import lru_cache
import asyncio
from discord import Embed
import json
import logging

load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CACHE_TIMEOUT = 300  # 5 minutes in seconds

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable is not set")

class NewsAPIError(Exception):
    """Custom exception for news API errors"""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

class NewsAPI:
    def __init__(self, api_key: str = NEWS_API_KEY):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": self.api_key})
        self._last_rate_limit_error = None
        self._cache = {}

    async def _get_cached(self, url: str, params: Dict) -> Dict:
        """Internal method to handle caching and rate limiting"""
        # Create a cache key from the URL and sorted params
        cache_key = f"{url}:{json.dumps(params, sort_keys=True)}"
        
        # Check if we have a cached response
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=CACHE_TIMEOUT):
                return cached_data
        
        try:
            logger.info(f"Making request to {url} with params: {params}")
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"API Response status: {data.get('status')}")
            logger.info(f"Total results: {data.get('totalResults')}")
            
            if data["status"] != "ok":
                raise NewsAPIError(f"API Error: {data.get('message', 'Unknown error')}")
            
            # Cache the response
            self._cache[cache_key] = (data, datetime.now())
            return data
            
        except requests.RequestException as e:
            if hasattr(e.response, 'headers') and 'Retry-After' in e.response.headers:
                retry_after = int(e.response.headers['Retry-After'])
                self._last_rate_limit_error = datetime.now() + timedelta(seconds=retry_after)
                raise NewsAPIError(f"Rate limited. Please try again later.", retry_after)
            raise NewsAPIError(f"Request failed: {str(e)}")

    async def get_top_headlines(self, country: str = "us", category: str = "general", keyword: Optional[str] = None) -> Tuple[List[Dict], Optional[int]]:
        """
        Get top headlines from NewsAPI with optional keyword search
        Returns a tuple of (articles, total_results)
        """
        url = f"{self.base_url}/top-headlines"
        params = {
            "country": country,
            "category": category,
            "language": "en",
            "q": keyword if keyword else None
        }
        
        try:
            data = await self._get_cached(url, params)
            articles = data["articles"]
            total_results = data["totalResults"]
            
            logger.info(f"Found {len(articles)} articles")
            
            # Format articles into Discord embeds
            embeds = []
            for article in articles[:5]:  # Limit to top 5
                embed = Embed(
                    title=article["title"],
                    url=article["url"],
                    description=article.get("description", "No description available"),
                    timestamp=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                )
                if article.get("urlToImage"):
                    embed.set_image(url=article["urlToImage"])
                
                embed.set_author(name=article["source"]["name"])
                embeds.append(embed)
                
            return embeds, total_results
            
        except NewsAPIError as e:
            if e.retry_after:
                raise NewsAPIError(f"Rate limited. Please try again in {e.retry_after} seconds.")
            raise

    async def get_article_by_source(self, source: str, keyword: Optional[str] = None) -> Tuple[List[Dict], Optional[int]]:
        """
        Get articles from a specific source with optional keyword search
        Returns a tuple of (articles, total_results)
        """
        url = f"{self.base_url}/top-headlines"
        params = {
            "sources": source,
            "language": "en",
            "q": keyword if keyword else None
        }
        
        try:
            data = await self._get_cached(url, params)
            articles = data["articles"]
            total_results = data["totalResults"]
            
            logger.info(f"Found {len(articles)} articles from source {source}")
            
            # Format articles into Discord embeds
            embeds = []
            for article in articles[:5]:  # Limit to top 5
                embed = Embed(
                    title=article["title"],
                    url=article["url"],
                    description=article.get("description", "No description available"),
                    timestamp=datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                )
                if article.get("urlToImage"):
                    embed.set_image(url=article["urlToImage"])
                
                embed.set_author(name=article["source"]["name"])
                embeds.append(embed)
                
            return embeds, total_results
            
        except NewsAPIError as e:
            if e.retry_after:
                raise NewsAPIError(f"Rate limited. Please try again in {e.retry_after} seconds.")
            raise

    async def get_article_summary(self, article_url: str) -> str:
        """Get a summary of an article using natural language processing"""
        # TODO: Implement article summarization using NLP
        return "Article summary feature coming soon!"
        params = {
            "sources": source,
            "language": "en"
        }
        
        try:
            response = await asyncio.to_thread(self.session.get, url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] != "ok":
                raise NewsAPIError(f"API Error: {data.get('message', 'Unknown error')}")
                
            return data["articles"][:5]
            
        except requests.RequestException as e:
            raise NewsAPIError(f"Request failed: {str(e)}")
