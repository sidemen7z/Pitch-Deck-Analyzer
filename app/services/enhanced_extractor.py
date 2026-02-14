"""
Enhanced Information Extractor - Phase 5: Field-Level Structured Extraction
Section-specific prompts with confidence scoring and traceability
"""
from typing import Dict, Any, List
from app.services.llm_client import llm_client
from app.utils.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)


class EnhancedInformationExtractor:
    """Production-grade field-level extractor with confidence and traceability"""
    
    EXTRACTION_PROMPT = """
Extract structured investment information from this pitch deck.

Slides Content:
{content}

Section Map:
{section_map}

Extract the following with EXACT field names and include source tracking:

{{
  "company": {{
    "name": "string or null",
    "founding_date": "YYYY-MM-DD or null",
    "location": "string or null",
    "industry": "string or null",
    "mission": "string or null"
  }},
  "market": {{
    "TAM": {{"value": number, "unit": "USD/users", "confidence": 0-1, "source_slide": number}},
    "SAM": {{"value": number, "unit": "USD/users", "confidence": 0-1, "source_slide": number}},
    "SOM": {{"value": number, "unit": "USD/users", "confidence": 0-1, "source_slide": number}},
    "CAGR": {{"value": number, "unit": "percent", "confidence": 0-1, "source_slide": number}},
    "target_customer": "string or null"
  }},
  "traction": {{
    "revenue": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "ARR": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "MRR": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "users": {{"value": number, "confidence": 0-1, "source_slide": number}},
    "growth_rate": {{"value": number, "unit": "percent", "period": "monthly/yearly", "confidence": 0-1, "source_slide": number}},
    "key_milestones": ["string"]
  }},
  "financials": {{
    "burn_rate": {{"value": number, "currency": "USD", "period": "monthly", "confidence": 0-1, "source_slide": number}},
    "runway_months": {{"value": number, "confidence": 0-1, "source_slide": number}},
    "EBITDA": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "gross_margin": {{"value": number, "unit": "percent", "confidence": 0-1, "source_slide": number}}
  }},
  "funding": {{
    "ask_amount": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "valuation": {{"value": number, "currency": "USD", "type": "pre/post", "confidence": 0-1, "source_slide": number}},
    "previous_funding": {{"value": number, "currency": "USD", "confidence": 0-1, "source_slide": number}},
    "use_of_funds": ["string"]
  }},
  "team": [
    {{
      "name": "string",
      "title": "string",
      "experience": "string",
      "linkedin": "url or null",
      "confidence": 0-1,
      "source_slide": number
    }}
  ],
  "business_model": {{
    "revenue_streams": ["string"],
    "pricing_model": "string or null",
    "customer_acquisition_cost": {{"value": number, "currency": "USD", "confidence": 0-1}},
    "lifetime_value": {{"value": number, "currency": "USD", "confidence": 0-1}}
  }},
  "competition": {{
    "competitors": ["string"],
    "competitive_advantages": ["string"],
    "moat": "string or null"
  }}
}}

IMPORTANT:
- Use null for missing data
- Extract numbers without currency symbols in the value field
- Confidence should reflect extraction certainty (0.0 to 1.0)
- source_slide must be the actual slide number where data was found
- For arrays, include all items found
"""
    
    @staticmethod
    async def extract_structured_data(
        parsed_doc: Dict[str, Any],
        classified_doc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract field-level structured data with confidence and traceability"""
        try:
            # Prepare content with section context
            content = ""
            for slide in parsed_doc["slides"]:
                content += f"\n=== Slide {slide['slide_no']} ===\n"
                content += slide.get("raw_text", "")
                content += "\n"
            
            # Prepare section map summary
            section_map_str = ""
            for category, slides in classified_doc.get("section_map", {}).items():
                if slides:
                    section_map_str += f"{category}: slides {slides}\n"
            
            # Call Gemini for extraction
            prompt = EnhancedInformationExtractor.EXTRACTION_PROMPT.format(
                content=content[:12000],  # Limit content
                section_map=section_map_str
            )
            
            extracted_data = await llm_client.generate_json(prompt)
            
            # Calculate overall confidence
            confidence_scores = []
            
            # Collect all confidence scores
            for section in ["market", "traction", "financials", "funding"]:
                if section in extracted_data:
                    for field, data in extracted_data[section].items():
                        if isinstance(data, dict) and "confidence" in data:
                            confidence_scores.append(data["confidence"])
            
            # Team confidence
            if "team" in extracted_data:
                for member in extracted_data["team"]:
                    if "confidence" in member:
                        confidence_scores.append(member["confidence"])
            
            overall_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0.5
            )
            
            return {
                "document_id": parsed_doc["document_id"],
                "extracted_data": extracted_data,
                "overall_confidence": overall_confidence,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "extraction_method": "gemini-2.0-flash-exp-structured"
            }
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            raise
