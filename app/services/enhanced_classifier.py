"""
Enhanced Content Classifier - Phase 4: Section Classification & Labeling
Uses Gemini 2.0 for zero-shot classification with structured output
"""
from typing import List, Dict, Any
from app.services.gemini_client import gemini_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class EnhancedContentClassifier:
    """Production-grade section classifier with 11 categories"""
    
    SECTION_CATEGORIES = [
        "company_overview",
        "problem",
        "solution",
        "market",
        "product",
        "business_model",
        "traction",
        "financials",
        "competition",
        "team",
        "funding_ask"
    ]
    
    CLASSIFICATION_PROMPT = """
You are analyzing a startup pitch deck. Classify each slide into ONE of these categories:

Categories:
1. company_overview - Company introduction, mission, vision
2. problem - Problem statement, pain points, market gap
3. solution - Solution description, value proposition
4. market - Market size (TAM/SAM/SOM), market opportunity, target market
5. product - Product features, demo, technology
6. business_model - Revenue model, pricing, go-to-market strategy
7. traction - Metrics, growth, achievements, milestones, revenue
8. financials - Financial projections, P&L, burn rate, runway
9. competition - Competitive landscape, competitive advantages
10. team - Founders, team members, advisors, experience
11. funding_ask - Funding amount, use of funds, valuation

Analyze these slides and classify each one:

{slides_content}

Respond with JSON in this EXACT format:
{{
  "section_map": {{
    "company_overview": [slide_numbers],
    "problem": [slide_numbers],
    "solution": [slide_numbers],
    "market": [slide_numbers],
    "product": [slide_numbers],
    "business_model": [slide_numbers],
    "traction": [slide_numbers],
    "financials": [slide_numbers],
    "competition": [slide_numbers],
    "team": [slide_numbers],
    "funding_ask": [slide_numbers]
  }},
  "slide_classifications": [
    {{
      "slide_no": 1,
      "category": "company_overview",
      "confidence": 0.95,
      "reasoning": "brief explanation"
    }}
  ]
}}
"""
    
    @staticmethod
    async def classify_slides(parsed_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Classify slides into sections using Gemini 2.0"""
        try:
            # Prepare slide content for classification
            slides_content = ""
            for slide in parsed_doc["slides"]:
                slides_content += f"\n--- Slide {slide['slide_no']} ---\n"
                slides_content += slide.get("raw_text", "")[:500]  # Limit per slide
                slides_content += "\n"
            
            # Call Gemini for classification
            prompt = EnhancedContentClassifier.CLASSIFICATION_PROMPT.format(
                slides_content=slides_content[:8000]  # Limit total
            )
            
            response = await gemini_client.generate_json(prompt)
            
            # Add document metadata
            response["document_id"] = parsed_doc["document_id"]
            response["total_slides"] = parsed_doc["total_slides"]
            response["extraction_method"] = "gemini-2.0-flash-exp"
            
            return response
        
        except Exception as e:
            logger.error(f"Classification error: {e}")
            # Return fallback classification
            return {
                "document_id": parsed_doc["document_id"],
                "section_map": {cat: [] for cat in EnhancedContentClassifier.SECTION_CATEGORIES},
                "slide_classifications": [],
                "error": str(e)
            }
