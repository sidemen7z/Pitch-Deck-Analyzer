"""
Investment Signals Analyzer - Phase 6: Insight Generation
Generates investment signals, red flags, and green flags
"""
from typing import Dict, Any, List
from app.services.llm_client import llm_client
from app.utils.logging import get_logger

logger = get_logger(__name__)


class InvestmentAnalyzer:
    """Generate investment insights and signals"""
    
    ANALYSIS_PROMPT = """
Analyze this startup pitch deck data and generate investment signals.

Extracted Data:
{extracted_data}

Generate a comprehensive investment analysis with:

{{
  "investment_signals": {{
    "green_flags": [
      {{"signal": "string", "reasoning": "string", "importance": "high/medium/low"}}
    ],
    "red_flags": [
      {{"signal": "string", "reasoning": "string", "severity": "high/medium/low"}}
    ],
    "yellow_flags": [
      {{"signal": "string", "reasoning": "string"}}
    ]
  }},
  "key_metrics_summary": {{
    "revenue_status": "string",
    "growth_trajectory": "string",
    "market_opportunity": "string",
    "team_strength": "string",
    "competitive_position": "string"
  }},
  "investment_recommendation": {{
    "overall_score": 0-100,
    "recommendation": "strong_pass/pass/maybe/no_pass",
    "key_strengths": ["string"],
    "key_concerns": ["string"],
    "suggested_next_steps": ["string"]
  }},
  "comparable_analysis": {{
    "similar_companies": ["string"],
    "market_positioning": "string"
  }},
  "risk_assessment": {{
    "market_risk": "high/medium/low",
    "execution_risk": "high/medium/low",
    "financial_risk": "high/medium/low",
    "competitive_risk": "high/medium/low"
  }}
}}

Be specific and data-driven in your analysis.
"""
    
    @staticmethod
    async def analyze_investment_potential(extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment signals and recommendations"""
        try:
            # Prepare extracted data summary
            data_summary = str(extracted_info.get("extracted_data", {}))[:8000]
            
            prompt = InvestmentAnalyzer.ANALYSIS_PROMPT.format(
                extracted_data=data_summary
            )
            
            analysis = await llm_client.generate_json(prompt)
            
            return {
                "document_id": extracted_info["document_id"],
                "analysis": analysis,
                "analysis_method": "gemini-2.0-investment-analysis"
            }
        
        except Exception as e:
            logger.error(f"Investment analysis error: {e}")
            return {
                "document_id": extracted_info["document_id"],
                "analysis": {
                    "investment_signals": {
                        "green_flags": [],
                        "red_flags": [],
                        "yellow_flags": []
                    },
                    "error": str(e)
                }
            }
