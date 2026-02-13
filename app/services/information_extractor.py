from app.models.schemas import (
    ClassifiedDocument, ExtractedInformation, CompanyInfo, TeamInfo,
    FinancialInfo, MarketInfo, TractionInfo, FundingAsk
)
from app.services.gemini_client import gemini_client
from app.utils.logging import get_logger
from datetime import datetime

logger = get_logger(__name__)


class InformationExtractor:
    """Extract structured information from classified pitch deck"""
    
    EXTRACTION_PROMPT = """
Extract key investment information from this pitch deck content.

Content:
{content}

Extract the following information and respond with JSON:
{{
  "company": {{
    "name": "company name or null",
    "founding_date": "YYYY-MM-DD or null",
    "location": "location or null",
    "industry": "industry or null"
  }},
  "team": [
    {{
      "name": "person name",
      "title": "role/title",
      "background": "brief background"
    }}
  ],
  "financials": {{
    "revenue": number or null,
    "currency": "USD",
    "burn_rate": number or null,
    "runway_months": number or null,
    "funding_raised": number or null
  }},
  "market": {{
    "market_size": number or null,
    "target_customer": "description or null",
    "growth_rate": number or null
  }},
  "traction": {{
    "user_count": number or null,
    "growth_rate": number or null,
    "key_milestones": ["milestone1", "milestone2"]
  }},
  "ask": {{
    "amount": number or null,
    "currency": "USD",
    "use_of_funds": "description or null"
  }}
}}

Use null for missing information. Extract numbers without currency symbols.
"""
    
    @staticmethod
    async def extract(classified_doc: ClassifiedDocument) -> ExtractedInformation:
        """Extract structured information"""
        try:
            # Combine all section content
            content = "\n\n".join([
                f"Section: {section.section_type.value}\n{section.content}"
                for section in classified_doc.sections
            ])
            
            # Call Gemini for extraction
            prompt = InformationExtractor.EXTRACTION_PROMPT.format(content=content[:10000])
            response = await gemini_client.generate_json(prompt)
            
            # Parse company info
            company_data = response.get("company", {})
            company = CompanyInfo(
                name=company_data.get("name"),
                founding_date=company_data.get("founding_date"),
                location=company_data.get("location"),
                industry=company_data.get("industry"),
                confidence={
                    "name": 0.8 if company_data.get("name") else 0.0,
                    "founding_date": 0.7 if company_data.get("founding_date") else 0.0,
                    "location": 0.7 if company_data.get("location") else 0.0,
                    "industry": 0.8 if company_data.get("industry") else 0.0,
                }
            )
            
            # Parse team
            team = []
            for member in response.get("team", []):
                team.append(TeamInfo(
                    name=member.get("name", "Unknown"),
                    title=member.get("title", ""),
                    background=member.get("background", ""),
                    confidence=0.7
                ))
            
            # Parse financials
            financials_data = response.get("financials", {})
            financials = FinancialInfo(
                revenue=financials_data.get("revenue"),
                currency=financials_data.get("currency", "USD"),
                burn_rate=financials_data.get("burn_rate"),
                runway_months=financials_data.get("runway_months"),
                funding_raised=financials_data.get("funding_raised"),
                confidence={
                    "revenue": 0.7 if financials_data.get("revenue") else 0.0,
                    "burn_rate": 0.6 if financials_data.get("burn_rate") else 0.0,
                }
            )
            
            # Parse market
            market_data = response.get("market", {})
            market = MarketInfo(
                market_size=market_data.get("market_size"),
                target_customer=market_data.get("target_customer"),
                growth_rate=market_data.get("growth_rate"),
                confidence={
                    "market_size": 0.7 if market_data.get("market_size") else 0.0,
                }
            )
            
            # Parse traction
            traction_data = response.get("traction", {})
            traction = TractionInfo(
                user_count=traction_data.get("user_count"),
                growth_rate=traction_data.get("growth_rate"),
                key_milestones=traction_data.get("key_milestones", []),
                confidence={
                    "user_count": 0.7 if traction_data.get("user_count") else 0.0,
                }
            )
            
            # Parse funding ask
            ask_data = response.get("ask", {})
            ask = FundingAsk(
                amount=ask_data.get("amount"),
                currency=ask_data.get("currency", "USD"),
                use_of_funds=ask_data.get("use_of_funds"),
                confidence={
                    "amount": 0.8 if ask_data.get("amount") else 0.0,
                }
            )
            
            return ExtractedInformation(
                document_id=classified_doc.document_id,
                company=company,
                team=team,
                financials=financials,
                market=market,
                traction=traction,
                ask=ask,
                extraction_timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            raise
