import aiohttp
from typing import List, Dict

class OllamaAPI:
    def __init__(self):
        self.base_url = "http://localhost:11434/api"
    
    async def list_models(self) -> List[str]:
        """Get list of available models"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/tags") as response:
                data = await response.json()
                return [model["name"] for model in data["models"]]
    
    async def generate(self, prompt: str, model: str = "llama2") -> str:
        """Generate text using specified model"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/generate",
                json={"model": model, "prompt": prompt}
            ) as response:
                data = await response.json()
                return data["response"] 