from typing import List
from app.models.schemas import ParsedDocument, ClassifiedDocument, ClassifiedSection, SectionType
from app.services.gemini_client import gemini_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ContentClassifier:
    """Classify pitch deck sections using Gemini AI"""
    
    CLASSIFICATION_PROMPT = """
You are analyzing a pitch deck. Classify each page/slide into one of these categories:
- problem: Problem statement or pain points
- solution: Solution or product description
- market: Market size, opportunity, or target market
- business_model: Revenue model or business strategy
- team: Team members, founders, or advisors
- traction: Metrics, growth, or achievements
- financials: Financial projections or current financials
- competition: Competitive landscape or advantages
- ask: Funding ask or use of funds
- unclassified: Cannot determine category

Analyze this pitch deck content and classify each section:

{content}

Respond with JSON in this format:
{{
  "sections": [
    {{
      "section_type": "problem",
      "page_numbers": [1],
      "content": "brief summary",
      "confidence": 0.9
    }}
  ]
}}
"""
    
    @staticmethod
    async def classify(document: ParsedDocument) -> ClassifiedDocument:
        """Classify document sections"""
        try:
            # Prepare content for classification
            content = ""
            for page in document.pages:
                content += f"\n--- Page {page.page_number} ---\n{page.text}\n"
            
            # Call Gemini for classification
            prompt = ContentClassifier.CLASSIFICATION_PROMPT.format(content=content[:8000])
            response = await gemini_client.generate_json(prompt)
            
            # Parse response
            sections = []
            for section_data in response.get("sections", []):
                sections.append(ClassifiedSection(
                    section_type=SectionType(section_data.get("section_type", "unclassified")),
                    page_numbers=section_data.get("page_numbers", []),
                    content=section_data.get("content", ""),
                    confidence=section_data.get("confidence", 0.5)
                ))
            
            # Calculate overall confidence
            overall_confidence = sum(s.confidence for s in sections) / len(sections) if sections else 0.5
            
            return ClassifiedDocument(
                document_id=document.document_id,
                sections=sections,
                overall_confidence=overall_confidence
            )
        
        except Exception as e:
            logger.error(f"Classification error: {e}")
            # Return unclassified fallback
            return ClassifiedDocument(
                document_id=document.document_id,
                sections=[
                    ClassifiedSection(
                        section_type=SectionType.UNCLASSIFIED,
                        page_numbers=list(range(1, len(document.pages) + 1)),
                        content=document.raw_text[:500],
                        confidence=0.3
                    )
                ],
                overall_confidence=0.3
            )
