from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class SectionType(str, Enum):
    """Pitch deck section types"""
    PROBLEM = "problem"
    SOLUTION = "solution"
    MARKET = "market"
    BUSINESS_MODEL = "business_model"
    TEAM = "team"
    TRACTION = "traction"
    FINANCIALS = "financials"
    COMPETITION = "competition"
    ASK = "ask"
    UNCLASSIFIED = "unclassified"


class ProcessingStatus(str, Enum):
    """Document processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Page(BaseModel):
    """Parsed page/slide content"""
    page_number: int
    text: str
    images: List[str] = []
    layout: Optional[Dict] = None


class ParsedDocument(BaseModel):
    """Document after parsing"""
    document_id: str
    pages: List[Page]
    metadata: Dict
    raw_text: str


class ClassifiedSection(BaseModel):
    """Classified section of pitch deck"""
    section_type: SectionType
    page_numbers: List[int]
    content: str
    confidence: float = Field(ge=0.0, le=1.0)


class ClassifiedDocument(BaseModel):
    """Document after classification"""
    document_id: str
    sections: List[ClassifiedSection]
    overall_confidence: float = Field(ge=0.0, le=1.0)


class FieldConfidence(BaseModel):
    """Confidence scores for individual fields"""
    pass


class CompanyInfo(BaseModel):
    """Company information"""
    name: Optional[str] = None
    founding_date: Optional[str] = None  # ISO 8601
    location: Optional[str] = None
    industry: Optional[str] = None
    confidence: Dict[str, float] = {}


class TeamInfo(BaseModel):
    """Team member information"""
    name: str
    title: str
    background: str
    confidence: float = Field(ge=0.0, le=1.0)


class FinancialInfo(BaseModel):
    """Financial metrics"""
    revenue: Optional[float] = None
    currency: str = "USD"
    burn_rate: Optional[float] = None
    runway_months: Optional[int] = None
    funding_raised: Optional[float] = None
    confidence: Dict[str, float] = {}


class MarketInfo(BaseModel):
    """Market information"""
    market_size: Optional[float] = None
    target_customer: Optional[str] = None
    growth_rate: Optional[float] = None
    confidence: Dict[str, float] = {}


class TractionInfo(BaseModel):
    """Traction metrics"""
    user_count: Optional[int] = None
    growth_rate: Optional[float] = None
    key_milestones: List[str] = []
    confidence: Dict[str, float] = {}


class FundingAsk(BaseModel):
    """Funding request information"""
    amount: Optional[float] = None
    currency: str = "USD"
    use_of_funds: Optional[str] = None
    confidence: Dict[str, float] = {}


class ExtractedInformation(BaseModel):
    """Complete extracted information"""
    document_id: str
    company: CompanyInfo
    team: List[TeamInfo] = []
    financials: FinancialInfo
    market: MarketInfo
    traction: TractionInfo
    ask: FundingAsk
    extraction_timestamp: str


class Summary(BaseModel):
    """Executive summary"""
    executive_summary: str
    key_highlights: List[str] = []
    confidence: float = Field(ge=0.0, le=1.0)


class SectionSummary(BaseModel):
    """Section-specific summary"""
    section_type: SectionType
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class ConfidenceBreakdown(BaseModel):
    """Confidence categorization"""
    high_confidence: List[str] = []
    medium_confidence: List[str] = []
    low_confidence: List[str] = []


class ScoredInformation(ExtractedInformation):
    """Extracted information with confidence scores"""
    overall_confidence: float = Field(ge=0.0, le=1.0)
    confidence_breakdown: ConfidenceBreakdown


class JSONOutput(BaseModel):
    """Final JSON output format"""
    schema_version: str
    document_id: str
    processing_timestamp: str
    data: ExtractedInformation
    summaries: Dict
    confidence: Dict
    metadata: Dict
