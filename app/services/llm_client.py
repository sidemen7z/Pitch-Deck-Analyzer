"""
Unified LLM Client - Supports both Gemini API and Local LLMs (Ollama)
"""
import google.generativeai as genai
import json
import os
from typing import Dict, Any, Optional
import httpx

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Unified client supporting multiple LLM backends"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini")  # gemini or ollama
        
        if self.provider == "gemini":
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Using Gemini API")
        
        elif self.provider == "ollama":
            self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            logger.info(f"Using Ollama with model: {self.ollama_model}")
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    async def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate content using configured LLM"""
        if self.provider == "gemini":
            return await self._generate_gemini(prompt, temperature)
        elif self.provider == "ollama":
            return await self._generate_ollama(prompt, temperature)
    
    async def _generate_gemini(self, prompt: str, temperature: float) -> str:
        """Generate using Gemini API"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    async def _generate_ollama(self, prompt: str, temperature: float) -> str:
        """Generate using Ollama local LLM"""
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise
    
    async def generate_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """Generate structured JSON output"""
        try:
            full_prompt = f"{prompt}\n\nRespond with valid JSON only, no additional text."
            response = await self.generate_content(full_prompt, temperature)
            
            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM: {e}")
            logger.error(f"Response was: {response[:500]}")
            raise
        except Exception as e:
            logger.error(f"LLM JSON generation error: {e}")
            raise


# Global client instance
llm_client = LLMClient()
