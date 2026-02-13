import google.generativeai as genai
from typing import Dict, Any, Optional
import json

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        # Use the correct model name for the current API version
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    async def generate_content(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate content using Gemini"""
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
            logger.error(f"Failed to parse JSON from Gemini: {e}")
            raise
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {e}")
            raise


# Global client instance
gemini_client = GeminiClient()
