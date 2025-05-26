import aiohttp
import json
from typing import List, Dict, Any, Optional
from utils.error_handler import APIError

class OllamaAPI:
    def __init__(self, base_url: str, model: str = "llama2"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate(self, prompt: str) -> str:
        """Generate a response for a single prompt"""
        await self._ensure_session()
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            ) as response:
                if response.status != 200:
                    raise APIError(f"Ollama API returned status {response.status}")
                
                data = await response.json()
                return data.get("response", "")
                
        except Exception as e:
            raise APIError(f"Failed to generate response: {str(e)}")

    async def generate_with_history(self, history: str) -> str:
        """Generate a response with conversation history"""
        await self._ensure_session()
        
        try:
            # Format the prompt with conversation history
            prompt = f"""Previous conversation:
{history}

Please provide a helpful response to the last message, taking into account the conversation history."""

            async with self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            ) as response:
                if response.status != 200:
                    raise APIError(f"Ollama API returned status {response.status}")
                
                data = await response.json()
                return data.get("response", "")
                
        except Exception as e:
            raise APIError(f"Failed to generate response: {str(e)}")

    async def list_models(self) -> List[str]:
        """List available models"""
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    raise APIError(f"Ollama API returned status {response.status}")
                
                data = await response.json()
                return [model["name"] for model in data.get("models", [])]
                
        except Exception as e:
            raise APIError(f"Failed to list models: {str(e)}")

    async def set_model(self, model: str) -> None:
        """Set the model to use"""
        models = await self.list_models()
        if model not in models:
            raise APIError(f"Model {model} not found. Available models: {', '.join(models)}")
        self.model = model 